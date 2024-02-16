### File Sharing

Your media is stored in `{{env.Getenv "HOMELAB_STORAGE_PATH"}}`. You can access it directly on your homelab device, or from any device on your network that supports Windows File Sharing / Samba.

- Local Access:
  - Windows, Linux: `\\{{env.Getenv "HOMELAB_HOST_LOCAL_IP"}}`
  - Windows, Linux: `\\{{env.Getenv "HOMELAB_HOST_NAME"}}`
  - macOS, Linux: `smb://{{env.Getenv "HOMELAB_HOST_LOCAL_IP"}}`
  - macOS, Linux: `smb://{{env.Getenv "HOMELAB_HOST_NAME"}}`
