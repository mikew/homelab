## Services

{{HOMELAB_USER_GUIDES}}

## FAQ

**Q. How can I find my local IP?**

A. Tap the "Homelab Info" icon on your desktop. You will see a bunch of information about your device.

**Q. Updating Services**

A. When your device restarts it will update all the services mentioned in this document. If you would like to update without restarting, tap "Upgrade Services" on your desktop.

**Q. How can I access these services from anywhere?**

A. Your device is set up to be accessible at https://{{HOMELAB_BASE_DOMAIN}}. Initially, you won't be able to access this address. To do this, you will need to either forward these ports ...

- `80 -> {{HOMELAB_HOST_LOCAL_IP}}`
- `443 -> {{HOMELAB_HOST_LOCAL_IP}}`

Or follow the Tailscale + DNS guides.
