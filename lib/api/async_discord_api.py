from aiohttp import ClientSession


class DiscordApi:
    def __init__(self) -> None:
        pass

    async def get_user_data(self, access_token: str) -> dict:
        async with ClientSession() as session:
            async with session.get('https://discord.com/api/v9/users/@me', headers={'Authorization': f'Bearer {access_token}'}) as response:
                return await response.json()