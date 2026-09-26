from config import OKTA_DOMAIN, OKTA_API_TOKEN
from typing import List, Dict, Any, Tuple
import requests
import json
import os

class OktaService:
    def __init__(self):
        self.domain = OKTA_DOMAIN
        self.client_id = os.getenv("OKTA_CLIENT_ID")
        self.client_secret = os.getenv("OKTA_CLIENT_SECRET")
        self.private_key_jwk = os.getenv("OKTA_PRIVATE_KEY")
        self.access_token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        print(f"[OktaService] Initializing with domain: {self.domain}")
        print(f"[OktaService] Client ID configured: {bool(self.client_id)}")
        print(f"[OktaService] Private key configured: {bool(self.private_key_jwk)}")
        print(f"[OktaService] Client secret configured: {bool(self.client_secret)}")

        # Try OAuth first if credentials are provided
        oauth_used = False
        if self.client_id and self.private_key_jwk:
            try:
                print("[OktaService] Attempting OAuth JWT authentication...")
                self._get_oauth_token_jwt()
                oauth_used = True
                print("[OktaService] ✓ OAuth JWT authentication successful")
            except Exception as e:
                print(f"[OktaService] ✗ OAuth JWT failed: {str(e)}")
        elif self.client_id and self.client_secret:
            try:
                print("[OktaService] Attempting OAuth client_secret authentication...")
                self._get_oauth_token()
                oauth_used = True
                print("[OktaService] ✓ OAuth client_secret authentication successful")
            except Exception as e:
                print(f"[OktaService] ✗ OAuth client_secret failed: {str(e)}")

        # Fallback to SSWS token if OAuth not used or failed
        if not oauth_used:
            if OKTA_API_TOKEN:
                self.headers["Authorization"] = f"SSWS {OKTA_API_TOKEN}"
                print("[OktaService] Using SSWS API token for authentication")
            else:
                raise Exception("No authentication method configured: provide OKTA_API_TOKEN or OAuth credentials")

    def _get_oauth_token_jwt(self):
        """Exchange client credentials for access token using private_key_jwt"""
        try:
            import time
            import uuid
            import json as json_lib
            from jwcrypto import jwk
            import jwt

            # Parse the JWK private key using jwcrypto
            key = jwk.JWK.from_json(self.private_key_jwk)
            private_key = key.get_op_key('sign')

            # Extract kid from JWK
            key_dict = json_lib.loads(self.private_key_jwk)
            kid = key_dict.get('kid')

            # Create JWT assertion
            now = int(time.time())
            assertion_payload = {
                "iss": self.client_id,
                "sub": self.client_id,
                "aud": f"{self.domain}/oauth2/v1/token",
                "exp": now + 3600,
                "iat": now,
                "jti": str(uuid.uuid4())
            }

            # Sign JWT with private key and include kid in header
            headers = {"kid": kid} if kid else {}
            client_assertion = jwt.encode(assertion_payload, private_key, algorithm="RS256", headers=headers)

            # Request token using client_credentials with JWT assertion
            # Org Authorization Server requires explicit scope matching granted Okta API Scopes
            token_url = f"{self.domain}/oauth2/v1/token"
            data = {
                "grant_type": "client_credentials",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": client_assertion,
                "scope": "okta.users.manage okta.users.read okta.groups.manage okta.groups.read"
            }

            print(f"[OAuth JWT] Requesting token from {token_url}")
            response = requests.post(token_url, data=data)
            print(f"[OAuth JWT] Token response status: {response.status_code}")
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.access_token}"
                print(f"[OAuth JWT] Token obtained successfully (length: {len(self.access_token)} chars)")
            else:
                print(f"[OAuth JWT] Token request failed: {response.text}")
                raise Exception(f"Failed to get OAuth token: {response.text}")
        except Exception as e:
            raise Exception(f"OAuth JWT error: {str(e)}")

    def _get_oauth_token(self):
        """Exchange client credentials for access token using Basic Auth"""
        try:
            import base64

            token_url = f"{self.domain}/oauth2/v1/token"

            # client_secret_basic requires Basic Auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "grant_type": "client_credentials"
            }

            response = requests.post(token_url, headers=headers, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.access_token}"
            else:
                raise Exception(f"Failed to get OAuth token: {response.text}")
        except Exception as e:
            raise Exception(f"OAuth token error: {str(e)}")

    def user_exists(self, email: str) -> Tuple[bool, str | None]:
        """Check if user exists by email. Returns (exists, user_id)"""
        try:
            url = f"{self.domain}/api/v1/users?search=profile.login eq \"{email}\""
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                users = response.json()
                if users:
                    return True, users[0].get('id')
            return False, None
        except Exception as e:
            raise Exception(f"Error checking user: {str(e)}")

    def create_user(self, user_data: Dict[str, Any]) -> Tuple[bool, str, str]:
        """Create a new user. Returns (success, user_id, message)"""
        try:
            email = user_data.get("email", "unknown")
            print(f"[create_user] Creating user: {email}")

            user_body = {
                "profile": {
                    "login": user_data.get("login"),
                    "email": user_data.get("email"),
                    "firstName": user_data.get("firstName"),
                    "lastName": user_data.get("lastName"),
                }
            }

            optional_fields = [
                "middleName", "honorificPrefix", "honorificSuffix", "title",
                "displayName", "nickName", "profileUrl", "secondEmail",
                "mobilePhone", "primaryPhone", "streetAddress", "city",
                "state", "zipCode", "countryCode", "postalAddress",
                "preferredLanguage", "locale", "timezone", "userType",
                "employeeNumber", "costCenter", "organization", "division",
                "department", "managerId", "manager"
            ]

            for field in optional_fields:
                if field in user_data and user_data[field]:
                    user_body["profile"][field] = user_data[field]

            url = f"{self.domain}/api/v1/users?activate=true"
            print(f"[create_user] POST to {url}")
            print(f"[create_user] Auth method: {'OAuth JWT' if self.access_token else 'SSWS Token'}")
            print(f"[create_user] User body: {user_body}")

            response = requests.post(url, headers=self.headers, json=user_body)
            print(f"[create_user] Response status: {response.status_code}")
            print(f"[create_user] Response headers: {dict(response.headers)}")
            print(f"[create_user] Response text length: {len(response.text)}")
            print(f"[create_user] Response text: {response.text[:500] if response.text else 'EMPTY'}")

            if response.status_code in [200, 201]:
                print(f"[create_user] Status is success, parsing JSON...")
                try:
                    user = response.json()
                    user_id = user.get('id')
                    if not user_id:
                        print(f"[create_user] ✗ No user ID in response: {user}")
                        return False, "", f"Error creating user: No user ID returned"
                    print(f"[create_user] ✓ User created: {user_id}")
                    return True, user_id, f"User {email} created successfully"
                except Exception as json_err:
                    print(f"[create_user] ✗ Failed to parse response JSON: {str(json_err)}")
                    print(f"[create_user] Response text: {response.text}")
                    return False, "", f"Error creating user: HTTP 200 but JSON parse failed: {str(json_err)}"
            else:
                # Build detailed error message including HTTP status
                error_text = response.text.strip() if response.text else ""

                # Try to parse JSON error first
                try:
                    error_json = response.json()
                    if 'errorCode' in error_json:
                        error_text = f"{error_json.get('errorCode')}: {error_json.get('errorSummary', '')}"
                    elif isinstance(error_json, dict):
                        error_text = str(error_json)
                except:
                    pass

                # If still empty, use status code
                if not error_text:
                    error_text = f"HTTP {response.status_code} - empty body"

                print(f"[create_user] ✗ Okta API error (status {response.status_code}): {error_text}")
                return False, "", f"Error creating user: [{response.status_code}] {error_text}"
        except Exception as e:
            import traceback
            error_msg = str(e).strip()
            if not error_msg:
                error_msg = f"Unknown error (exception type: {type(e).__name__}, no message)"
            tb = traceback.format_exc()
            print(f"[create_user] ✗ Exception type: {type(e).__name__}")
            print(f"[create_user] ✗ Exception: {error_msg}")
            print(f"[create_user] Traceback: {tb}")
            return False, "", f"Error creating user: {error_msg}"

    def add_user_to_group(self, user_id: str, group_id: str) -> Tuple[bool, str]:
        """Add user to group. Returns (success, message)"""
        try:
            url = f"{self.domain}/api/v1/groups/{group_id}/users/{user_id}"
            response = requests.put(url, headers=self.headers)

            if response.status_code in [200, 204]:
                return True, "User added to group successfully"
            elif response.status_code == 409:
                return True, "User already in group"
            else:
                return False, f"Error adding user to group: {response.text}"
        except Exception as e:
            error_str = str(e)
            if "already" in error_str.lower():
                return True, "User already in group"
            return False, f"Error adding user to group: {error_str}"

    def get_groups(self) -> List[Dict[str, str]]:
        """Get all groups. Returns list of {id, name}"""
        try:
            url = f"{self.domain}/api/v1/groups"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                groups = response.json()
                result = []
                for group in groups:
                    result.append({
                        "id": group.get('id'),
                        "name": group.get('profile', {}).get('name')
                    })
                return result
            else:
                error_msg = response.text if response.text else f"HTTP {response.status_code}"
                raise Exception(f"API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Error fetching groups: {str(e)}")

    def get_group_by_name(self, group_name: str) -> str | None:
        """Get group ID by name"""
        try:
            url = f"{self.domain}/api/v1/groups?search=profile.name eq \"{group_name}\""
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                groups = response.json()
                if groups:
                    return groups[0].get('id')
            return None
        except Exception as e:
            raise Exception(f"Error fetching group: {str(e)}")
