from PIL import Image
img_path = "/mount/src/my-mtb/images/pm_en_1-3-010_f.jpg"
Image.open(img_path).verify()
