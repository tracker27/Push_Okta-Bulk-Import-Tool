import os
from dotenv import load_dotenv

load_dotenv()

OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
OKTA_API_TOKEN = os.getenv("OKTA_API_TOKEN", "")  # Optional if using OAuth

if not OKTA_DOMAIN:
    raise ValueError("OKTA_DOMAIN environment variable must be set")

# Credentials gating access to this tool's own API (not Okta credentials).
# Required so the backend isn't reachable by anyone who can hit the port -
# without this, any user creation / group management endpoint is wide open.
APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

if not APP_USERNAME or not APP_PASSWORD:
    raise ValueError(
        "APP_USERNAME and APP_PASSWORD must be set in .env - they protect "
        "this tool's endpoints from unauthenticated access."
    )

# Groups this tool should never list or let someone add users to - e.g. the
# org-wide "Everyone" group and any admin group, since a bulk CSV import is
# not how membership in those should ever change. Comma-separated, exact
# (case-insensitive) group name match.
EXCLUDED_GROUPS = set(
    name.strip().lower()
    for name in os.getenv("EXCLUDED_GROUPS", "Everyone,Okta Administrators").split(",")
    if name.strip()
)
