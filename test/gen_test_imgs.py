from PIL import Image, ImageDraw
for i in range(4000):
	print(i)
	img = Image.new('RGBA', (500 - i // 10, 100 + i // 10), color = (255, 255, 255, i // 20))
	d = ImageDraw.Draw(img)
	d.text((10, 10), str(i))
	img.save(f"{i:04}.png")
