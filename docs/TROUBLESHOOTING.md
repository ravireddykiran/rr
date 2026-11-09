# Troubleshooting

**A channel doesn't play.**
Most channels in the index have more than one source; switch to the next one (the web player shows "N sources", TiviMate long-press → change source, VLC: the duplicates are separate entries). Free streams come and go; the playlists are regenerated twice a week by the GitHub Action so dead links disappear and new ones appear.

**"Geo-blocked" label.**
The broadcaster restricts the stream to its home country. It will only work from there (or over a VPN exiting there). Tick "Hide geo-blocked" in the web player, or build a playlist without them:
`python3 scripts/build_playlists.py --no-geo-blocked --countries IN -o india-open.m3u`

**"Not 24/7" label.**
The channel only streams during live programming (events, sessions, news hours). Try again later.

**Works in VLC but not in the browser.**
Expected. Browsers need the stream server to send CORS headers, refuse plain `http://` video on an `https://` page, and can't play DASH `.mpd`. Use any native app from [APPS.md](APPS.md).

**The playlist is huge and my TV app is slow.**
Use a country, category or featured playlist instead of `all.m3u`. Or build a custom one:
`python3 scripts/build_playlists.py --countries US --categories news sports --min-quality 720 -o my.m3u`

**No program guide shows up.**
Add the EPG URL for your country manually ([EPG.md](EPG.md)). Guides can take a few minutes to download on first run. Channels without a `tvg-id` (a few hundred "Other" entries) have no guide data anywhere.

**Which streams actually work from my network?**
Run the checker from the device/network you watch on:
`python3 scripts/check_streams.py playlists/countries/us.m3u --write-online us-online.m3u`

**I want a channel that isn't here.**
The index only includes streams the broadcaster publishes openly. Ask in the iptv-org discussions (https://github.com/orgs/iptv-org/discussions) or add it to your own copy by appending to `scripts/curated.json` / a local m3u.

**Updating the data by hand.**
`python3 scripts/build_playlists.py --refresh` re-downloads the iptv-org database and rebuilds everything, including the web player's `channels.json`.
