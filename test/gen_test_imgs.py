from PIL import Image, ImageDraw
for i in range(4000):
	img = Image.new('L', (500 - i // 10, 100 + i // 10), color = 255)
	d = ImageDraw.Draw(img)
	d.text((10, 10), str(i))
	img.save(f"{i:04}.png")
