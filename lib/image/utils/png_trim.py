from PIL import Image, ImageChops


def trim(image: Image.Image) -> Image.Image:
    """
    Trim image with transparent background

    Args:
        image (PIL.Image.Image): The input image.

    Returns:
        PIL.Image.Image: The trimmed image.
    """
    bg = Image.new(image.mode, image.size, image.getpixel((0,0)))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)