# auth

Adding auth to a service can be done with labels:

```yml
- traefik.http.routers.${COMPOSE_PROJECT_NAME}-service-name.middlewares=auth@file
```

You can also use HTTP Basic Auth, in case that works better for certain
services:

```yml
- traefik.http.routers.${COMPOSE_PROJECT_NAME}-service-name.middlewares=auth-basic@file
```

## Integrating

Some services can just be gated with a simple auth gate, others can use SSO. And
some have their own concept of users and cannot be integrated with the Auth
service whatsoever.

### Auth Gate

Many services have their own login, but no concept of users: the login form is
just there for very basic gating. If possible, turn off their login, and add one
of the labels given above.

#### DVR (Sonarr, Radarr, Prowlarr, etc.)

You can disable the authentication in them by editing, for example,
`services/dvr/persistent/sonarr/config/config.xml` and changing
`AuthenticationMethod` to `external`:

```xml
<AuthenticationMethod>External</AuthenticationMethod>
```

#### DNS (Pihole)

Run `pihole -a -p` to disable the password.

#### Home Automation (Home Assistant)

A custom auth provider that works with Authelia is included, but needs to be
manually defined in
`services/home-automation/persistent/homeassistant/configuration.yml`.

```yml
homeassistant:
  auth_providers:
    - type: authelia_auth
```

### SSO

#### Remote Desktop Gateway (Guacamole)

This is already set up for you.
https://www.authelia.com/integration/openid-connect/apache-guacamole/

Note: You will want to set up groups in Guacamole that are named after your auth
groups.  `admins` should be given admin privilages via a group named `admins`,
and the `users` group should be given access to any servers you want them to
access via a group named `users.

#### Notes (Outline)

This is already set up for you.

##### outline-authelia-users-yml-bridge

Outline works with OIDC, but does nothing with group information. This service
contains a bridge that will create groups in Outline from a users groups in
Authelia.

To fully enable it, you must add a webhook and get an API token.

To add the webhook, you must:

- Visit `https://notes.${HOMELAB_BASE_DOMAIN}/settings/integrations/webhooks`
- Tap "New Webhook..."
- Name it whatever you like, `outline-authelia-users-yml-bridge` makes sense
- The URL will be `https://outline-authelia-users-yml-bridge.${HOMELAB_BASE_DOMAIN}/webhook`
- Copy the Signing Secret
- Paste the Signing Secret in `outline-authelia-users-yml-bridge-env`

To get an API token, you must:

- Visit `https://notes.${HOMELAB_BASE_DOMAIN}/settings/tokens`
- Tap "New token..."
- Name it whatever you like, `outline-authelia-users-yml-bridge` makes sense
- Copy the Token
- Paste the token in `outline-authelia-users-yml-bridge-env`

#### Source Code (Gitea)

You will have to add a new Authentication Source in Gitea:

- Visit https://git.${HOMELAB_BASE_DOMAIN}/admin/auths/new
- Fill out these fields with:
  - **Authentication Name**: `Authelia`
  - **Client ID**: Grab from your `services/auth/env` file
  - **Client Secret**: Grab from your `services/auth/env` file
  - **OpenID Connect Auto Discovery URL**:
    `https://auth.${HOMELAB_BASE_DOMAIN}/.well-known/openid-configuration`
    (Remember to replace `${HOMELAB_BASE_DOMAIN}` with its proper value.)
  - **Skip Local 2FA**: Unchecked. Optional but this can be configured in
    Authelia instead.
  - **Claim name providing group names for this source**: `groups`
  - **Group Claim value for administrator users**: `admins`

#### Monitoring (Grafana)

This is already set up for you.

- The `admins` group is automatically mapped to admin privilages in Grafana.
- The `developers` group is automatically mapped to editor privilages in
  Grafana.

#### Cloud (Nextcloud)

Nextcloud is, of course, an awkward beast. The service here includes the `user_oidc` app, but it still needs to be configured. Luckily, this can be done in a somewhat automated way.

First, get into your nextcloud container:

```sh
docker exec --user www-data -it cloud-nextcloud-nextcloud-1 bash
```

Now, inside your container, run a series of commands:

```sh
# Add the Authelia OIDC Provider.
# You'll have to replace some placeholders yourself:
# - CLIENT_ID - Your Client ID for Nextcloud
# - CLIENT_SECRET - Your unhashed Client Secret for Nextcloud
# - HOMELAB_BASE_DOMAIN - Your HOMELAB_BASE_DOMAIN from `/opt/homelab/ui/homelab-shell-env-debug`
./occ \
  user_oidc:provider \
  Authelia \
  "--clientid=CLIENT_ID" \
  "--clientsecret=CLIENT_SECRET" \
  "--discoveryuri=https://auth.HOMELAB_BASE_DOMAIN/.well-known/openid-configuration" \
  "--scope=openid email profile groups" \
  --mapping-uid=preferred_username \
  --unique-uid=0

# Set up group group provisioning on Authelia.
PROVIDER_NAME=Authelia
PROVIDER_ID=$(./occ user_oidc:provider --output json "$PROVIDER_NAME" | python -c 'import json; p = json.loads(input()); print(p["id"])')
./occ \
  config:app:set \
  user_oidc \
  "provider-${PROVIDER_ID}-groupProvisioning" \
  --value 1

# Redirect to Authelia on login page.
./occ \
  config:app:set \
  user_oidc \
  allow_multiple_user_backends \
  --value=0
```
