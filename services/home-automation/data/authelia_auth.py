from typing import Any, cast, TypedDict
import logging

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

CONF_GROUP_ADMIN = 'group_admin'
CONF_GROUP_READ_ONLY = 'group_read_only'

CONFIG_SCHEMA = AUTH_PROVIDER_SCHEMA.extend({
    vol.Optional(CONF_GROUP_ADMIN, default='admins'): str,
    vol.Optional(CONF_GROUP_READ_ONLY, default='read-only'): str,
})


class AutheliaUserInfo(TypedDict):
    user_name: str
    full_name: str
    email: str
    groups: list[str]


@AUTH_PROVIDERS.register("authelia_auth")
class AutheliaAuthProvider(AuthProvider):
    DEFAULT_TITLE = "Authelia"

    _authelia_user_info_cache: dict[str, AutheliaUserInfo] = {}

    async def async_login_flow(self, context: dict[str, Any] | None) -> LoginFlow:
        """Return a flow to login."""

        if context is None:
            raise Exception("Context not passed to async_login_flow")

        # Accesing request via context requires a patch.
        request = context.get('request')
        if request is None:
            raise Exception('no request in context')

        remote_user = request.headers.get('remote-user')
        remote_name = request.headers.get('remote-name')
        remote_groups = request.headers.get('remote-groups')
        remote_email = request.headers.get('remote-email')

        user_info: AutheliaUserInfo | None = None

        if remote_user and remote_name:
            groups: list[str] = remote_groups.split(",") if remote_groups else []

            user_info = {
                "user_name": remote_user,
                "full_name": remote_name,
                "groups": groups,
                "email": remote_email,
            }

        return AuthealiaAuthLoginFlow(self, user_info)

    async def async_get_or_create_credentials(
        self, user_info: AutheliaUserInfo
    ) -> Credentials:
        """Get credentials based on the flow result."""
        self._authelia_user_info_cache[user_info["user_name"]] = user_info
        username = user_info["user_name"]

        if not username:
            raise Exception('No username in flow_result passed to async_get_or_create_credentials')

        for credential in await self.async_credentials():
            if credential.data["username"] == username:
                return credential

        return self.async_create_credentials({
            "username": username,
        })

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

        if conf_group_admin and conf_group_admin in user_info['groups']:
            resolved_group = GROUP_ID_ADMIN

        if conf_group_read_only and conf_group_read_only in user_info['groups']:
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
        user_info: AutheliaUserInfo | None,
    ):
        """Initialize the login flow"""
        super().__init__(auth_provider)
        self._user_info = user_info

    async def async_step_init(
        self,
        user_input: dict[str, str] | None = None,
    ) -> FlowResult:
        """Handle the step of the form."""
        if self._user_info is None:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({}),
                errors={'base': 'invalid_auth'},
            )

        try:
            return await self.async_finish(self._user_info)
        except:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({}),
                errors={'base': 'invalid_auth'},
            )
