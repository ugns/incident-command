import os
import ldclient
from ldclient.context import Context
from ldclient.config import Config

ldclient.set_config(Config(os.environ.get(
    'LAUNCHDARKLY_SDK_KEY', '')))  # SDK key from env
ld_client = ldclient.get()


class Flags:
    def __init__(self, user):
        user_ctx = (
            Context.builder(user.get("email") or user.get("sub"))
            .kind('user')
            .set('name', user.get("name"))
            .set('email', user.get("email"))
            .set('sub', user.get("sub"))
            .set('org_id', user.get("org_id"))
            .set('org_name', user.get("org_name"))
            .build()
        )
        org_ctx = (
            Context.builder(user.get("org_id"))
            .kind('organization')
            .set('name', user.get("org_name"))
            .set('org_id', user.get("org_id"))
            .build()
        )
        self.multi_ctx = (
            Context.multi_builder()
            .add(user_ctx)
            .add(org_ctx)
            .build()
        )

    def has_super_admin_access(self):
        if not ld_client or not ld_client.is_initialized():
            return False

        return ld_client.variation("super-admin-access", self.multi_ctx, False)

    def has_admin_access(self):
        if not ld_client or not ld_client.is_initialized():
            return False

        return ld_client.variation("admin-access", self.multi_ctx, False)
