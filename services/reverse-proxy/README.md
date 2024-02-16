# reverse-proxy

This will use Route53 for the ACME DNS challenge. To see what permissions are
needed, refer to [the DNS challenge providers of
Traefik](https://doc.traefik.io/traefik/https/acme/#providers)

To use a different provider, change the `--certificatesresolvers.letsencrypt.acme.dnschallenge.provider=` line in `docker-compose.yml`.

To integrate with the reverse proxy, you'll need to use the reverse proxy network, and add some labels:

```yml
version: "2"

services:
  SOME_SERVICE:
    networks:
      - default
      - reverse-proxy
    labels:
      - traefik.enable=true
      - traefik.http.routers.${COMPOSE_PROJECT_NAME}-SOME_SERVICE.rule=Host(`SOME_SERVICE.${HOMELAB_BASE_DOMAIN}`)
      - traefik.http.routers.${COMPOSE_PROJECT_NAME}-SOME_SERVICE.entrypoints=web,websecure
      # If traefik doesn't detect the port you might need this.
      # - traefik.http.services.${COMPOSE_PROJECT_NAME}-SOME_SERVICE.loadbalancer.server.port=80

networks:
  reverse-proxy:
    external: true
```
