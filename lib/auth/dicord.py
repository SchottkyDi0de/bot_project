import hashlib
import time

from aiohttp import ClientSession
from the_retry import retry

from lib.settings.settings import Config
from lib.exceptions.api import APIError
from lib.logger.logger import get_logger

_log = get_logger(__name__, 'DiscordOAuthLogger', 'logs/discord_oauth.log')


class DiscordOAuth:
    redirect_url = 'http://188.170.203.33:80/auth'
    client_id = Config().CLIENT_ID_DEV
    client_secret = Config().CLIENT_SECRET_DEV
    state = hashlib.sha256(str(time.time()).encode()).hexdigest()
    auth_url = (
        f'https://discord.com/api/oauth2/authorize?'
        f'client_id={client_id}&'
        f'redirect_uri={redirect_url}&'
        f'response_type=code&'
        f'scope=identify&'
        f'state={state}'
    )
    def get_state(self) -> str:
        """
        Get the current state of the object.

        Returns:
            str: The SHA256 hash of the current time encoded as a hexadecimal string.
        """
        return hashlib.sha256(str(time.time()).encode()).hexdigest()

    async def exchange_code(self, code) -> str:
        """
        Exchanges an authorization code for an access token.

        Args:
            code (str): The authorization code to exchange.

        Returns:
            str: The access token.

        Raises:
            APIError: If an error occurs while exchanging the code.
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_url,
            'code': code,
            'state': self.get_state()
        }

        async with ClientSession() as session:
            async with session.post('https://discord.com/api/oauth2/token', data=data) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['access_token']
                else:
                    raise APIError(f'Error exchanging code: {response.status}')
            
