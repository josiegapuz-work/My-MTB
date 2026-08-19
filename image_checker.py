from PIL import Image
import os

folder = "images"

for filename in os.listdir(folder):
    if filename.endswith(".jpg"):
        path = os.path.join(folder, filename)
        img = Image.open(path)

        # Apply rotation if needed, e.g. 90 degrees
        rotated = img.rotate(90, expand=True)

        # Strip EXIF by converting to RGB
        rotated = rotated.convert("RGB")
        rotated.save(path)
