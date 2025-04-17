from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.jwk import construct
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8080/realms/zip-checker/protocol/openid-connect/token"
)
KEYCLOAK_URL = "http://keycloak:8080/realms/zip-checker/protocol/openid-connect/certs"

async def verify_token(token: str = Depends(oauth2_scheme)):
    logger.info(f"Verifying token: {token[:10]}...")
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Fetching JWKS from {KEYCLOAK_URL}")
            response = await client.get(KEYCLOAK_URL, timeout=10.0)
            logger.info(f"JWKS response: {response.status_code}, content: {response.text}")
            response.raise_for_status()
            jwks = response.json()

        public_key = None
        for key in jwks["keys"]:
            if key["alg"] == "RS256":
                public_key = construct(key).to_pem().decode()
                break

        if not public_key:
            logger.error("No RS256 key found in JWKS")
            raise HTTPException(status_code=401, detail="Invalid token")

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer="http://localhost:8080/realms/zip-checker",
            options={"verify_aud": False}
        )
        logger.info("Token verified successfully")
        return payload
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while fetching JWKS: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Auth error: {str(e)}")
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error during auth: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail=f"Auth error: {str(e)}")