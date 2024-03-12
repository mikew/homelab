### Movie DVR

Powered by [Radarr][radarr-docs]

- Link: https://moviedvr.{{env.Getenv "HOMELAB_BASE_DOMAIN"}}

The idea behind this is you search for a movie, select the desired quality, and that's it. Radarr will periodically search for any missing movies and download them.

![Radarr Add Movie](https://user-images.githubusercontent.com/4729/210125492-4d0c069c-78a1-413b-a5e5-5efd6ac52be8.png)

You can also connect with other apps, for example if you use Trackt, Plex's Watchlist, or IMDB lists to track movies you'd like to watch. That way you'll only need to add movies to that list and they will be downloaded.

Once a download is complete, Radarr will move and rename the files for you, and your home theatre library will update.

### TV DVR

Powered by [Sonarr][sonarr-docs]

- Link: https://tvdvr.{{env.Getenv "HOMELAB_BASE_DOMAIN"}}

The idea behind this is you add a movie to a list, select the desired quality, and that's it. Sonarr will periodically search for any missing episodes and download them.

![Sonarr Add Show](https://user-images.githubusercontent.com/4729/210187766-17b31e1c-9569-4523-9aaf-d8de104741da.png)

You can also connect with lists, for example if you use Trackt, Plex's Watchlist, or IMDB lists. That way you'll only need to add TV shows to that list and they will be downloaded.

Once a download is complete, Radarr will move and rename the files for you, and your home theatre library will update.

### Torrent Search

Powered by [Prowlarr][prowlarr-docs]

- Link: https://torrentsearch.{{env.Getenv "HOMELAB_BASE_DOMAIN"}}

This is a multi-torrent-site search engine, it's pretty straightforward. Type something in the search bar, press enter. You'll see a list of results, the categories, and how many seeds / peers are available. If you press the download icon, the torrent will be immediately added to your torrent client.

![Prowlarr Search](https://user-images.githubusercontent.com/4729/210187763-2ff992c2-6ffe-4b82-bfab-dc40dabb3ec8.png)

The various DVRs use this in the background to find what's available to download.

### Torrents

Powered by [Transmission][transmission-homepage]

- Link: https://torrents.{{env.Getenv "HOMELAB_BASE_DOMAIN"}}

This is your torrent download client. Typically you don't interact with it very much: downloads should be added from the DVRs, or directly from your torrent search engine (nothing is stopping you from adding your own torrents if you want).

![Transsmission](https://user-images.githubusercontent.com/4729/210187767-086b7e2a-c89a-4b87-b73a-7f13c3a8e478.png)

You won't have to interact with this very much. Most of your downloads will be started automatically by the DVR, and you download directly in your torrent search app. However, it still helps to access this to do any maintenance or change settings.

[radarr-docs]: https://wiki.servarr.com/radarr
[sonarr-docs]: https://wiki.servarr.com/en/sonarr
[prowlarr-docs]: https://wiki.servarr.com/en/prowlarr
[transmission-homepage]: https://transmissionbt.com/
