#!/usr/bin/env python3
"""App Store Connect API client for Oneware Games.

Credentials come from the environment:
  ASC_ISSUER_ID       Issuer ID (App Store Connect -> Users and Access -> Integrations)
  ASC_KEY_ID          Key ID of the API key
  ASC_PRIVATE_KEY     Contents of the AuthKey_XXXX.p8 file
    or ASC_PRIVATE_KEY_PATH  Path to the .p8 file
  ASC_VENDOR_NUMBER   Vendor number (Payments and Financial Reports), for sales

Output is JSON (or TSV for sales) on stdout so it can be piped or saved.
Raw downloads go to data/ (gitignored).
"""

import argparse
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import jwt  # PyJWT, with cryptography for ES256

API = "https://api.appstoreconnect.apple.com"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _env(name):
    value = os.environ.get(name)
    if not value:
        sys.exit(f"error: {name} is not set (see tools/asc.py docstring)")
    return value


def _private_key():
    if os.environ.get("ASC_PRIVATE_KEY"):
        return os.environ["ASC_PRIVATE_KEY"].replace("\\n", "\n")
    path = os.environ.get("ASC_PRIVATE_KEY_PATH")
    if path:
        return Path(path).read_text()
    sys.exit("error: set ASC_PRIVATE_KEY or ASC_PRIVATE_KEY_PATH")


def token():
    now = int(time.time())
    return jwt.encode(
        {"iss": _env("ASC_ISSUER_ID"), "iat": now, "exp": now + 15 * 60,
         "aud": "appstoreconnect-v1"},
        _private_key(),
        algorithm="ES256",
        headers={"kid": _env("ASC_KEY_ID"), "typ": "JWT"},
    )


def request(method, path, params=None, body=None, raw=False):
    url = path if path.startswith("http") else API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token()}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"error: {method} {url} -> HTTP {e.code}\n{detail}")
    if raw:
        return payload
    return json.loads(payload) if payload else {}


def get_all(path, params=None):
    """Follow `links.next` pagination and return every `data` item."""
    items, page = [], request("GET", path, params)
    items.extend(page.get("data", []))
    while page.get("links", {}).get("next"):
        page = request("GET", page["links"]["next"])
        items.extend(page.get("data", []))
    return items


def _out(obj):
    json.dump(obj, sys.stdout, indent=2)
    sys.stdout.write("\n")


# --- commands ---------------------------------------------------------------

def cmd_apps(args):
    apps = get_all("/v1/apps", {"limit": 200})
    _out([{"id": a["id"], "name": a["attributes"]["name"],
           "bundleId": a["attributes"]["bundleId"],
           "sku": a["attributes"].get("sku")} for a in apps])


def cmd_versions(args):
    versions = request("GET", f"/v1/apps/{args.app}/appStoreVersions",
                       {"limit": args.limit})["data"]
    _out([{"id": v["id"], **{k: v["attributes"].get(k) for k in
           ("versionString", "appStoreState", "platform", "createdDate",
            "releaseType")}} for v in versions])


def cmd_builds(args):
    builds = request("GET", "/v1/builds", {
        "filter[app]": args.app, "sort": "-uploadedDate", "limit": args.limit,
    })["data"]
    _out([{"id": b["id"], **{k: b["attributes"].get(k) for k in
           ("version", "uploadedDate", "processingState", "expired",
            "minOsVersion")}} for b in builds])


def cmd_reviews(args):
    reviews = request("GET", f"/v1/apps/{args.app}/customerReviews", {
        "sort": "-createdDate", "limit": args.limit,
    })["data"]
    _out([{"id": r["id"], **{k: r["attributes"].get(k) for k in
           ("rating", "title", "body", "reviewerNickname", "createdDate",
            "territory")}} for r in reviews])


def cmd_iaps(args):
    iaps = get_all(f"/v1/apps/{args.app}/inAppPurchasesV2", {"limit": 200})
    _out([{"id": i["id"], **{k: i["attributes"].get(k) for k in
           ("name", "productId", "inAppPurchaseType", "state")}}
          for i in iaps])


def cmd_sales(args):
    """Daily summary sales report (units, proceeds) as TSV."""
    report_date = args.date or (date.today() - timedelta(days=2)).isoformat()
    payload = request("GET", "/v1/salesReports", {
        "filter[frequency]": args.frequency,
        "filter[reportType]": "SALES",
        "filter[reportSubType]": "SUMMARY",
        "filter[vendorNumber]": _env("ASC_VENDOR_NUMBER"),
        "filter[reportDate]": report_date,
        "filter[version]": args.version,
    }, raw=True)
    tsv = gzip.decompress(payload).decode()
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / f"sales-{args.frequency.lower()}-{report_date}.tsv"
    out.write_text(tsv)
    print(f"# saved {out}", file=sys.stderr)
    sys.stdout.write(tsv)


