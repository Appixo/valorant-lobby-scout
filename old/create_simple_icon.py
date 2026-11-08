#!/usr/bin/env python3
"""
Create a simple Valorant-inspired icon as a placeholder
"""
import os

try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a 256x256 image with Valorant colors
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Valorant red background
    valorant_red = (255, 70, 85)  # #ff4655
    draw.rounded_rectangle([(0, 0), (size, size)], radius=20, fill=valorant_red)
    
    # White 'V' in the center
    # This is a simple triangle-ish V shape
    v_points = [
        (size * 0.3, size * 0.3),   # Top left
        (size * 0.5, size * 0.7),   # Bottom center
        (size * 0.7, size * 0.3),   # Top right
        (size * 0.6, size * 0.3),   # Top right inner
        (size * 0.5, size * 0.55),  # Mid center
        (size * 0.4, size * 0.3),   # Top left inner
    ]
    draw.polygon(v_points, fill='white')
    
    # Save as PNG
    img.save('valorant_icon.png', 'PNG')
    
    print("[SUCCESS] Created valorant_icon.png")
    print(f"[INFO] Size: {size}x{size} pixels")
    print("[INFO] Location: " + os.path.abspath('valorant_icon.png'))
    print("\nThis is a simple placeholder icon.")
    print("For the official icon, manually download from:")
    print("https://www.valorantpc.com or search 'Valorant logo PNG'")
    
except ImportError:
    print("[ERROR] PIL/Pillow not installed")
    print("Install with: pip install Pillow")
except Exception as e:
    print(f"[ERROR] Failed to create icon: {e}")

