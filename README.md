# Free IPTV — thousands of legal, free live TV channels

Ready-to-use playlists, a web player that installs as an app, setup guides for every TV device, and a self-hosted Jellyfin stack. Everything is free and the channel data refreshes itself twice a week.

**Where the channels come from.** The [iptv-org](https://github.com/iptv-org/iptv) community index: 18,000+ streams that broadcasters publish openly (public broadcasters, news networks, free ad-supported channels like Pluto TV, Plex, Rakuten, Samsung TV Plus, DistroTV). No pirated pay-TV. Details in [docs/LEGAL.md](docs/LEGAL.md).

**On a phone?** Go straight to **[docs/MOBILE.md](docs/MOBILE.md)** (Android and iPhone, with or without installing anything).

## 1-minute start

1. Pick a playlist from **[playlists/README.md](playlists/README.md)** and copy its URL. Good first picks:

   | Playlist | What's in it |
   |---|---|
   | `playlists/featured/english-news.m3u` | ABC News Live, CBS News, NBC News NOW, Bloomberg, Sky News, BBC News, DW, France 24, Euronews, Al Jazeera's CNA, NHK World, WION, NDTV… |
   | `playlists/featured/india.m3u` | DD, NDTV, Aaj Tak, Republic, Times Now, Sun TV, TV9, ETV, Asianet, Zee, Colors, Star, Sony… across Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati |
   | `playlists/featured/movies.m3u` · `kids.m3u` · `sports.m3u` · `music.m3u` · `documentary.m3u` | Themed free channels |
   | `playlists/countries/us.m3u` · `in.m3u` · `uk.m3u` · … | Everything for one country (181 countries) |
   | `playlists/categories/news.m3u` · `sports.m3u` · … | Everything in one genre (30 categories) |
   | `playlists/all.m3u` | All 18,609 streams (heavy; use on a PC or Jellyfin) |

2. Install a free player on your device and paste the URL. **[docs/APPS.md](docs/APPS.md)** has step-by-step instructions for Android TV / Google TV, Fire TV Stick, Samsung & LG smart TVs, Roku, Apple TV, iPhone/iPad, Android, Windows/macOS/Linux and browsers. Quick picks: **Televizo** or **TiviMate** on Android/Fire TV, **IPTV Smarters** on iPhone/Apple TV/Samsung/LG, **VLC** or **Kodi** on a computer.

3. The program guide (EPG) is already linked inside every playlist. If your app asks for one, see [docs/EPG.md](docs/EPG.md).

## The web player (no install needed)

`player/` is a complete app: search, filters by country / category / language, the featured lists, favourites, backup sources per channel, keyboard shortcuts, light/dark, deep links, and "Install app" on Android and desktop Chrome.

- **Host it on GitHub Pages**: Settings → Pages → Source: *GitHub Actions*. The workflow in `.github/workflows/update.yml` publishes it to `https://<your-user>.github.io/rr/` and republishes after every data refresh.
- **Run it locally**: `cd player && python3 -m http.server 8000` → http://localhost:8000
- **Docker**: `cd docker && docker compose up -d` → http://localhost:8080 (player) and http://localhost:8096 (Jellyfin, see below)

Browsers can't play every stream (CORS, http-on-https and DASH restrictions); the player explains why and offers *Copy URL* / *Open in VLC*. Native apps play everything.

## Jellyfin: one server, every screen

`docker/docker-compose.yml` runs Jellyfin plus nginx. Add a playlist as an *M3U Tuner* and an EPG as *XMLTV*, then use the free Jellyfin app on Android TV, Fire TV, Roku, Apple TV, iOS, Samsung, LG, Xbox or the web. It gives you a proper TV guide and can record. Steps in [docs/APPS.md](docs/APPS.md#jellyfin-your-own-tv-server-docker).

## Build your own playlist

```sh
python3 scripts/build_playlists.py --refresh                                  # rebuild everything from the latest data
python3 scripts/build_playlists.py --countries IN --categories news -o in-news.m3u
python3 scripts/build_playlists.py --languages tel tam -o south-india.m3u
python3 scripts/build_playlists.py --countries US UK --no-geo-blocked --min-quality 720 -o hd-open.m3u
python3 scripts/check_streams.py playlists/featured/english-news.m3u --write-online online.m3u   # keep only streams that respond from your network
```

Edit `scripts/curated.json` to change the featured lists (channel IDs are the `tvg-id` values, searchable in the web player).

## Keeping it fresh

`.github/workflows/update.yml` re-downloads the iptv-org data every Monday and Thursday, commits the regenerated playlists, and redeploys the web player. Run it manually any time from the Actions tab.

## Repository layout

```
playlists/        generated M3U files + index (README.md)
player/           web player (index.html, channels.json, hls.min.js, PWA files)
scripts/          build_playlists.py, check_streams.py, curated.json
docs/             MOBILE.md, APPS.md, EPG.md, TROUBLESHOOTING.md, LEGAL.md
docker/           docker-compose.yml (nginx + Jellyfin), nginx.conf
.github/workflows automatic refresh + GitHub Pages deploy
```

Problems? See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
