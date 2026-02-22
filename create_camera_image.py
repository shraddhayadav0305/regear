#!/usr/bin/env python
"""Generate and save a camera image using PIL"""

try:
    from PIL import Image, ImageDraw
    import os
    
    # Create image with transparent background
    img = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw camera body (dark gray rectangle with rounded corners)
    camera_width = 200
    camera_height = 140
    start_x = 50
    start_y = 80
    
    # Main body
    draw.rectangle(
        [(start_x, start_y), (start_x + camera_width, start_y + camera_height)],
        fill=(40, 40, 40),
        outline=(20, 20, 20),
        width=3
    )
    
    # Lens (circle)
    lens_x = start_x + camera_width - 60
    lens_y = start_y + camera_height // 2
    lens_radius = 40
    
    # Lens outer circle
    draw.ellipse(
        [(lens_x - lens_radius, lens_y - lens_radius),
         (lens_x + lens_radius, lens_y + lens_radius)],
        fill=(30, 30, 30),
        outline=(10, 10, 10),
        width=2
    )
    
    # Lens inner circles (glass effect)
    for r in [30, 20, 10]:
        draw.ellipse(
            [(lens_x - r, lens_y - r),
             (lens_x + r, lens_y + r)],
            outline=(60, 60, 60),
            width=1
        )
    
    # Top panel with buttons
    top_h = 20
    draw.rectangle(
        [(start_x, start_y - top_h), (start_x + camera_width, start_y)],
        fill=(50, 50, 50),
        outline=(20, 20, 20),
        width=2
    )
    
    # Small button on top
    draw.rectangle(
        [(start_x + 20, start_y - 15), (start_x + 40, start_y - 5)],
        fill=(70, 70, 70),
        outline=(40, 40, 40),
        width=1
    )
    
    # Flip/rotate button
    draw.rectangle(
        [(start_x + 50, start_y - 15), (start_x + 70, start_y - 5)],
        fill=(70, 70, 70),
        outline=(40, 40, 40),
        width=1
    )
    
    # Side panel detail
    draw.rectangle(
        [(start_x + camera_width - 40, start_y + 30),
         (start_x + camera_width - 20, start_y + 90)],
        fill=(50, 50, 50),
        outline=(30, 30, 30),
        width=1
    )
    
    # Save the image
    os.makedirs('static/images', exist_ok=True)
    img.save('static/images/camera.png')
    print("✅ Camera image created: static/images/camera.png")
    print(f"   Size: 300x300 pixels (RGBA with transparency)")
    
except ImportError:
    print("❌ PIL not available. Installing...")
    import subprocess
    subprocess.run(['pip', 'install', 'Pillow'], check=True)
    print("Please run this script again.")
except Exception as e:
    print(f"❌ Error: {e}")
