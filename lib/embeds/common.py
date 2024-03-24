from discord import Colour, Embed

from lib.locale.locale import Text

class CommonMSG():
    
    def verify(self) -> Embed:
        text = Text().get()
        return Embed(
            title=text.cmds.verify.items.verify,
            description=text.cmds.verify.items.message.description
        ).add_field(
            name=text.frequent.info.warning,
            value=text.cmds.verify.items.message.additional_info
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