#!/usr/bin/env python
"""
Process and optimize camera image for category display

This script will:
1. Save the new camera image provided
2. Resize and optimize it to fit perfectly in 100x100px box
3. Add proper padding/centering for best display
"""

from PIL import Image
import os

def optimize_image_for_category(input_path, output_path, target_size=100):
    """
    Optimize an image to display properly in a 100x100px category box
    
    Args:
        input_path: Path to source image
        output_path: Path to save optimized image
        target_size: Size of category box (100x100px)
    """
    try:
        # Open image
        img = Image.open(input_path)
        
        # Convert RGBA if needed for transparency
        if img.mode in ('RGBA', 'LA'):
            pass  # Keep as is
        elif img.mode == 'RGB':
            # Add alpha channel for transparency
            img = img.convert('RGBA')
        
        # Get original dimensions
        orig_width, orig_height = img.size
        
        # Calculate scaling to fit in target box with some padding
        # We want the image to be 85-90% of the box size
        padding_ratio = 0.85
        max_display_size = int(target_size * padding_ratio)
        
        # Calculate scale factor to fit the larger dimension
        scale = max_display_size / max(orig_width, orig_height)
        
        # Calculate new size
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)
        
        # Resize image with high-quality resampling
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a new transparent background (100x100)
        bg = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
        
        # Calculate position to center the image
        x = (target_size - new_width) // 2
        y = (target_size - new_height) // 2
        
        # Paste resized image onto background
        bg.paste(img_resized, (x, y), img_resized if img_resized.mode == 'RGBA' else None)
        
        # Convert to RGB for better compatibility (optional)
        # If you want transparency kept, comment this out
        # bg = bg.convert('RGB')
        
        # Save optimized image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        bg.save(output_path, 'PNG', quality=95)
        
        print(f"✅ Image optimized and saved!")
        print(f"   Original size: {orig_width}x{orig_height}")
        print(f"   Resized to: {new_width}x{new_height}")
        print(f"   Final box: 100x100px")
        print(f"   Saved to: {output_path}")
        print(f"   File size: {os.path.getsize(output_path)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing image: {e}")
        return False


# Usage example
if __name__ == "__main__":
    # Note: For now, this is a utility script
    # To use it with a new image:
    # 1. Save your image to 'camera_new.png' in the project root
    # 2. Uncomment the lines below:
    
    # if os.path.exists('camera_new.png'):
    #     optimize_image_for_category('camera_new.png', 'static/images/camera.png')
    # else:
    #     print("Place your camera image as 'camera_new.png' in project root")
    
    print("Image optimization utility ready!")
    print("\nTo process an image:")
    print("  from process_image import optimize_image_for_category")
    print("  optimize_image_for_category('your_image.png', 'static/images/camera.png')")
