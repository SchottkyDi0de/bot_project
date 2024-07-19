import fastapi

from lib.image.common import ImageGenCommon

app = fastapi.FastAPI()

class ImageGenServer:
    
    def __init__() -> None:
        pass
    
    @app.get('image_gen_server/generate_common_image', include_in_schema=False)
    async def generate_common_image() -> str:
        ...