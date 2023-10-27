# homelab

This is my collection of services I've been adding to for years. It's using docker-compose as the sweet spot for orchestration.

I've used this to self-host my services for almost a decade. I've also used it to build "set top boxes" for people, complete with user guides and tools to help them administer them.

## Requirements

- `docker`
- `docker-compose`
- One folder for "storage". That is, one folder to be shared with most containers, containing all of your music, movies, tv shows, and downloads.
- A domain with [DNS supported by Traefik](https://doc.traefik.io/traefik/https/acme/#providers)

## Getting Started

Homelab expects to live at `/opt/homelab`. It's not a hard requirement, only some of the "user helpers" reference this path.

```sh
sudo mkdir /opt/homelab
sudo chown "$UID:$GID" /opt/homelab
git clone https://github.com/mikew/homelab /opt/homelab
```

After this, you need to set up your "homelab shell environment". These are a bunch of environment variables that are injected when starting any service. They really, really help with repetition and making it easier to do homelab-wide changes.

```sh
cp /opt/homelab/bin/homelab-shell-env-example /opt/homelab/bin/homelab-shell-env
"${EDITOR:-nano}" /opt/homelab/bin/homelab-shell-env
```

To easily list the homelab shell environment, run:

```sh
/opt/homelab/ui/homelab-shell-env-debug
```

## Before running any and all services

- Review the `docker-compose.yml` so you know what it entails.
- If there's a file named `env-example`, your to copy its contents to `env` and set any variable accordingly. Mostly they're just used to keep secrets out of the repository.
- If there's a `README.md`, read it.
- If there's a `USER_GUIDE.md`, there might be some fun things to learn in there.

## Running Services (when evaluating)

After you've reviewed the service, and made any edits you need to, you need to evaluate it.

Because of the "homelab shell environment", you can't just run `docker-compose up`. There's a helper for that:

```sh
/opt/homelab/bin/docker-compose-up
```

So, if you wanted to try running the reverse proxy, you would:

```sh
cd /opt/homelab/services/reverse-proxy
/opt/homelab/bin/docker-compose-up
```

Then, you can start another service that uses the reverse proxy, like the DVR:

```sh
cd /opt/homelab/services/dvr
/opt/homelab/bin/docker-compose-up
```

To be honest, I've used `tmux` to help me "evaluate" services for _months_ at a time before turning them into systemd services.

You can use the general `docker-compose` helper to inject the homelab shell environment to various `docker-compose` commands:

```sh
cd /opt/homelab/services/home-automation
/opt/homelab/bin/docker-compose run --rm homeassistant sh
```

## Running Services

Once you've evaluated the services, you can easily add them as systemd services. I prefer using that as it gives another layer of orchestration, and I find `journalctl` better for viewing logs than `docker logs`.

```sh
cd /opt/homelab
./bin/copy-systemd-files
```

This will create a bunch of systemd services named something like `homelab.SERVICE_NAME.service`, so you can do things like:

```sh
sudo systemctl restart homelab.home-theatre.service
journalctl -f -u homelab.home-theatre.service
```

# Notes

## Updating Services

The `docker-compose-up` script runs both `docker-compose pull` and `docker-compose build --pull`, so, any service will be up to date when it starts.

There's also a helper that will restart all homelab services:

```sh
/opt/homelab/ui/update-services
```

## Organization

### Naming

I like to name services after their purpose, not what provides them. That's why you see things like:

- source-code instead of gitlab / gitea
- home-automation instead of home assistant
- dns instead of pihole

Some things, I just couldn't find a good name for. Soulseek? "Music downloader" somehow seemed way too verbose.

There's also others I just couldn't figure out a name for. Tailscale, it's _like_ a vpn, but maybe not in everyone's understanding of it.

### Persistent storage

I like to keep things close to the source. So, rather than using docker volumes, if a service needs storage it's stored inside the service directory at `./persistent`.

## Adding new services, or modifying existing ones

They're just docker compose files, so add or edit anything you'd like.

### Reverse proxy

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

### Hooks

Because some services need some folders / files created _just right_, or because you can't bind mount a folder where you need, the `docker-compose-up` also runs "hooks" before and after each stage. The scripts live in a folder named `./script` in any service directory, named after any of the hooks:

- `pre-pull`
- `post-pull`
- `pre-build`
- `post-build`
- `pre-up`
- `post-up`

### Documentation

Keep "techy general setup" in `README.md`, and any `USER_GUIDE.md` file will be rolled up in the `documentation` service.

This generates a .md file at `/opt/homelab/ui/Homelab User Guide.md`, and a corresponding .html file. All IPs, host name, domain names, any of the homelab shell environment variables will be replaced with their actual values, so links actually work for people.

## Permissions

I've done what I can over the years but sometimes you still gotta `sudo` to edit files.
