"""
This requires an AuthRequest Authz Endpoint with a CookieSession auth strategy
present in your Authelia config:
https://www.authelia.com/configuration/miscellaneous/server-endpoints-authz/#configuration

Add this to your Home Assistant `configuration.yml`:

```yml
homeassistant:
  auth_providers:
    - type: authelia_auth
      # authelia_base_url: https://auth.example.com
      # authelia_cookie_name: authelia_session
      # authelia_auth_request_route: /api/authz/auth-request
      # require_authelia_session_cookie: true
      # group_admin: admins
      # group_read_only: read-only
```
"""

from typing import Any, TypedDict
import logging

import aiohttp
import voluptuous as vol

from homeassistant.auth.providers import (
    AUTH_PROVIDER_SCHEMA,
    AUTH_PROVIDERS,
    AuthProvider,
    LoginFlow,
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.auth.models import Credentials, UserMeta
from homeassistant.auth.const import (
    GROUP_ID_ADMIN,
    GROUP_ID_USER,
    GROUP_ID_READ_ONLY,
)

_LOGGER = logging.getLogger(__name__)

CONF_AUTHELIA_BASE_URL = "authelia_base_url"
CONF_AUTHELIA_COOKIE_NAME = "authelia_cookie_name"
CONF_AUTHELIA_AUTH_REQUEST_ROUTE = "authelia_auth_request_route"
CONF_REQUIRE_AUTHELIA_SESSION_COOKIE = "require_authelia_session_cookie"
CONF_GROUP_ADMIN = "group_admin"
CONF_GROUP_READ_ONLY = "group_read_only"

CONFIG_SCHEMA = AUTH_PROVIDER_SCHEMA.extend(
    {
        vol.Optional(CONF_AUTHELIA_BASE_URL, default=""): str,
        vol.Optional(CONF_AUTHELIA_COOKIE_NAME, default="authelia_session"): str,
        vol.Optional(CONF_AUTHELIA_AUTH_REQUEST_ROUTE, default="/api/authz/auth-request"): str,
        vol.Optional(CONF_REQUIRE_AUTHELIA_SESSION_COOKIE, default=True): bool,
        vol.Optional(CONF_GROUP_ADMIN, default="admins"): str,
        vol.Optional(CONF_GROUP_READ_ONLY, default="read-only"): str,
    }
)


class AutheliaUserInfo(TypedDict):
    user_name: str
    full_name: str
    email: str
    groups: list[str]


class AuthealiaAuthLoginFlowContext(TypedDict):
    authelia_base_url: str
    authelia_cookie_name: str
    authelia_auth_request_route: str
    require_authelia_session_cookie: bool
    user_info: AutheliaUserInfo | None
    authelia_session_cookie: str
    home_assistant_external_url: str


@AUTH_PROVIDERS.register("authelia_auth")
class AutheliaAuthProvider(AuthProvider):
    DEFAULT_TITLE = "Authelia"

    _authelia_user_info_cache: dict[str, AutheliaUserInfo] = {}

    async def async_login_flow(self, context: dict[str, Any] | None) -> LoginFlow:
        """Return a flow to login."""

        if context is None:
            raise Exception("Context not passed to async_login_flow")

        # Accesing request via context requires a patch.
        request = context.get("request")
        if request is None:
            raise Exception("no request in context")

        remote_user = request.headers.get("remote-user")
        remote_name = request.headers.get("remote-name")
        remote_groups = parse_authelia_groups_header(
            request.headers.get("remote-groups")
        )
        remote_email = request.headers.get("remote-email")

        authelia_base_url = self.config[CONF_AUTHELIA_BASE_URL]
        authelia_cookie_name = self.config[CONF_AUTHELIA_COOKIE_NAME]
        authelia_auth_request_route = self.config[CONF_AUTHELIA_AUTH_REQUEST_ROUTE]
        require_authelia_session_cookie = self.config[
            CONF_REQUIRE_AUTHELIA_SESSION_COOKIE
        ]

        if require_authelia_session_cookie and not authelia_base_url:
            raise Exception(
                "authelia_base_url must be set when require_authelia_session_cookie is on"
            )

        authelia_auth_login_flow_context: AuthealiaAuthLoginFlowContext = {
            "authelia_base_url": authelia_base_url,
            "authelia_cookie_name": authelia_cookie_name,
            "authelia_auth_request_route": authelia_auth_request_route,
            "require_authelia_session_cookie": require_authelia_session_cookie,
            "user_info": None,
            "authelia_session_cookie": request.cookies.get(authelia_cookie_name, ""),
            "home_assistant_external_url": self.hass.config.external_url,
        }

        if remote_user and remote_name:
            authelia_auth_login_flow_context["user_info"] = {
                "user_name": remote_user,
                "full_name": remote_name,
                "groups": remote_groups,
                "email": remote_email,
            }

        return AuthealiaAuthLoginFlow(self, authelia_auth_login_flow_context)

    async def async_get_or_create_credentials(
        self, user_info: AutheliaUserInfo
    ) -> Credentials:
        """Get credentials based on the flow result."""
        self._authelia_user_info_cache[user_info["user_name"]] = user_info
        username = user_info["user_name"]

        if not username:
            raise Exception(
                "No username in flow_result passed to async_get_or_create_credentials"
            )

        for credential in await self.async_credentials():
            if credential.data["username"] == username:
                return credential

        return self.async_create_credentials(
            {
                "username": username,
            }
        )

    async def async_user_meta_for_credentials(
        self, credentials: Credentials
    ) -> UserMeta:
        """Return extra user metadata for credentials.

        Currently, supports name, group and local_only.
        """
        user_info = self._authelia_user_info_cache.get(credentials.data["username"])

        if not user_info:
            raise Exception(
                f"AutheliaUserInfo for {credentials.data['username']} not in cache"
            )

        resolved_group = GROUP_ID_USER
        conf_group_admin = self.config[CONF_GROUP_ADMIN]
        conf_group_read_only = self.config[CONF_GROUP_READ_ONLY]

        if conf_group_admin and conf_group_admin in user_info["groups"]:
            resolved_group = GROUP_ID_ADMIN

        if conf_group_read_only and conf_group_read_only in user_info["groups"]:
            resolved_group = GROUP_ID_READ_ONLY

        return UserMeta(
            name=user_info["full_name"],
            is_active=True,
            group=resolved_group,
            local_only=False,
        )


class AuthealiaAuthLoginFlow(LoginFlow):
    """Handler for the login flow."""

    def __init__(
        self,
        auth_provider: AutheliaAuthProvider,
        authelia_auth_login_flow_context: AuthealiaAuthLoginFlowContext,
    ):
        """Initialize the login flow"""
        super().__init__(auth_provider)
        self._authelia_auth_login_flow_context = authelia_auth_login_flow_context

    async def async_step_init(
        self,
        user_input: dict[str, str] | None = None,
    ) -> FlowResult:
        """Handle the step of the form."""
        if self._authelia_auth_login_flow_context["user_info"] is None:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({}),
                errors={"base": "invalid_auth"},
            )

        try:
            if self._authelia_auth_login_flow_context[
                "require_authelia_session_cookie"
            ]:
                await validate_authelia_session(self._authelia_auth_login_flow_context)

            return await self.async_finish(
                self._authelia_auth_login_flow_context["user_info"]
            )
        except:
            _LOGGER.exception("Error")
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({}),
                errors={"base": "invalid_auth"},
            )


