# The GoogleAuthProvider implementation has moved to the shared EventCoord
# library.  This module is retained only for backward compatibility and will
# be removed in a future release.
from EventCoord.auth.google import GoogleAuthProvider  # noqa: F401
