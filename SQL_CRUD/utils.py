"""Import fastapi's tools"""
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import httpx
from jose import jwt, JWTError

from config import get_settings

settings = get_settings()

AUTH0_DOMAIN = settings.auth0_domain
AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_CLIENT_ID = settings.auth0_client_id
AUTH0_CLIENT_SECRET = settings.auth0_client_secret
AUTH0_CALLBACK_URL = settings.auth0_callback_url
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_API_AUDIENCE = settings.auth0_api_audience


class AuthMiddleware(BaseHTTPMiddleware):
    """Definition of middleware that should be added"""

    def __init__(self, app, auth0_domain, client_id, audience, algorithms):
        super().__init__(app)
        self.auth0_domain = auth0_domain
        self.client_id = client_id
        self.audience = audience
        self.algorithms = algorithms
        self.jwks = self.get_jwks()

    def get_jwks(self):
        """Returns the Identity Server's public key set in the JWKS format."""
        response = httpx.get(f"https://{self.auth0_domain}/.well-known/jwks.json")
        return response.json()

    async def decode_token(self, token: str, id_token: bool = False):
        """Try to decode the token to verify connection

        Args:
            token (str): token to decode
            id_token (bool, optional): Defaults to False.

        Raises:
            HTTPException: Raises if nothing in rsa_keys
            HTTPException: Raises if something went wrong during decoding

        Returns:
            returns payload
        """
        unverified_header = jwt.get_unverified_header(token)
        rsa_keys = [
            key for key in self.jwks["keys"] if key["kid"] == unverified_header["kid"]
        ]
        audience = self.audience if not id_token else self.client_id
        if not rsa_keys:
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            payload = jwt.decode(
                token, rsa_keys[0], algorithms=self.algorithms, audience=audience
            )
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def dispatch(self, request: Request, call_next):
        """Dispatch function, sets connection or redirects user
        Returns:
            Response or redirection link
        """
        if request.url.path == "/callback":
            response = await call_next(request)
            return response
        if "authorization" in request.headers:
            token = request.headers.get("authorization").split("Bearer ")[-1]
            try:
                await self.decode_token(token)
                response = await call_next(request)
                return response
            except HTTPException:
                pass
        redirect_url = (
            f"{AUTH0_AUTHORIZE_URL}?response_type=code&client_id={self.client_id}"
        )
        redirect_url += f"&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid profile email"
        redirect_url += f"&audience={AUTH0_API_AUDIENCE}"
        return RedirectResponse(url=redirect_url)


async def exchange_code_for_token(code: str):
    """Trying to exchange code for token

    Args:
        code (str): code to work with

    Returns:
        json object with token
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            AUTH0_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "client_id": AUTH0_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "code": code,
                "redirect_uri": AUTH0_CALLBACK_URL,
                "audience": AUTH0_API_AUDIENCE,
            },
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.json()}