def parse_authelia_groups_header(groups: str | None):
    groups_list: list[str] = groups.split(",") if groups else []

    return groups_list


async def validate_authelia_session(
    authelia_auth_login_flow_context: AuthealiaAuthLoginFlowContext,
):
    user_info = authelia_auth_login_flow_context["user_info"]

    if not user_info:
        raise Exception("No user_info passed to validate_authelia_session")

    headers = {
        "Cookie": f'{authelia_auth_login_flow_context["authelia_cookie_name"]}={authelia_auth_login_flow_context["authelia_session_cookie"]}',
        "X-Original-Method": "GET",
        "X-Original-URL": authelia_auth_login_flow_context[
            "home_assistant_external_url"
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{authelia_auth_login_flow_context['authelia_base_url']}{authelia_auth_login_flow_context['authelia_auth_request_route']}",
            headers=headers,
        ) as response:
            if response.status >= 400:
                raise Exception("Could not validate authelia_session")

            remote_user = response.headers.get("remote-user")
            remote_name = response.headers.get("remote-name")
            remote_groups = parse_authelia_groups_header(
                response.headers.get("remote-groups")
            )
            remote_email = response.headers.get("remote-email")

            if (
                remote_user != user_info["user_name"]
                or remote_name != user_info["full_name"]
                or remote_groups != user_info["groups"]
                or remote_email != user_info["email"]
            ):
                raise Exception("User info does not match")
