# Free apps for every device

Everything below is free (no subscription). Where an app has a paid tier, it is noted; the free tier is enough for these playlists.

You need two things in any app:

1. **A playlist URL** from [`playlists/README.md`](../playlists/README.md). Start with a featured list (for example English news) or your country's file; `all.m3u` has 18,000+ streams and is slow to load on weaker devices.
2. **An EPG URL** (optional, gives you the program guide). Each playlist already contains one in its header, and most apps pick it up automatically. If yours doesn't, copy one from [EPG.md](EPG.md).

Tip: the raw GitHub URLs are long. Open the playlist index on your phone, copy the link, and paste it into the app, or shorten it once with any URL shortener.

---

## Android TV, Google TV, Chromecast with Google TV, Nvidia Shield, Mi Box

| App | Cost | Notes |
|---|---|---|
| **Televizo** | Free | Lightweight, great EPG, works with M3U URLs directly. Best free choice. |
| **OTT Navigator** | Free (premium optional) | Powerful filters and archive support. |
| **TiviMate** | Free (premium unlocks multiple playlists, recording) | The most polished UI; the free version plays one playlist, which is all you need. |
| **IPTV Smarters Pro** | Free | Choose "Load your playlist or file/URL". |
| **Kodi + PVR IPTV Simple Client** | Free, open source | Full TV guide and recording. |
| **Jellyfin** | Free, open source | If you run the Docker stack in [`docker/`](../docker/docker-compose.yml). |

Setup (Televizo / TiviMate / OTT Navigator are all the same idea):

1. Install the app from the Play Store.
2. Add playlist → **URL / M3U** → paste the playlist link → Next.
3. If asked for EPG, paste the EPG URL for your country from [EPG.md](EPG.md) (or leave the auto-detected one).
4. Wait for channels and guide to load. Done.

## Amazon Fire TV Stick / Fire TV Cube

The Amazon Appstore has **IPTV Smarters Pro**, **Televizo**, **OTT Navigator** and **TiviMate**. Install from the Appstore and follow the Android TV steps.

Alternative: install **Downloader** from the Appstore, then open the web player URL (see "Web player" below) inside it.

## Smart TVs (Samsung Tizen, LG webOS, Hisense VIDAA, Sony/Philips/TCL Android TV)

- **Android TV / Google TV sets** (Sony, Philips, TCL, Hisense Android): use the Android TV section above.
- **Samsung (Tizen) and LG (webOS)**: free options are **SS IPTV** (free, add playlist via its website code) and **IPTV Smarters** (Samsung/LG store). *Smart IPTV (SIPTV)* and *Smart STB* are popular but require a one-time fee; avoid unless you want them.
- **Any smart TV with a browser**: open the web player URL (below). Fewer streams play in a browser than in an app, but it needs no install.
- **Simplest universal fix for any TV**: a cheap Android TV / Fire TV stick plugged into an HDMI port.

## Roku

Roku does not allow generic IPTV apps on its store. Workarounds, all free:

- Screen-mirror / cast from a phone running one of the Android apps above.
- Run **Jellyfin** (Docker stack in this repo); the Jellyfin Roku channel shows the Live TV guide.
- The Roku "web video caster" style apps on your phone can cast individual stream URLs.

## Apple TV (tvOS)

| App | Cost |
|---|---|
| **iPlayTV** | Paid (one-time) — best, but not free |
| **IPTV Smarters Player** | Free |
| **Kodi** (sideload) | Free |
| **Jellyfin** | Free (with the Docker stack) |
| **VLC for Apple TV** | Free. Open Network Stream only, no playlist UI |

## iPhone / iPad

- **IPTV Smarters Player** (free), **GSE Smart IPTV** (free), **Flex IPTV** (free). Add playlist → URL.
- **VLC for iOS** (free): Network → Open Network Stream → paste a single stream URL, or download the `.m3u` file to Files and open it with VLC.
- **Safari**: open the web player URL. Safari plays HLS natively, so many streams work.

## Android phones and tablets

- **Televizo**, **OTT Navigator**, **IPTV Smarters Pro**, **TiviMate** (phone version), **VLC**, **MX Player** (open the m3u file).
- **Chrome**: open the web player and tap **Install app** to add it to the home screen as a standalone app.

## Windows, macOS, Linux

| App | Notes |
|---|---|
| **VLC** | Media → Open Network Stream → paste the playlist URL. The playlist appears in View → Playlist. Works with every stream type including DASH and RTMP. |
| **Kodi** | Add-ons → PVR IPTV Simple Client → set M3U URL and XMLTV URL → enable TV in settings. Full guide and recording. |
| **IPTVnator** | Free, open source desktop IPTV player with EPG. |
| **Hypnotix** | Free, Linux (ships with Linux Mint). |
| **Jellyfin** | See Docker below. |
| **Browser** | The web player in this repo. |

## Web player (no install, any device with a browser)

The `player/` folder is a complete web app. Three ways to use it:

1. **GitHub Pages** (recommended): in the repository go to *Settings → Pages → Source: GitHub Actions*. The included workflow then publishes it at `https://<your-user>.github.io/rr/` on every update.
2. **Locally**: `cd player && python3 -m http.server 8000` then open `http://localhost:8000`.
3. **Docker**: `cd docker && docker compose up -d` then open `http://localhost:8080`.

The player supports search, country/category/language filters, the featured lists, favourites, backup sources per channel, keyboard control, light/dark theme, deep links (`?ch=BBCNews.uk`, `?country=IN`, `?list=english-news`), loading any external playlist (`?m3u=https://...`), and installs as a PWA on Android/desktop Chrome.

Browser limitation: streams whose servers don't allow cross-origin playback, plain `http://` streams on an `https://` page, and DASH `.mpd` streams won't play in a browser. The player tells you when that happens and gives you a **Copy URL** / **Open in VLC** button. Native apps (everything above) don't have these limits.

## Jellyfin: your own TV server (Docker)

[`docker/docker-compose.yml`](../docker/docker-compose.yml) starts Jellyfin plus an nginx that serves the player and playlists.

1. Install Docker, then `cd docker && docker compose up -d`.
2. Open `http://<host>:8096`, finish the Jellyfin wizard.
3. Dashboard → Live TV → Tuner Devices → **+** → *M3U Tuner* → URL `http://web/playlists/featured/english-news.m3u` (or any playlist). Enable "Auto-loop live streams" off, leave the rest default.
4. Dashboard → Live TV → TV Guide Data Providers → **+** → *XMLTV* → URL from [EPG.md](EPG.md) for your country.
5. Install the Jellyfin app on your TV/phone (Android TV, Fire TV, Roku, Apple TV, iOS, Samsung, LG, Xbox all have one), sign in, and open **Live TV**.

Jellyfin handles the heavy lifting (one server, every device), and can record shows to disk.
