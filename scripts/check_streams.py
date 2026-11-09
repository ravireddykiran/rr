#!/usr/bin/env python3
"""
Check which streams in a playlist actually respond, and optionally write a
playlist containing only the working ones.

    python3 scripts/check_streams.py playlists/featured/english-news.m3u
    python3 scripts/check_streams.py playlists/countries/in.m3u --write-online online-in.m3u --workers 64

Results depend on WHERE you run this: a geo-blocked stream looks dead from the
wrong country, and some hosts rate-limit. Run it on the device/network you will
actually watch from. Standard library only.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def parse_m3u(text: str) -> tuple[str, list[dict]]:
    header = "#EXTM3U"
    items: list[dict] = []
    block: list[str] = []
    for line in text.splitlines():
        if line.startswith("#EXTM3U"):
            header = line
            continue
        if not line.strip():
            continue
        if line.startswith("#"):
            block.append(line)
            continue
        extinf = next((b for b in block if b.startswith("#EXTINF")), "")
        ua = next((b.split("=", 1)[1] for b in block if b.startswith("#EXTVLCOPT:http-user-agent=")), None)
        ref = next((b.split("=", 1)[1] for b in block if b.startswith("#EXTVLCOPT:http-referrer=")), None)
        name = extinf.rsplit(",", 1)[-1] if extinf else line
        items.append({"name": name, "url": line.strip(), "block": block, "ua": ua, "ref": ref})
        block = []
    return header, items


def probe(item: dict, timeout: float) -> dict:
    url = item["url"]
    if not url.startswith(("http://", "https://")):
        return {**item, "status": "skipped", "detail": "non-http scheme"}
    headers = {"User-Agent": item["ua"] or DEFAULT_UA, "Accept": "*/*"}
    if item["ref"]:
        headers["Referer"] = item["ref"]
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            head = resp.read(4096)
            ctype = resp.headers.get("Content-Type", "")
        ms = int((time.time() - t0) * 1000)
        if head.lstrip().startswith(b"#EXTM3U") or "mpegurl" in ctype.lower() or url.lower().split("?")[0].endswith(".mpd") and b"<MPD" in head:
            return {**item, "status": "online", "detail": f"{ms} ms", "ms": ms}
        if head.lstrip().startswith(b"<"):
            return {**item, "status": "error", "detail": "returned HTML, not a stream", "ms": ms}
        return {**item, "status": "online", "detail": f"{ms} ms, {ctype or 'unknown type'}", "ms": ms}
    except urllib.error.HTTPError as exc:
        kind = "geo-blocked?" if exc.code in (401, 403, 451) else "error"
        return {**item, "status": kind, "detail": f"HTTP {exc.code}"}
    except Exception as exc:  # noqa: BLE001
        msg = str(exc).lower()
        if "timed out" in msg or "timeout" in msg:
            return {**item, "status": "timeout", "detail": f"> {timeout:.0f}s"}
        return {**item, "status": "error", "detail": re.sub(r"\s+", " ", str(exc))[:120]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("playlist", help="path or URL of an .m3u file")
    p.add_argument("--workers", type=int, default=32)
    p.add_argument("--timeout", type=float, default=10.0)
    p.add_argument("--write-online", metavar="FILE", help="write a playlist with only the online streams")
    p.add_argument("--json", metavar="FILE", help="write the full report as JSON")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    if args.playlist.startswith(("http://", "https://")):
        with urllib.request.urlopen(urllib.request.Request(args.playlist, headers={"User-Agent": DEFAULT_UA}), timeout=60) as r:
            text = r.read().decode("utf-8", "replace")
    else:
        text = Path(args.playlist).read_text(encoding="utf-8", errors="replace")
    header, items = parse_m3u(text)
    print(f"checking {len(items)} streams with {args.workers} workers (timeout {args.timeout:.0f}s) ...", file=sys.stderr)

    results: list[dict] = [None] * len(items)  # type: ignore[list-item]
    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(probe, it, args.timeout): i for i, it in enumerate(items)}
        for fut in cf.as_completed(futs):
            i = futs[fut]
            results[i] = fut.result()
            done += 1
            if not args.quiet:
                r = results[i]
                mark = {"online": "OK ", "timeout": "...", "skipped": "-- "}.get(r["status"], "ERR")
                print(f"[{done:>5}/{len(items)}] {mark} {r['name'][:50]:<50} {r['status']:<12} {r['detail']}", file=sys.stderr)

    summary = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    print("\nsummary:", ", ".join(f"{k}: {v}" for k, v in sorted(summary.items(), key=lambda kv: -kv[1])))

    if args.write_online:
        online = [r for r in results if r["status"] == "online"]
        out = [header] + ["\n".join(r["block"] + [r["url"]]) for r in online]
        Path(args.write_online).write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"wrote {len(online)} online streams to {args.write_online}")
    if args.json:
        Path(args.json).write_text(json.dumps([{k: v for k, v in r.items() if k != "block"} for r in results], indent=1), encoding="utf-8")
        print(f"wrote report to {args.json}")


if __name__ == "__main__":
    main()
