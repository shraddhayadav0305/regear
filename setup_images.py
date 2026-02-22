#!/usr/bin/env python
"""
Save camera image to static folder.

Instructions:
1. Place your camera.png image in the static/images/ folder
2. Or run this script with the image path

For now, we'll update the app to reference the image from static folder.
"""

import os
from pathlib import Path

# Create a test to verify the path works
static_images = Path("static/images")
print(f"Images folder exists: {static_images.exists()}")
print(f"Images path: {static_images.absolute()}")

# List current images
if static_images.exists():
    images = list(static_images.glob("*"))
    if images:
        print(f"\nCurrent images: {[img.name for img in images]}")
    else:
        print("\n(No images yet - place camera.png here)")
