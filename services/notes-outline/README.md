# Notes

## outline-authelia-users-yml-bridge

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
