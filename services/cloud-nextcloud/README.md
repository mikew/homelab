# cloud

This actually goes against the "one storage path" a bit. The main storage folder is provided, as you can use Nextcloud's "external storage" to make that folder accessible anywhere.

But the "cloud storage" is expected to be "${HOMELAB_STORAGE_PATH}/../cloud". The idea is you don't want your personal cloud data accidentally leaking to anything.

To do this, my "storage" folder actually looks like...

```
/storage
├── backup
├── cloud
├── storage
│   ├── games
│   ├── roms
│   ├── software
│   ├── downloads
│   ├── tv
│   └── movies
```

... and my `HOMELAB_STORAGE_PATH` is `/storage/storage`.
