import base64
from io import BytesIO
from os import PathLike

from PIL import Image

from lib.data_classes.themes import FakeImage

def bytes_to_img(img_bytes: bytes, content_type: str | None) -> Image.Image:
    """
    Converts an attachment.read() bytes to an image.
    
    Args:
        attachment (bytes): The attachment to convert.
    
    Returns:
        Image.Image: The image representation of the attachment.
    """
    with BytesIO(img_bytes) as buffer:
        buffer.seek(0)
        image = Image.open(buffer, formats=['PNG' if content_type == 'image/png' else 'JPEG']).copy()
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

    return image

def img_to_base64(image: Image.Image | FakeImage | BytesIO | PathLike | str) -> str:
    """
    Converts an image to a base64 string representation.
    
    Args:
        image (Image.Image | FakeImage | BytesIO | PathLike | str): The image to convert.
            It can be an instance of PIL.Image.Image, FakeImage, BytesIO, or PathLike object.
            It can also be a string representing the path to an image file.
            
    Returns:
        str: The base64 string representation of the image.
    
    Raises:
        TypeError: If the image parameter is not an instance of PIL.Image.Image, FakeImage, BytesIO, or PathLike object.
    """
    if isinstance(image, (Image.Image, FakeImage)):
        image = image.convert('RGBA')
        with BytesIO() as buffer:
            image.save(buffer, format='PNG')
            buffer.seek(0)
            base_64_img = base64.b64encode(buffer.read()).decode()

        return base_64_img
    
    elif isinstance(image, BytesIO):
        return base64.b64encode(image.getvalue()).decode()
    
    elif isinstance(image, (PathLike, str)):
        with BytesIO() as buffer:
            with Image.open(image, 'r') as img:
                img.save(buffer, format='PNG')
            
            buffer.seek(0)
            base_64_img = base64.b64encode(buffer.read()).decode()
        
        return base_64_img
    
    else:
        raise TypeError('image must be an instance of PIL.Image.Image, BytesIO, or PathLike object')

def base64_to_img(base64_string: str) -> Image.Image:
    if not isinstance(base64_string, str):
        raise TypeError(f'base64_string must be a string, not {base64_string.__class__.__name__}')
    
    with BytesIO(base64.b64decode(base64_string)) as buffer:
        buffer.seek(0)
        image = Image.open(buffer, formats=['PNG']).copy()
        
    return image


def img_to_readable_buffer(image: Image.Image) -> BytesIO:
    if not isinstance(image, Image.Image):
        raise TypeError(f'image must be an instance of PIL.Image.Image, not {image.__class__.__name__}')
    
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer

def readable_buffer_to_base64(buffer: BytesIO) -> str:
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return b64
