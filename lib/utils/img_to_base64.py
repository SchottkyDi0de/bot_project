import base64
from io import BytesIO

from PIL import Image

def convert_image(image: Image.Image) -> str:
    with BytesIO() as buffer:
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()