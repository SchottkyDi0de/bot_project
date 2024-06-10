from enum import Enum
from PIL import Image, ImageFilter

from lib.logger.logger import get_logger

_log = get_logger(__file__, 'ImageUtilsResizerLogger', 'logs/image_utils_resizer.log')


class ResizeMode(Enum):
    RESIZE = 1
    CROP_OR_FILL = 2
    AUTO = 3

def resize_image(image: Image.Image, size: tuple[int, int], mode: ResizeMode = ResizeMode.AUTO) -> Image.Image:
    """
    Resizes an image to the specified size.
    If image.width > or < target width more than 15% or image.height > or < target height more than 10%
    image has be cropped, otherwise image is resized.

    Args:
        image (PIL.Image.Image): The image to be resized.
        size (tuple[int, int]): The target size of the image.

    Returns:
        PIL.Image.Image: The resized image.

    Raises:
        ValueError: If the input image is not an instance of PIL.Image.Image.
    """
    if not isinstance(image, Image.Image):
        raise TypeError('image must be PIL.Image.Image')
    
    if image.size == size:
        return image
    
    if image.mode == 'RGB':
        image = image.convert('RGBA')

    img_size = image.size
    width_offset = 15  # Percent
    height_offset = 10  # Percent
    width_oversize = img_size[0] - size[0]
    height_oversize = img_size[1] - size[1]
    width_oversize_percent = abs(img_size[0] / size[0] * 100 - 100)
    height_oversize_percent = abs(img_size[1] / size[1] * 100 - 100)
    
    if mode == ResizeMode.CROP_OR_FILL:
        if width_oversize > 0:
            image = image.crop(
                (0 + width_oversize // 2, 
                0, 
                image.size[0] - width_oversize // 2, 
                image.size[1])
                )
            _log.debug(f'Width oversize: {image.size}')

        if height_oversize > 0:
            image = image.crop(
                (0, 
                0 + height_oversize // 2, 
                image.size[0], 
                image.size[1] - height_oversize // 2)
                )
            _log.debug(f'Height oversize: {image.size}')
            
        if width_oversize < 0 or height_oversize < 0:
            filter = ImageFilter.GaussianBlur(radius=100)
            bg = image.copy().resize(size, resample=Image.Resampling.LANCZOS).filter(filter)
            bg.paste(
                image, (
                    (size[0] // 2 - image.size[0] // 2) if width_oversize < 0 else 0,
                    (size[1] // 2 - image.size[1] // 2) if height_oversize < 0 else 0
                    )
                )
            image = bg.copy()
            
        return image
        
    if mode == ResizeMode.RESIZE:
        return image.resize(size, resample=Image.Resampling.LANCZOS)
    
    if mode == ResizeMode.AUTO:
        if width_oversize_percent < width_offset and height_oversize_percent < height_offset:
            image = image.resize((size[0], size[1]), resample=Image.Resampling.LANCZOS)
        
        if width_oversize > 0:
            image = image.crop(
                (0 + width_oversize // 2, 
                0, 
                image.size[0] - width_oversize // 2, 
                image.size[1])
                )
            _log.debug(f'Width oversize: {image.size}')

        if height_oversize > 0:
            image = image.crop(
                (0, 
                0 + height_oversize // 2, 
                image.size[0], 
                image.size[1] - height_oversize // 2)
                )
            _log.debug(f'Height oversize: {image.size}')

        if width_oversize < 0 or height_oversize < 0:
            # bg = Image.new('RGBA', size, (0, 0, 0, 40))
            filter = ImageFilter.GaussianBlur(radius=100)
            bg = image.copy().resize(size, resample=Image.Resampling.LANCZOS).filter(filter)
            bg.paste(
                image, (
                    (size[0] // 2 - image.size[0] // 2) if width_oversize < 0 else 0,
                    (size[1] // 2 - image.size[1] // 2) if height_oversize < 0 else 0
                    )
                )
            image = bg.copy()

        _log.debug(f'Image size: {image.size}')
        return image

        
def center_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """
    Crop an image to the center of the given size.

    Args:
        image (PIL.Image.Image): The image to be cropped.
        size (tuple[int, int]): The size of the cropped image.

    Returns:
        PIL.Image.Image: The cropped image.

    Raises:
        ValueError: If the input image is not an instance of PIL.Image.Image.
    """
    if not isinstance(image, Image.Image):
        raise TypeError('image must be PIL.Image.Image')
    
    if image.size == size:
        return image
        
    x_oversize = image.size[0] - size[0]
    y_oversize = image.size[1] - size[1]

    return image.crop(
        (x_oversize // 2, y_oversize // 2, image.size[0] - x_oversize // 2, image.size[1] - y_oversize // 2)
    )