#!/usr/bin/env python3
"""
Build free IPTV playlists (M3U) from the iptv-org public database.

Everything here is pulled from https://github.com/iptv-org (CC0 data): a
community-maintained index of stream URLs that broadcasters have made publicly
available on the open internet. No video is hosted in this repository.

Usage (stdlib only, Python 3.9+):

    python3 scripts/build_playlists.py                 # build everything into playlists/ and player/
    python3 scripts/build_playlists.py --refresh       # re-download the iptv-org data first
    python3 scripts/build_playlists.py --countries IN US UK --no-geo-blocked -o my.m3u
    python3 scripts/build_playlists.py --categories news sports --languages eng -o news-sports.m3u

Run with -h for the full option list.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

API_BASES = [
    "https://raw.githubusercontent.com/iptv-org/api/gh-pages/",
    "https://iptv-org.github.io/api/",
]
DATASETS = ["channels", "feeds", "streams", "logos", "categories", "countries", "languages"]

# Free XMLTV program guides (gzip'd), keyed by iptv-org country code.
# epgshare01 publishes guides whose channel ids match the iptv-org ids we use
# in tvg-id, so most apps light up the guide automatically.
EPG_BASE = "https://epgshare01.online/epgshare01/"
EPG_COUNTRIES = {
    "AL": "AL1", "AR": "AR1", "AT": "AT1", "AU": "AU1", "BA": "BA1", "BE": "BE2", "BG": "BG1",
    "BR": "BR1", "CA": "CA1", "CH": "CH1", "CL": "CL1", "CO": "CO1", "CR": "CR1", "CY": "CY1",
    "CZ": "CZ1", "DE": "DE1", "DK": "DK1", "DO": "DO1", "EC": "EC1", "EG": "EG1", "ES": "ES1",
    "FI": "FI1", "FR": "FR1", "GR": "GR1", "HK": "HK1", "HR": "HR1", "HU": "HU1", "ID": "ID1",
    "IE": "IE1", "IL": "IL1", "IN": "IN1", "IT": "IT1", "JM": "JM1", "JP": "JP1", "KE": "KE1",
    "KR": "KR1", "LT": "LT1", "LV": "LV1", "MT": "MT1", "MX": "MX1", "MY": "MY1", "NG": "NG1",
    "NL": "NL1", "NO": "NO1", "NZ": "NZ1", "PA": "PA1", "PE": "PE1", "PH": "PH1", "PK": "PK1",
    "PL": "PL1", "PT": "PT1", "RO": "RO1", "RS": "RS1", "SA": "SA1", "SE": "SE1", "SG": "SG1",
    "SK": "SK1", "SV": "SV1", "TR": "TR1", "UK": "UK1", "US": "US1", "UY": "UY1", "VN": "VN1",
    "ZA": "ZA1",
}
EPG_ALL = EPG_BASE + "epg_ripper_ALL_SOURCES1.xml.gz"


def epg_url(country: str | None) -> str | None:
    key = EPG_COUNTRIES.get((country or "").upper())
    return f"{EPG_BASE}epg_ripper_{key}.xml.gz" if key else None


# --------------------------------------------------------------------------- data


def fetch(name: str, cache_dir: Path, refresh: bool) -> list[dict]:
    path = cache_dir / f"{name}.json"
    if path.exists() and not refresh:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    last_err: Exception | None = None
    for base in API_BASES:
        url = f"{base}{name}.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "free-iptv-builder/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            cache_dir.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(f"  downloaded {name}.json ({len(data)//1024} KB) from {base}")
            return json.loads(data)
        except Exception as exc:  # noqa: BLE001 - try the next mirror
            last_err = exc
            print(f"  ! {url}: {exc}", file=sys.stderr)
    raise SystemExit(f"could not download {name}.json: {last_err}")


class Db:
    """Joined view of the iptv-org datasets."""

    def __init__(self, cache_dir: Path, refresh: bool) -> None:
        raw = {name: fetch(name, cache_dir, refresh) for name in DATASETS}
        self.channels = {c["id"]: c for c in raw["channels"]}
        self.categories = {c["id"]: c["name"] for c in raw["categories"]}
        self.countries = {c["code"]: c for c in raw["countries"]}
        self.languages = {l["code"]: l["name"] for l in raw["languages"]}
        self.feeds: dict[tuple[str, str], dict] = {}
        self.main_feed: dict[str, dict] = {}
        for f in raw["feeds"]:
            self.feeds[(f["channel"], f["id"])] = f
            if f.get("is_main") or f["channel"] not in self.main_feed:
                self.main_feed[f["channel"]] = f
        self.logos: dict[str, str] = {}
        for l in raw["logos"]:
            # prefer the logo flagged in_use and attached to the channel (not a feed)
            key = l["channel"]
            if key in self.logos and (l.get("feed") or not l.get("in_use", True)):
                continue
            self.logos[key] = l["url"]
        self.streams = raw["streams"]

    def entries(self) -> list[dict]:
        """Flatten every stream into a self-describing playlist entry."""
        out = []
        for s in self.streams:
            ch = self.channels.get(s["channel"] or "")
            if ch and ch.get("is_nsfw"):
                continue
            cats = [c for c in (ch["categories"] if ch else []) if c != "xxx"]
            if ch and "xxx" in ch["categories"]:
                continue
            feed = None
            if ch:
                feed = self.feeds.get((ch["id"], s["feed"])) if s.get("feed") else self.main_feed.get(ch["id"])
            langs = feed["languages"] if feed else []
            name = ch["name"] if ch else (s.get("title") or "Unknown")
            feed_name = ""
            if feed and s.get("feed") and not feed.get("is_main"):
                feed_name = feed["name"]
            labels = list(s.get("labels") or [])
            out.append(
                {
                    "id": ch["id"] if ch else "",
                    "feed": s.get("feed") or "",
                    "name": name,
                    "feed_name": feed_name,
                    "country": ch["country"] if ch else "",
                    "categories": cats,
                    "languages": langs,
                    "logo": self.logos.get(ch["id"], "") if ch else "",
                    "url": s["url"],
                    "quality": s.get("quality") or "",
                    "labels": labels,
                    "user_agent": s.get("user_agent") or "",
                    "referrer": s.get("referrer") or "",
                    "website": ch.get("website") or "" if ch else "",
                }
            )
        return out


# --------------------------------------------------------------------------- m3u


def esc(value: str) -> str:
    return value.replace('"', "'").replace("\n", " ").strip()


def extinf(e: dict, db: Db, group: str) -> str:
    attrs = []
    if e["id"]:
        attrs.append(f'tvg-id="{esc(e["id"])}"')
    attrs.append(f'tvg-name="{esc(e["name"])}"')
    if e["logo"]:
        attrs.append(f'tvg-logo="{esc(e["logo"])}"')
    if e["country"]:
        attrs.append(f'tvg-country="{e["country"]}"')
    if e["languages"]:
        attrs.append(f'tvg-language="{esc(";".join(db.languages.get(l, l) for l in e["languages"]))}"')
    if e["user_agent"]:
        attrs.append(f'http-user-agent="{esc(e["user_agent"])}"')
    if e["referrer"]:
        attrs.append(f'http-referrer="{esc(e["referrer"])}"')
    attrs.append(f'group-title="{esc(group)}"')
    title = e["name"]
    if e["feed_name"]:
        title += f" {e['feed_name']}"
    if e["quality"]:
        title += f" ({e['quality']})"
    for label in e["labels"]:
        title += f" [{label}]"
    lines = [f"#EXTINF:-1 {' '.join(attrs)},{esc(title)}"]
    if e["user_agent"]:
        lines.append(f"#EXTVLCOPT:http-user-agent={e['user_agent']}")
    if e["referrer"]:
        lines.append(f"#EXTVLCOPT:http-referrer={e['referrer']}")
    lines.append(e["url"])
    return "\n".join(lines)


def group_for(e: dict, db: Db, mode: str) -> str:
    if mode == "country":
        c = db.countries.get(e["country"])
        return c["name"] if c else "International"
    if mode == "language":
        return db.languages.get(e["languages"][0], e["languages"][0]) if e["languages"] else "Unknown"
    cats = [db.categories.get(c, c.title()) for c in e["categories"]]
    return ";".join(cats) if cats else "Other"


def write_m3u(path: Path, entries: list[dict], db: Db, group_mode: str, epg: str | list[str] | None) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "#EXTM3U"
    if epg:
        urls = epg if isinstance(epg, list) else [epg]
        header += f' url-tvg="{",".join(urls)}" x-tvg-url="{",".join(urls)}"'
    body = [header]
    for e in entries:
        body.append(extinf(e, db, group_for(e, db, group_mode)))
    path.write_text("\n".join(body) + "\n", encoding="utf-8")
    return len(entries)


# --------------------------------------------------------------------------- filtering


def sort_key(e: dict):
    return (e["name"].casefold(), e["feed_name"], -quality_rank(e["quality"]))


def quality_rank(q: str) -> int:
    m = re.match(r"(\d+)", q or "")
    return int(m.group(1)) if m else 0


def apply_filters(entries: list[dict], args) -> list[dict]:
    out = entries
    if args.countries:
        wanted = {c.upper() for c in args.countries}
        out = [e for e in out if e["country"] in wanted]
    if args.categories:
        wanted = {c.lower() for c in args.categories}
        out = [e for e in out if wanted & set(e["categories"])]
    if args.languages:
        wanted = {l.lower() for l in args.languages}
        out = [e for e in out if wanted & set(e["languages"])]
    if args.no_geo_blocked:
        out = [e for e in out if "Geo-blocked" not in e["labels"]]
    if args.no_not_24_7:
        out = [e for e in out if "Not 24/7" not in e["labels"]]
    if args.https_only:
        out = [e for e in out if e["url"].startswith("https://")]
    if args.min_quality:
        out = [e for e in out if not e["quality"] or quality_rank(e["quality"]) >= args.min_quality]
    if args.search:
        rx = re.compile(args.search, re.I)
        out = [e for e in out if rx.search(e["name"])]
    return sorted(out, key=sort_key)


# --------------------------------------------------------------------------- full build


def raw_base_url(repo_root: Path, override: str | None) -> str:
    if override:
        return override.rstrip("/") + "/"
    try:
        remote = subprocess.check_output(["git", "-C", str(repo_root), "remote", "get-url", "origin"], text=True).strip()
        branch = subprocess.check_output(["git", "-C", str(repo_root), "symbolic-ref", "--short", "HEAD"], text=True).strip()
        m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", remote)
        if m:
            return f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{branch}/"
    except Exception:  # noqa: BLE001
        pass
    return "./"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def build_all(db: Db, entries: list[dict], out_dir: Path, player_dir: Path, base_url: str, curated_path: Path, with_languages: bool = False) -> None:
    entries = sorted(entries, key=sort_key)
    counts: dict[str, dict] = {"countries": {}, "categories": {}, "languages": {}, "featured": {}}

    print("writing playlists ...")
    n_all = write_m3u(out_dir / "all.m3u", entries, db, "category", EPG_ALL)

    by_country: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_country[e["country"] or "intl"].append(e)
    for code, items in sorted(by_country.items()):
        name = db.countries[code]["name"] if code in db.countries else "International"
        counts["countries"][code.lower()] = {"name": name, "count": write_m3u(out_dir / "countries" / f"{code.lower()}.m3u", items, db, "category", epg_url(code))}

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        for c in e["categories"] or ["other"]:
            by_cat[c].append(e)
    for cat, items in sorted(by_cat.items()):
        counts["categories"][cat] = {"name": db.categories.get(cat, cat.title()), "count": write_m3u(out_dir / "categories" / f"{cat}.m3u", items, db, "country", EPG_ALL)}

    by_lang: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        for l in e["languages"]:
            by_lang[l].append(e)
    lang_counts = {l: len(v) for l, v in by_lang.items() if len(v) >= 100}
    if with_languages:
        for lang in lang_counts:
            counts["languages"][lang] = {"name": db.languages.get(lang, lang), "count": write_m3u(out_dir / "languages" / f"{lang}.m3u", by_lang[lang], db, "category", EPG_ALL)}

    # curated / featured lists ------------------------------------------------
    curated = json.loads(curated_path.read_text(encoding="utf-8"))
    by_id: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        if e["id"]:
            by_id[e["id"]].append(e)
    for key, spec in curated.items():
        items: list[dict] = []
        seen = set()
        for cid in spec["channels"]:
            for e in by_id.get(cid, []):
                if spec.get("languages") and not (set(spec["languages"]) & set(e["languages"])):
                    continue
                if e["url"] in seen:
                    continue
                seen.add(e["url"])
                items.append(e)
        missing = [cid for cid in spec["channels"] if cid not in by_id]
        if missing:
            print(f"  featured/{key}: no streams right now for {', '.join(missing)}")
        epgs = sorted({u for u in (epg_url(e["country"]) for e in items) if u}) or EPG_ALL
        counts["featured"][key] = {"name": spec["name"], "description": spec.get("description", ""), "count": write_m3u(out_dir / "featured" / f"{key}.m3u", items, db, "category", epgs)}

    # compact JSON for the web player -----------------------------------------
    player_dir.mkdir(parents=True, exist_ok=True)
    compact = []
    for e in entries:
        compact.append(
            {
                "i": e["id"],
                "n": e["name"] + (f" {e['feed_name']}" if e["feed_name"] else ""),
                "c": e["country"],
                "g": e["categories"],
                "l": e["languages"],
                "o": e["logo"],
                "u": e["url"],
                "q": e["quality"],
                "b": e["labels"],
                "a": e["user_agent"],
                "r": e["referrer"],
            }
        )
    meta = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": "https://github.com/iptv-org/iptv",
        "countries": {k: v["name"] for k, v in db.countries.items()},
        "categories": db.categories,
        "languages": {k: db.languages.get(k, k) for k in lang_counts},
        "featured": {k: {"name": v["name"], "channels": curated[k]["channels"]} for k, v in counts["featured"].items()},
        "epg": {k: epg_url(k) for k in EPG_COUNTRIES},
        "total": len(compact),
    }
    (player_dir / "channels.json").write_text(json.dumps({"meta": meta, "channels": compact}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    write_index(out_dir, counts, n_all, base_url, meta["generated"])
    print(f"done: {n_all} streams, {len(counts['countries'])} countries, {len(counts['categories'])} categories, {len(counts['languages'])} languages, {len(counts['featured'])} featured lists")


def write_index(out_dir: Path, counts: dict, n_all: int, base_url: str, generated: str) -> None:
    def link(rel: str) -> str:
        return f"`{base_url}playlists/{rel}`" if base_url.startswith("http") else f"[{rel}]({rel})"

    lines = [
        "# Playlists",
        "",
        f"Generated {generated} from the [iptv-org](https://github.com/iptv-org/iptv) public database. "
        "Paste any URL below into a player (see [docs/APPS.md](../docs/APPS.md)). "
        "Every file already carries a free EPG (program guide) link in its header.",
        "",
        "## Everything",
        "",
        f"| Playlist | Streams | URL |", "|---|---:|---|",
        f"| All channels (grouped by category) | {n_all} | {link('all.m3u')} |",
        "",
        "## Featured (hand-picked)",
        "",
        "| Playlist | Streams | URL |", "|---|---:|---|",
    ]
    for key, v in counts["featured"].items():
        lines.append(f"| {v['name']} — {v['description']} | {v['count']} | {link(f'featured/{key}.m3u')} |")
    lines += ["", "## By category", "", "| Category | Streams | URL |", "|---|---:|---|"]
    for key, v in sorted(counts["categories"].items(), key=lambda kv: kv[1]["name"]):
        lines.append(f"| {v['name']} | {v['count']} | {link(f'categories/{key}.m3u')} |")
    if counts["languages"]:
        lines += ["", "## By language", "", "| Language | Streams | URL |", "|---|---:|---|"]
        for key, v in sorted(counts["languages"].items(), key=lambda kv: -kv[1]["count"]):
            lines.append(f"| {v['name']} | {v['count']} | {link(f'languages/{key}.m3u')} |")
    else:
        lines += ["", "## By language", "", "Language playlists are built on demand, e.g. `python3 scripts/build_playlists.py --languages hin -o hindi.m3u` "
                  "(or pass `--with-languages` to the full build). The web player can also filter by language."]
    lines += ["", "## By country", "", "| Country | Streams | URL |", "|---|---:|---|"]
    for key, v in sorted(counts["countries"].items(), key=lambda kv: kv[1]["name"]):
        lines.append(f"| {v['name']} | {v['count']} | {link(f'countries/{key}.m3u')} |")
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cache-dir", default=str(repo_root / ".cache"), help="where the iptv-org JSON is cached")
    p.add_argument("--refresh", action="store_true", help="re-download the iptv-org data even if cached")
    p.add_argument("-o", "--output", help="write ONE filtered playlist to this file instead of the full build")
    p.add_argument("--countries", nargs="+", metavar="CC", help="ISO country codes, e.g. US IN UK")
    p.add_argument("--categories", nargs="+", metavar="CAT", help="e.g. news sports kids movies music")
    p.add_argument("--languages", nargs="+", metavar="LANG", help="ISO 639-3 codes, e.g. eng hin tel spa")
    p.add_argument("--search", metavar="REGEX", help="only channels whose name matches")
    p.add_argument("--no-geo-blocked", action="store_true", help="drop streams flagged Geo-blocked")
    p.add_argument("--no-not-24-7", action="store_true", help="drop streams flagged Not 24/7")
    p.add_argument("--https-only", action="store_true", help="drop plain http:// streams (needed for the web player on https)")
    p.add_argument("--min-quality", type=int, metavar="P", help="drop streams below this height, e.g. 720")
    p.add_argument("--group-by", choices=["category", "country", "language"], default="category")
    p.add_argument("--out-dir", default=str(repo_root / "playlists"))
    p.add_argument("--player-dir", default=str(repo_root / "player"))
    p.add_argument("--curated", default=str(repo_root / "scripts" / "curated.json"))
    p.add_argument("--with-languages", action="store_true", help="also write playlists/languages/*.m3u (adds ~5 MB)")
    p.add_argument("--base-url", help="public raw URL prefix used in playlists/README.md (auto-detected from git)")
    args = p.parse_args(argv)

    print("loading iptv-org data ...")
    db = Db(Path(args.cache_dir), args.refresh)
    entries = db.entries()
    print(f"  {len(entries)} streams across {len({e['country'] for e in entries if e['country']})} countries")

    if args.output:
        selected = apply_filters(entries, args)
        epgs = sorted({u for u in (epg_url(c) for c in (args.countries or [])) if u}) or EPG_ALL
        n = write_m3u(Path(args.output), selected, db, args.group_by, epgs)
        print(f"wrote {n} streams to {args.output}")
        return

    build_all(db, entries, Path(args.out_dir), Path(args.player_dir), raw_base_url(repo_root, args.base_url), Path(args.curated), args.with_languages)


if __name__ == "__main__":
    main()
