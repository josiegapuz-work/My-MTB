from PIL import Image
import os

# Target aspect ratio (833:1048 ≈ 0.795)
TARGET_WIDTH = 833
TARGET_HEIGHT = 1048
TARGET_RATIO = TARGET_WIDTH / TARGET_HEIGHT

input_folder = "images"
output_folder = "images_resized"
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(input_folder, filename)
        img = Image.open(path)

        # Current aspect ratio
        current_ratio = img.width / img.height

        # Scale image to fit target height or width depending on ratio
        if current_ratio > TARGET_RATIO:
            # Image is wider → fit width
            new_width = TARGET_WIDTH
            new_height = int(TARGET_WIDTH / current_ratio)
        else:
            # Image is taller/narrower → fit height
            new_height = TARGET_HEIGHT
            new_width = int(TARGET_HEIGHT * current_ratio)

        resized = img.resize((new_width, new_height), Image.ANTIALIAS)

        # Create white background canvas
        canvas = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (255, 255, 255))

        # Center the resized image
        x_offset = (TARGET_WIDTH - new_width) // 2
        y_offset = (TARGET_HEIGHT - new_height) // 2
        canvas.paste(resized, (x_offset, y_offset))

        # Save result
        save_path = os.path.join(output_folder, filename)
        canvas.save(save_path, "JPEG")
        print(f"Processed {filename} → {save_path}")
