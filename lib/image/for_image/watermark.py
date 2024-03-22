from PIL import Image


class Watermark:
    v1 = Image.open('res/icons/watermark/watermark.png', formats=['png']).rotate(90, expand=True)