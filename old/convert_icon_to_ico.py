#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert PNG icon to ICO format for better Windows taskbar support
"""
import os
import sys

def convert_png_to_ico(png_path, ico_path=None):
    """
    Convert PNG image to ICO format with multiple sizes for Windows
    
    Args:
        png_path: Path to the PNG file
        ico_path: Output ICO path (optional, defaults to same name with .ico)
    """
    if ico_path is None:
        ico_path = os.path.splitext(png_path)[0] + '.ico'
    
    try:
        from PIL import Image
    except ImportError:
        print("[ERROR] Pillow library not found!")
        print("Please install it with: pip install Pillow")
        return False
    
    try:
        # Open the PNG image
        img = Image.open(png_path)
        print(f"[INFO] Loaded {png_path} ({img.size[0]}x{img.size[1]}, {img.mode})")
        
        # Convert RGBA to RGB if necessary (ICO doesn't support RGBA well)
        if img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
            print("[INFO] Converted RGBA to RGB")
        
        # Create multiple sizes for Windows (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Resize and save as ICO
        img.save(ico_path, format='ICO', sizes=sizes)
        
        print(f"[SUCCESS] Created {ico_path}")
        print(f"[INFO] ICO contains: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        return False

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console (helps with Unicode)
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    # Convert the valorant icon
    png_file = "valorant_icon.png"
    
    print("=" * 60)
    print("PNG to ICO Converter for Valorant Player Detector")
    print("=" * 60)
    
    if os.path.exists(png_file):
        print(f"[INFO] Converting {png_file} to ICO format...")
        if convert_png_to_ico(png_file):
            print("\n[DONE] Icon conversion complete!")
            print("The application will now use the ICO file for better taskbar support.")
        else:
            print("\n[FAILED] Icon conversion failed.")
    else:
        print(f"[ERROR] {png_file} not found in current directory")
        print(f"[INFO] Current directory: {os.getcwd()}")
        print("\nPlease make sure valorant_icon.png exists in the project folder.")

