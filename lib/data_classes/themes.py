from pydantic import BaseModel
from PIL import Image

from lib.data_classes.db_player import ImageSettings

class FakeImage(Image.Image, BaseModel):
    pass

class Theme(BaseModel):
    image_settings: ImageSettings
    bg_path: str
    bg: None | FakeImage
