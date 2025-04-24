from PIL import Image,ImageDraw
def round_image(img, radius):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)

    img = img.convert("RGBA")
    img.putalpha(mask)
    return img

