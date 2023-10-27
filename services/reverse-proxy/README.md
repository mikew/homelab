# reverse-proxy

This will use Route53 for the ACME DNS challenge. To see what permissions are
needed, refer to [the DNS challenge providers of
Traefik](https://doc.traefik.io/traefik/https/acme/#providers)

To use a different provider, change the `--certificatesresolvers.letsencrypt.acme.dnschallenge.provider=` line in `docker-compose.yml`.
