# Watch on your phone (5 minutes)

Two ways. **Option A** is a proper TV app with a guide and favourites. **Option B** needs no install at all.

The playlist URLs below point at this repository on GitHub. Pick ONE to start with (you can add more later):

| What you want | Playlist URL |
|---|---|
| English news | `https://raw.githubusercontent.com/ravireddykiran/rr/claude/free-iptv-setup-65wk2h/playlists/featured/english-news.m3u` |
| Indian channels (all languages) | `https://raw.githubusercontent.com/ravireddykiran/rr/claude/free-iptv-setup-65wk2h/playlists/featured/india.m3u` |
| **Telugu — live TV + movies** | `https://raw.githubusercontent.com/ravireddykiran/rr/claude/free-iptv-setup-65wk2h/playlists/featured/telugu.m3u` |
| **Sports (all free, English + global)** | `https://raw.githubusercontent.com/ravireddykiran/rr/claude/free-iptv-setup-65wk2h/playlists/featured/sports.m3u` |
| Movies | `.../playlists/featured/movies.m3u` |
| Sports | `.../playlists/featured/sports.m3u` |
| Kids | `.../playlists/featured/kids.m3u` |
| Music | `.../playlists/featured/music.m3u` |
| Your whole country | `.../playlists/countries/in.m3u` (swap `in` for `us`, `uk`, `ca`, `au`, `ae`, …) |
| Everything (18,000+, slow on phones) | `.../playlists/all.m3u` |

Replace `...` with `https://raw.githubusercontent.com/ravireddykiran/rr/claude/free-iptv-setup-65wk2h`. The full index is in [`playlists/README.md`](../playlists/README.md); open it on your phone and long-press a URL to copy it.

> The URLs go live as soon as this branch is pushed to GitHub (or change the branch name to `main` after merging).

---

## Option A — a TV app

### Android

1. Install **Televizo** from the Play Store (free, no ads in the way, good guide). Alternatives: **OTT Navigator**, **IPTV Smarters Pro**, **TiviMate**.
2. Open it → **Add playlist** → **URL** → paste a playlist URL → Next.
3. The EPG (program guide) is already inside the playlist; if the app asks, leave the detected URL or paste one from [EPG.md](EPG.md).
4. Wait for the channel list, tap a channel. Long-press to favourite. Swipe or use the guide to change channels.

Stream won't open? Long-press the channel → *Select stream / source*. Most channels have 2–20 backup sources.

### iPhone / iPad

1. Install **IPTV Smarters Player** (free) from the App Store. Alternatives: **GSE Smart IPTV**, **Flex IPTV**.
2. Open it → **Add new user** → **Load your playlist or file/URL** → *M3U URL* → paste a playlist URL → Add user.
3. Tap **Live TV**. Favourites: long-press a channel.
4. EPG: Settings → EPG → paste the URL for your country from [EPG.md](EPG.md) (for example `https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz` or `..._US1.xml.gz`).

Single streams in **VLC for iOS** (free): Network → *Open Network Stream* → paste a stream URL. The web player's **Open in VLC** button does this for you.

---

## Option B — no install, use the web player

1. Open the web player in Chrome (Android) or Safari (iPhone):
   - If GitHub Pages is enabled on the repo: `https://ravireddykiran.github.io/rr/`
   - Or on your home Wi-Fi from a computer in the house: `cd player && python3 -m http.server 8000`, then open `http://<computer-ip>:8000` on the phone.
2. Pick a list from **Featured lists…**, or type in the search box. Tap a channel.
3. **Android Chrome**: tap **Install app** in the header (or Chrome menu → *Add to Home screen*). It becomes a standalone full-screen app with its own icon.
   **iPhone Safari**: Share → *Add to Home Screen*.
4. Tap ★ to favourite; tick *Favourites only* for a tidy personal list.

What to expect on a phone browser: Safari plays most HLS streams natively; Chrome on Android plays most of them through the built-in hls.js. A minority of streams refuse to play in any browser because the broadcaster's server blocks cross-site playback or the stream is plain `http://`. The player tells you when that happens and shows **Copy URL** / **Open in VLC**; the same channel will work in Option A.

---

## Tips

- **Geo-blocked** label = only works from the channel's home country. Tick *Hide geo-blocked* in the web player, or in Televizo/Smarters just skip them.
- **Not 24/7** = the channel only streams during live programming.
- **Data use**: a 720p stream is about 1.5 GB per hour; most apps let you pick a lower-quality source (shown as 480p/576p) to save data.
- **Cast to TV**: Televizo, OTT Navigator and IPTV Smarters have Chromecast buttons; from the web player use Chrome's *Cast…* menu.
- **Share a channel**: the web player's **Share link** copies a URL like `?ch=BBCNews.uk` that opens straight on that channel.
