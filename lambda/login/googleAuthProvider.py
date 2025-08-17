import logging
import time
import requests
import json
from authlib.jose import JsonWebToken, JWTClaims
from typing import Tuple, Optional, Dict, Any
from EventCoord.models.organizations import Organization

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
valid_auds = [org['aud']
              for org in Organization.list_all() if 'aud' in org]
logger.debug(f"Valid audiences (aud): {valid_auds}")


class GoogleAuthProvider:
    def validate_google_id_token(self, token: str) -> Optional[JWTClaims]:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Validating Google ID token: {token[:10]}... (truncated)")
                resp = requests.get(JWKS_URL, timeout=5)
                logger.debug("JWKS endpoint responded")
                resp.raise_for_status()
                logger.debug("JWKS response status OK")
                jwks = resp.json()['keys']
                logger.debug(f"JWKS keys: {jwks}")
                jwt_obj = JsonWebToken(['RS256'])
                logger.debug("About to decode JWT")
                claims = jwt_obj.decode(
                    token,
                    jwks,
                    claims_options={
                        "iss": {
                            "essential": True,
                            "values": ['accounts.google.com', 'https://accounts.google.com']
                        },
                        "aud": {
                            "essential": True,
                            "values": valid_auds
                        }
                    }
                )
                logger.debug("Decoded JWT, about to validate")
                claims.validate(now=int(time.time()), leeway=3)
                logger.info(f"Google ID token is valid: {claims}")
                return claims
            except Exception as e:
                logger.error(f"Google ID token validation failed: {e}")
                if attempt == max_retries:
                    logger.error("Max retries reached")
                    return None
                time.sleep(0.5 * attempt)

    def authenticate(self, token: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        try:
            logger.info(
                f"Authenticating Google token: {token[:10]}... (truncated)")
            token_info = self.validate_google_id_token(token)
            if not token_info:
                logger.warning("Invalid Google token")
                return None, {"error": "Invalid Google token"}
            logger.info(f"Token info: {json.dumps(token_info)}")
            # Lookup organization by aud
            aud = token_info.get('aud')
            if not isinstance(aud, str) or not aud:
                logger.warning("Missing or invalid 'aud' in token")
                return None, {"error": "Missing or invalid audience (aud) in token"}
            org = Organization.get_by_aud(aud)
            if not org:
                logger.warning("No organization found for this audience (aud)")
                return None, {"error": "No organization found for this audience (aud)"}
            logger.info(f"Organization lookup by aud={aud}: {org}")
            # Standardize user info
            user_info = {
                'sub': token_info.get('sub'),
                'email': token_info.get('email'),
                'name': token_info.get('name'),
                'givenName': token_info.get('given_name'),
                'familyName': token_info.get('family_name'),
                'picture': token_info.get('picture'),
                'org_id': org.get('org_id'),
                'org_name': org.get('name'),
                # Google hosted domain
                'hd': token_info.get('hd') if token_info.get('hd') else None,
            }
            logger.info(f"User info constructed: {user_info}")
            return user_info, None
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None, {"error": "Token validation failed"}
