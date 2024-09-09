from lib.api import API
from lib.database.players import PlayersDB
from lib.image import CommonImageGen


class Objects:
    pdb = PlayersDB()
    api = API()
    common_image_gen = CommonImageGen()
