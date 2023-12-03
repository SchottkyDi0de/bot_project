from PIL import Image

from lib.logger.logger import get_logger

_log = get_logger(__name__, 'ImageUtilsResizerLogger', 'logs/image_utils_resizer.log')

def resize_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """
    Resizes an image to the specified size.
    If image.width > or < target width more than 10% or image.height > or < target height more than 5%
    image has be cropped, otherwise image is resized.

    Args:
        image (PIL.Image.Image): The image to be resized.
        size (tuple[int, int]): The target size of the image.

    Returns:
        PIL.Image.Image: The resized image.

    Raises:
        ValueError: If the input image is not an instance of PIL.Image.Image.
    """
    if isinstance(image, Image.Image):
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

        if width_oversize_percent < width_offset and height_oversize_percent < height_offset:
            image = image.resize((size[0], size[1]))
        
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
            bg = Image.new('RGBA', size, (0, 0, 0, 0))
            bg.paste(
                image, (
                    (size[0] // 2 - image.size[0] // 2) if width_oversize < 0 else 0,
                    (size[1] // 2 - image.size[1] // 2) if height_oversize < 0 else 0
                    )
                )
            image = bg.copy()

        _log.debug(f'Image size: {image.size}')
        return image

    raise ValueError('image must be PIL.Image.Image')