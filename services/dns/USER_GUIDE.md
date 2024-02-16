### DNS

Powered by [Pi-hole](https://pi-hole.net)

- External Access: https://dns.{{env.Getenv "HOMELAB_BASE_DOMAIN"}}

This is an ad-blocking DNS, which also points any requests for `{{env.Getenv "HOMELAB_BASE_DOMAIN"}}` to `{{env.Getenv "HOMELAB_HOST_LOCAL_IP"}}`.

You can combine this with Tailscale to access your services from outside of your home. To do this, follow the Tailscale guide and read `{{env.Getenv "HOMELAB_ROOT"}}/services/dns/README.md`
