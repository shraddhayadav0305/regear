#!/usr/bin/env python
"""
Create an optimized camera image for the category display
This creates a clean, properly-sized camera icon for the 100x100px box
"""

from PIL import Image, ImageDraw
import os

def create_camera_image_optimized():
    """Create and optimize camera image for category box"""
    
    # Create a larger image first (for quality), then resize down
    size = 400
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    dark_gray = (60, 60, 70)
    light_gray = (120, 120, 140)
    gold = (255, 180, 0)
    orange = (255, 140, 0)
    
    # Draw camera body (rounded rectangle effect with larger body)
    margin = 40
    body_left = margin
    body_top = margin + 50
    body_right = size - margin
    body_bottom = size - margin
    
    # Main body rectangle
    draw.rectangle(
        [(body_left, body_top), (body_right, body_bottom)],
        fill=dark_gray,
        outline=(40, 40, 50),
        width=5
    )
    
    # Top panel
    draw.rectangle(
        [(body_left, body_top - 60), (body_right, body_top)],
        fill=(80, 80, 90),
        outline=(40, 40, 50),
        width=3
    )
    
    # Lens assembly
    lens_center_x = body_right - 100
    lens_center_y = size // 2 + 20
    lens_radius = 70
    
    # Outer lens ring
    draw.ellipse(
        [(lens_center_x - lens_radius, lens_center_y - lens_radius),
         (lens_center_x + lens_radius, lens_center_y + lens_radius)],
        fill=(70, 70, 80),
        outline=(40, 40, 50),
        width=4
    )
    
    # Glass effect - concentric circles
    for r, color in [(60, light_gray), (45, gold), (30, orange), (15, (255, 200, 50))]:
        draw.ellipse(
            [(lens_center_x - r, lens_center_y - r),
             (lens_center_x + r, lens_center_y + r)],
            outline=color,
            width=2
        )
    
    # Center dot
    draw.ellipse(
        [(lens_center_x - 8, lens_center_y - 8),
         (lens_center_x + 8, lens_center_y + 8)],
        fill=(255, 255, 255),
        outline=(100, 100, 100),
        width=1
    )
    
    # Flash unit on top
    flash_left = body_left + 60
    flash_top = body_top - 50
    draw.rectangle(
        [(flash_left, flash_top), (flash_left + 40, flash_top + 35)],
        fill=light_gray,
        outline=(40, 40, 50),
        width=2
    )
    
    # Viewfinder on top
    vf_left = body_left + 140
    vf_top = body_top - 50
    draw.rectangle(
        [(vf_left, vf_top), (vf_left + 35, vf_top + 35)],
        fill=(50, 50, 60),
        outline=(40, 40, 50),
        width=2
    )
    
    # Side handle detail
    handle_x = body_left + 30
    handle_y = size // 2
    draw.rectangle(
        [(handle_x, handle_y), (handle_x + 35, handle_y + 80)],
        fill=(80, 80, 90),
        outline=(40, 40, 50),
        width=2
    )
    
    # Button on side
    draw.ellipse(
        [(handle_x + 8, handle_y + 20), (handle_x + 18, handle_y + 30)],
        fill=(100, 100, 110),
        outline=(40, 40, 50),
        width=1
    )
    
    # Resize to final size (100x100)
    img_final = img.resize((100, 100), Image.Resampling.LANCZOS)
    
    # Save
    os.makedirs('static/images', exist_ok=True)
    output_path = 'static/images/camera.png'
    img_final.save(output_path, 'PNG')
    
    file_size = os.path.getsize(output_path)
    print("✅ Optimized camera image created!")
    print(f"   Size: 100x100 pixels")
    print(f"   Location: {output_path}")
    print(f"   File size: {file_size} bytes")
    print(f"   Format: PNG with transparency")
    return True

if __name__ == "__main__":
    print("="*60)
    print("CREATING OPTIMIZED CAMERA IMAGE")
    print("="*60)
    print()
    create_camera_image_optimized()
    print()
    print("="*60)
    print("Image ready! Refresh your browser to see changes.")
    print("="*60)
