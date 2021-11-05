from PIL import Image, ImageDraw
for i in range(79):
	img = Image.new('L', (60, 30), color = 255)
	d = ImageDraw.Draw(img)
	d.text((10, 10), str(i))
	img.save(f"{i:03}.png")
