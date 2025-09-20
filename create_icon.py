#!/usr/bin/env python3
"""
Create application icon for Transmission Dashboard
"""

from PIL import Image, ImageDraw
import os

def create_icon():
    """Create a 64x64 icon for the application"""
    # Create a 64x64 image with transparent background
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background circle
    draw.ellipse([8, 8, 56, 56], fill=(102, 126, 234, 255), outline=(255, 255, 255, 255), width=2)
    
    # Draw chart bars (dashboard representation)
    draw.rectangle([20, 35, 25, 45], fill=(255, 255, 255, 255))
    draw.rectangle([28, 30, 33, 45], fill=(255, 255, 255, 255))
    draw.rectangle([36, 25, 41, 45], fill=(255, 255, 255, 255))
    
    # Draw "TD" text
    draw.text((32, 15), "TD", fill=(255, 255, 255, 255))
    
    # Save as ICO file
    img.save('icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
    print("✅ Created icon.ico")

if __name__ == '__main__':
    create_icon()
