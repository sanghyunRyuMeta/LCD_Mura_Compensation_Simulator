import numpy as np
from PIL import Image
import os
import glob

folder = os.path.dirname(os.path.abspath(__file__))
image_files = glob.glob(os.path.join(folder, "*.png"))

for img_path in image_files:
    print(f"Processing: {os.path.basename(img_path)}")
    img = np.array(Image.open(img_path))

    # Copy row 7 (index 7) into rows 0-6
    for row in range(7):
        img[row, :] = img[7, :]

    out_img = Image.fromarray(img)
    out_img.save(img_path)
    print(f"  Saved (rows 0-6 filled with row 7 values)")

print("Done.")
