from PIL import Image, ImageDraw

img = Image.new('L', (200, 200), color = 0)
draw = ImageDraw.Draw(img)
draw.line((0, 0, 199, 0), fill=255)
draw.line((0, 0, 0, 199), fill=255)
draw.line((199, 199, 199, 0), fill=255)
draw.line((199, 199, 0, 199), fill=255)
img.save("box.png")
