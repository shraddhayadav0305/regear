#!/usr/bin/env python
"""
Instructions for using your own camera image

CURRENT STATUS:
✅ Camera image is now set for "Cameras & DSLR" category
✅ Located at: static/images/camera.png
✅ Size: 300x300 pixels
✅ Format: PNG with transparency

TO USE YOUR OWN IMAGE:
1. Save your camera.png image to: static/images/camera.png
   (This will replace the current generated image)

2. Recommended specifications:
   - Size: 300x300 pixels (minimum 150x150)
   - Format: PNG, JPG, or WebP
   - Should have transparent background (PNG recommended)
   - Should be centered and well-proportioned

HOW IT WORKS:
- The API endpoint /api/categories returns image paths for each category
- For Cameras & DSLR, it returns: "/static/images/camera.png"
- The homepage JavaScript displays this as a background image
- Image fills the 100x100px category box with cover positioning

TO REPLACE WITH YOUR IMAGE:
Option 1 (Easiest): 
- Copy your camera image and save as 'camera.png' to 'static/images/' folder
- Restart the Flask server
- Done! Your image will now display

Option 2 (Different format):
- If your image is JPG: rename/convert to static/images/camera.png
- If you want WebP: save as static/images/camera.webp and update app.py

TO ADD MORE CUSTOM IMAGES:
- Add other images to static/images/ folder
- Update app.py category_images dict with paths
- Example: "Mobile Phones": "/static/images/phones.png"
"""

import os
import shutil

print(__doc__)

# Check current camera image
camera_path = "static/images/camera.png"
if os.path.exists(camera_path):
    size = os.path.getsize(camera_path)
    print(f"\n✅ Current camera.png exists ({size} bytes)")
else:
    print(f"\n⚠️ Camera image not found at {camera_path}")

# Check folder
images_folder = "static/images"
if os.path.exists(images_folder):
    files = os.listdir(images_folder)
    if files:
        print(f"   Files in {images_folder}: {files}")
