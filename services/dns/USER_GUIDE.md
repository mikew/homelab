### DNS

Powered by [Pi-hole](https://pi-hole.net)

This is an ad-blocking DNS, which also points any requests for `{{HOMELAB_BASE_DOMAIN}}` to `{{HOMELAB_HOST_LOCAL_IP}}`.

You can combine this with Tailscale to access your services from outside of your home. To do this, follow the Tailscale guide and read `{{HOMELAB_ROOT}}/services/dns/README.md`
