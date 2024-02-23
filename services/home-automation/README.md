# home-automation

The `docker-compose.yml` file forwards some of the homelab environment variables to the container. You can use these in a `configuration.yaml` like so:

```yml
group: !include groups.yaml
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

http:
  use_x_forwarded_for: true
  cors_allowed_origins:
    - !env_var EXTERNAL_URL
  trusted_proxies:
    # local network
    - !env_var HOMELAB_LAN_CIDR
    # docker containers
    - 172.16.0.0/12

homeassistant:
  external_url: !env_var EXTERNAL_URL
  internal_url: !env_var INTERNAL_URL
  time_zone: !env_var TZ
```

## Authelia Auth

While Home Assistant doesn't support SSO, it can be integrated with any authentication backend. One for Authelia is included, but needs to be added to your `configuration.yaml`:

```yml
homeassistant:
  auth_providers:
    - type: command_line
      meta: true
      command: /authelia-auth
      args:
        - --authelia-base
        - !env_var AUTHELIA_BASE
        - --authelia-home-assistant-domain
        - !env_var AUTHELIA_HOME_ASSISTANT_DOMAIN
```
