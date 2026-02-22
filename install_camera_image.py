#!/usr/bin/env python
"""
Save and optimize the camera image they provided
This script will replace the placeholder camera.png with an optimized version
"""

from PIL import Image, ImageDraw
import os

def create_optimized_camera_image():
    """
    Create or process camera image optimized for 100x100px display
    """
    
    # First, check if there's a camera image in the root directory
    possible_paths = [
        'camera.png',
        'camera.jpg',
        'camera.jpeg',
        'camera.webp',
        'Camera.png',
        'Camera.jpg',
        'downloaded_camera.png'
    ]
    
    source_file = None
    for path in possible_paths:
        if os.path.exists(path):
            source_file = path
            print(f"Found image: {path}")
            break
    
    # Create output directory
    os.makedirs('static/images', exist_ok=True)
    
    if source_file:
        # Process the found image
        print(f"\n✅ Processing image: {source_file}")
        
        try:
            img = Image.open(source_file)
            print(f"   Original size: {img.size}")
            print(f"   Format: {img.format}")
            print(f"   Mode: {img.mode}")
            
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Get dimensions
            w, h = img.size
            
            # Calculate scaling to fit in 100x100 box (85% of box size)
            display_size = 85
            scale = display_size / max(w, h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Resize with high quality
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Create background
            bg = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
            
            # Center image
            x = (100 - new_w) // 2
            y = (100 - new_h) // 2
            bg.paste(img, (x, y), img)
            
            # Save
            output = 'static/images/camera.png'
            bg.save(output, 'PNG')
            
            file_size = os.path.getsize(output)
            print(f"\n✅ Camera image optimized and saved!")
            print(f"   Size: 100x100px (optimized)")
            print(f"   Location: {output}")
            print(f"   File size: {file_size} bytes")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing image: {e}")
            return False
    
    else:
        print("⚠️ No camera image found in root directory")
        print("\nTo use your camera image:")
        print("1. Save your camera image to project root as 'camera.png'")
        print("2. Run this script again")
        print("\nSupported formats: PNG, JPG, JPEG, WebP")
        return False

if __name__ == "__main__":
    print("="*60)
    print("CAMERA IMAGE OPTIMIZATION TOOL")
    print("="*60)
    create_optimized_camera_image()
    print("="*60)
