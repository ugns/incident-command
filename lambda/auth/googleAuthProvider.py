import os
import json
import requests
import logging
from typing import Protocol, Tuple, Optional, Dict, Any
from EventCoord.models.organizations import Organization

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GoogleAuthProvider:
    def authenticate(self, token: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        try:
            logger.info(
                f"Authenticating Google token: {token[:10]}... (truncated)")
            resp = requests.get(
                f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
            logger.info(
                f"Google tokeninfo response status: {resp.status_code}")
            if resp.status_code != 200:
                logger.warning(f"Invalid Google token: {resp.text}")
                return None, {"error": "Invalid Google token"}
            token_info = resp.json()
            logger.info(f"Token info: {json.dumps(token_info)}")
            # Lookup organization by aud
            org = Organization.get_by_aud(token_info.get('aud'))
            logger.info(
                f"Organization lookup by aud={token_info.get('aud')}: {org}")
            if not org:
                logger.warning("No organization found for this audience (aud)")
                return None, {"error": "No organization found for this audience (aud)"}
            # Standardize user info
            user_info = {
                'email': token_info.get('email'),
                'name': token_info.get('name'),
                'givenName': token_info.get('given_name'),
                'familyName': token_info.get('family_name'),
                'picture': token_info.get('picture'),
                'org_id': org.get('org_id'),
                'org_name': org.get('name'),
                # Google hosted domain
                'hd': token_info.get('hd') if token_info.get('hd') else None,
                'sub': token_info.get('sub'),
            }
            logger.info(f"User info constructed: {user_info}")
            return user_info, None
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None, {"error": "Token validation failed"}
