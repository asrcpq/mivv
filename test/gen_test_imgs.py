from PIL import Image, ImageDraw
for i in range(79):
	img = Image.new('L', (120 - i, 20 + i), color = 255)
	d = ImageDraw.Draw(img)
	d.text((10, 10), str(i))
	img.save(f"{i:03}.png")