def cmd_analytics_enable(args):
    """Ask Apple to start generating analytics reports for an app (once)."""
    _out(request("POST", "/v1/analyticsReportRequests", body={"data": {
        "type": "analyticsReportRequests",
        "attributes": {"accessType": args.access},
        "relationships": {"app": {"data": {"type": "apps", "id": args.app}}},
    }}))


def cmd_analytics_list(args):
    """List report requests for an app and the reports under each."""
    requests_ = request("GET", f"/v1/apps/{args.app}/analyticsReportRequests")["data"]
    result = []
    for r in requests_:
        params = {"limit": 200}
        if args.category:
            params["filter[category]"] = args.category
        reports = get_all(f"/v1/analyticsReportRequests/{r['id']}/reports", params)
        result.append({
            "requestId": r["id"], **r["attributes"],
            "reports": [{"id": rep["id"], "name": rep["attributes"]["name"],
                         "category": rep["attributes"]["category"]}
                        for rep in reports],
        })
    _out(result)


def cmd_analytics_download(args):
    """Download the newest instance(s) of one analytics report to data/."""
    instances = request("GET", f"/v1/analyticsReports/{args.report}/instances", {
        "filter[granularity]": args.granularity, "limit": args.count,
    })["data"]
    if not instances:
        sys.exit("no instances yet (reports appear 1-2 days after enabling)")
    DATA_DIR.mkdir(exist_ok=True)
    saved = []
    for inst in instances:
        day = inst["attributes"]["processingDate"]
        segments = get_all(f"/v1/analyticsReportInstances/{inst['id']}/segments")
        for n, seg in enumerate(segments):
            # Segment URLs are pre-signed; no auth header needed.
            with urllib.request.urlopen(seg["attributes"]["url"], timeout=120) as resp:
                content = gzip.decompress(resp.read())
            out = DATA_DIR / f"analytics-{args.report}-{day}-{n}.tsv"
            out.write_bytes(content)
            saved.append(str(out))
    _out(saved)


def cmd_token(args):
    """Print a JWT, e.g. for manual curl debugging."""
    print(token())


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("apps", help="list apps").set_defaults(fn=cmd_apps)

    for name, fn, default_limit, help_ in (
        ("versions", cmd_versions, 10, "App Store versions and review state"),
        ("builds", cmd_builds, 10, "recent uploaded builds"),
        ("reviews", cmd_reviews, 50, "newest customer reviews"),
    ):
        s = sub.add_parser(name, help=help_)
        s.add_argument("app", help="App Store Connect app id")
        s.add_argument("--limit", type=int, default=default_limit)
        s.set_defaults(fn=fn)

    s = sub.add_parser("iaps", help="in-app purchases for an app")
    s.add_argument("app")
    s.set_defaults(fn=cmd_iaps)

    s = sub.add_parser("sales", help="summary sales report (TSV)")
    s.add_argument("--date", help="YYYY-MM-DD (default: 2 days ago)")
    s.add_argument("--frequency", default="DAILY",
                   choices=["DAILY", "WEEKLY", "MONTHLY", "YEARLY"])
    s.add_argument("--version", default="1_1")
    s.set_defaults(fn=cmd_sales)

    s = sub.add_parser("analytics-enable", help="start analytics reports for an app")
    s.add_argument("app")
    s.add_argument("--access", default="ONGOING",
                   choices=["ONGOING", "ONE_TIME_SNAPSHOT"])
    s.set_defaults(fn=cmd_analytics_enable)

    s = sub.add_parser("analytics-list", help="list available analytics reports")
    s.add_argument("app")
    s.add_argument("--category", choices=[
        "APP_STORE_ENGAGEMENT", "APP_STORE_COMMERCE", "APP_USAGE",
        "FRAMEWORK_USAGE", "PERFORMANCE"])
    s.set_defaults(fn=cmd_analytics_list)

    s = sub.add_parser("analytics-download", help="download an analytics report")
    s.add_argument("report", help="report id from analytics-list")
    s.add_argument("--granularity", default="DAILY",
                   choices=["DAILY", "WEEKLY", "MONTHLY"])
    s.add_argument("--count", type=int, default=1, help="how many recent instances")
    s.set_defaults(fn=cmd_analytics_download)

    sub.add_parser("token", help="print a JWT").set_defaults(fn=cmd_token)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
