from discord import Colour, Embed

from lib.data_classes.db_player import AccountSlotsEnum, GameAccount
from lib.locale.locale import Text
from lib.utils.slot_info import get_formatted_slot_info

class CommonMSG():
    
    def verify(self, game_account: GameAccount, slot: AccountSlotsEnum) -> Embed:
        text = Text().get()
        return Embed(
            title=text.cmds.verify.items.verify,
            description=text.cmds.verify.items.message.description
        ).set_footer(
            text=get_formatted_slot_info(
                slot=slot, 
                text=text, 
                game_account=game_account,
                shorted=True,
                clear_md=True
            )
        )

    def custom(
        self,
        title: str,
        description: str = '',
        colour: str = 'green',
        ) -> Embed:
        
        embed =  Embed(
            title=title,
            description=description,
            colour=getattr(Colour, colour)()
        )
            
        return embed