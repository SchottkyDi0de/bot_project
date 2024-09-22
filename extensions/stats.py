from uuid import uuid4
from typing import TYPE_CHECKING

from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InlineQueryResultCachedPhoto

from lib.settings.settings import Config
from lib.utils.nickname_handler import handle_nickname
from lib.utils.validators import validate

from extensions.setup import ExtensionsSetup
from ex_func import StatsFunc
from lib.database.players import PlayersDB
from lib import (API, CooldownStorage, HookExceptions, MissingArgumentsError, Text,
                    CommonImageGen, Activities, analytics, parse_message, multi_accounts, check)

if TYPE_CHECKING:
    from aiogram import Bot, Router
    from aiogram.types import Message, InlineQuery

_config = Config().get()


class Stats(ExtensionsSetup):
    __funcs_filters__ = [
        ("stats", (Command("stats"),)),
    ]

    def init(self):
        self.pdb = PlayersDB()
        self.api = API()
        self.img_gen = CommonImageGen()
    
    def __extend_router__(self, router: 'Router'):
        router.inline_query.register(self.inline_stats)
    
    @HookExceptions().hook()
    @check(in_db=False)
    @CooldownStorage.cooldown(10, "gen_stats")
    @multi_accounts("stats_macc", "send_photo")
    @Activities.upload_photo
    @analytics("stats")
    @parse_message(max_args=2, min_args=0)
    async def stats(self, msg: 'Message', splitted_message: list[str], bot: 'Bot', **_):
        member = await self.pdb.check_member_exists(msg.from_user.id, get_if_exist=True, raise_error=False)
        member = member if member else None

        if len(splitted_message) == 2:
            region = splitted_message[1]
            nickname = splitted_message[0]
            composite_nickname = handle_nickname(nickname, validate(nickname, "nickname"))
            player_id = composite_nickname.player_id
            nickname = composite_nickname.nickname
        elif len(splitted_message) == 1:
            raise MissingArgumentsError
        else:
            if not member:
                await bot.send_message(msg.chat.id, Text().get().frequent.info.unregistred_player)
                return

            account = member.current_account
            region = account.region
            player_id = account.game_id
            nickname = account.nickname

        if member:
            img = await StatsFunc.stats4registred_player(member.current_slot, member)
        else:
            img = await StatsFunc.generate_image(player_id, nickname, region)
        
        if isinstance(img, str):
            await bot.send_message(msg.chat.id, img)
            return

        return (msg.chat.id, BufferedInputFile(img.read(), "stats.png")), {}
    
    async def inline_stats(self, query: 'InlineQuery', bot: 'Bot'):
        await Text().load_by_id(await self.pdb.get_member(query.from_user.id), query.from_user.language_code)

        splitted_query = query.query.strip().split()
        member = None
        if len(splitted_query) == 2:
            region = splitted_query[1] if splitted_query[1] in _config.default.available_regions else splitted_query[0]
            nickname = splitted_query[1] if not (splitted_query[1] in _config.default.available_regions) else splitted_query[0]
            
            if region not in _config.default.available_regions:
                return

            composite_nickname = handle_nickname(nickname, validate(nickname, "nickname"))
            player_id = composite_nickname.player_id
            nickname = composite_nickname.nickname
        elif len(splitted_query) == 1 and splitted_query[0].lower() == 'me':
            try:
                member = await self.pdb.get_member(query.from_user.id)
                account = member.current_account
            except:
                return

            region = account.region
            player_id = account.game_id
            nickname = account.nickname
        else:
            return
        data = await self.api.get_stats(
            game_id=player_id,
            search=nickname,
            region=region
            )
        
        img = self.img_gen.generate(data, member, member.current_slot if member else None)

        msg = await bot.send_photo(_config.init_photos_id, BufferedInputFile(img.read(), filename="stats.png"))

        await query.answer(results=[
                                InlineQueryResultCachedPhoto(id=str(uuid4()), 
                                title=f"{nickname} stats",
                                photo_file_id=msg.photo[0].file_id)
        ])
        await msg.delete()
