import os
import ldclient
from ldclient.context import Context
from ldclient.config import Config

ldclient.set_config(Config(os.environ.get(
    'LAUNCHDARKLY_SDK_KEY', '')))  # SDK key from env
ld_client = ldclient.get()


class Flags:
  @staticmethod
  def has_admin_access(user):
      if not ld_client or not ld_client.is_initialized():
          return False

      user_ctx = (
          Context.builder(user.get("email") or user.get("sub"))
          .kind('user')
          .set('email', user.get("email"))
          .build()
      )
      org_ctx = (
          Context.builder(user.get("org_id"))
          .kind('organization')
          .set('org_id', user.get("org_id"))
          .build()
      )
      multi_ctx = (
          Context.multi_builder()
          .add(user_ctx)
          .add(org_ctx)
          .build()
      )
      return ld_client.variation("admin-access", multi_ctx, False)
