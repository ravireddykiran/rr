# EPG (program guide)

Every playlist in `playlists/` already includes an EPG link in its first line (`url-tvg=`). TiviMate, Televizo, OTT Navigator, IPTV Smarters, Kodi and Jellyfin can read it automatically. If your app asks for an EPG URL separately, use one of these.

The channel IDs in the playlists (`tvg-id`, for example `BBCNews.uk`) follow the iptv-org naming scheme, which these guides use too, so the guide maps onto the channels without manual matching.

## Ready-made XMLTV files (free, updated daily)

Hosted by the epgshare01 project, gzip compressed (every app understands `.xml.gz`):

| Region | URL |
|---|---|
| United States | `https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz` |
| US local stations | `https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS2.xml.gz` |
| US sports | `https://epgshare01.online/epgshare01/epg_ripper_US_SPORTS1.xml.gz` |
| United Kingdom | `https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz` |
| India | `https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz` and `..._IN4.xml.gz` |
| Canada | `https://epgshare01.online/epgshare01/epg_ripper_CA1.xml.gz` |
| Australia | `https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz` |
| Germany | `https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz` |
| France | `https://epgshare01.online/epgshare01/epg_ripper_FR1.xml.gz` |
| Spain | `https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz` |
| Italy | `https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz` |
| Brazil | `https://epgshare01.online/epgshare01/epg_ripper_BR1.xml.gz` |
| Mexico | `https://epgshare01.online/epgshare01/epg_ripper_MX1.xml.gz` |
| Pluto TV / Plex / Rakuten / DistroTV channels | `..._PLEX1.xml.gz`, `..._RAKUTEN1.xml.gz`, `..._DISTROTV1.xml.gz` |
| Everything (very large, 100+ MB) | `https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz` |

Pattern for other countries: `https://epgshare01.online/epgshare01/epg_ripper_<CC>1.xml.gz` where `<CC>` is the ISO code (AR, AT, BE, BG, CH, CL, CO, CZ, DK, EG, FI, GR, HK, HR, HU, ID, IE, IL, JP, KE, KR, MY, NG, NL, NO, NZ, PE, PH, PK, PL, PT, RO, RS, SA, SE, SG, SK, TR, VN, ZA and more). The full list is in the header of `playlists/all.m3u`'s source script (`EPG_COUNTRIES` in `scripts/build_playlists.py`).

Tip: in TiviMate/Televizo you can add several EPG URLs; add your country plus `US1` for the big ad-supported networks.

## Build your own guide (iptv-org/epg)

If you want a guide for channels the ready-made files miss, the iptv-org EPG grabber pulls schedules from 200+ broadcaster websites:

```sh
git clone --depth 1 https://github.com/iptv-org/epg.git
cd epg && npm install
npm run grab --- --site=tvguide.com        # or any site from SITES.md
# produces guide.xml — serve it from the docker "web" container or any web server
```

A Docker image is documented in that repository as well.
