### File Sharing

Your media is stored in `/storage`. You can access it directly on your homelab device, or from any device on your network that supports Windows File Sharing / Samba.

- Local Access:
  - Windows, Linux: `\\{{HOMELAB_HOST_LOCAL_IP}}`
  - Windows, Linux: `\\{{HOMELAB_HOST_NAME}}`
  - macOS, Linux: `smb://{{HOMELAB_HOST_LOCAL_IP}}`
  - macOS, Linux: `smb://{{HOMELAB_HOST_NAME}}`
