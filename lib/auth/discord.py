import hashlib
from random import randint

from aiohttp import BasicAuth, ClientSession

from lib.exceptions.api import APIError
from lib.logger.logger import get_logger
from lib.settings.settings import Config, EnvConfig
from lib.utils.string_parser import insert_data

_log = get_logger(__file__, 'DiscordOAuthLogger', 'logs/discord_oauth.log')
_config = Config().get()
_env_config = EnvConfig()


class DiscordOAuth:
    redirect_url = insert_data(
        _config.auth.ds_auth_redirect_url,
        {
            'host': _config.server.host,
            'port': _config.server.port
        }
    )
    client_id = EnvConfig.CLIENT_ID
    client_secret = EnvConfig.CLIENT_SECRET
    state = hashlib.sha256(str(randint(0, 100000)).encode('utf-8')).hexdigest()
    auth_url = (
        f'https://discord.com/oauth2/authorize?'
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
            str: SHA256 hash of a random integer.
        """
        return hashlib.sha256(str(randint(0, 100000)).encode('utf-8')).hexdigest()

    async def exchange_code(self, code: str) -> str:
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
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_url,
            'code': code,
            'state': self.get_state()
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        async with ClientSession() as session:
            async with session.post('https://discord.com/api/v9/oauth2/token', data=data, headers=headers, auth=BasicAuth(self.client_id, self.client_secret)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['access_token']
                else:
                    raise APIError(f'Error exchanging code: {response.status}, \ntext: {await response.text()}\njson: {await response.json()}')
