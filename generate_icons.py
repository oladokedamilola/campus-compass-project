"""
Generate all PWA and favicon icons using only Pillow (no Cairo required)
Run: pip install pillow
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Configuration
OUTPUT_DIR = 'static/images/icons'

# Icon sizes needed for PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Favicon sizes
FAVICON_SIZES = [16, 32, 48]

# Apple touch icon sizes
APPLE_SIZES = [180]

# Maskable icon size
MASKABLE_SIZE = 512

# Colors
DARK_BG = '#0D0D0D'
ACCENT = '#00F0FF'
ACCENT_DARK = '#00C8D4'
GRAY_DARK = '#1a1a1a'
GRAY_MID = '#333333'
GRAY_LIGHT = '#666666'

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✅ Created directory: {directory}")

def draw_compass_icon(size):
    """Draw a compass icon on a PIL Image"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions
    center = size // 2
    outer_radius = int(size * 0.48)
    inner_radius = int(size * 0.35)
    center_radius = int(size * 0.1)
    pointer_length = int(size * 0.38)
    pointer_width = int(size * 0.1)
    
    # Draw background circle
    draw.ellipse(
        [center - outer_radius, center - outer_radius, 
         center + outer_radius, center + outer_radius],
        fill=GRAY_DARK,
        outline=ACCENT,
        width=max(2, int(size * 0.025))
    )
    
    # Draw outer glow ring (semi-transparent)
    draw.ellipse(
        [center - outer_radius - 1, center - outer_radius - 1,
         center + outer_radius + 1, center + outer_radius + 1],
        outline=ACCENT,
        width=max(1, int(size * 0.01))
    )
    
    # Draw North pointer (triangle)
    north_points = [
        (center, center - pointer_length),
        (center + pointer_width, center - int(pointer_length * 0.3)),
        (center, center - int(pointer_length * 0.15)),
        (center - pointer_width, center - int(pointer_length * 0.3))
    ]
    draw.polygon(north_points, fill=ACCENT)
    
    # Draw South pointer
    south_points = [
        (center, center + pointer_length),
        (center + pointer_width, center + int(pointer_length * 0.3)),
        (center, center + int(pointer_length * 0.15)),
        (center - pointer_width, center + int(pointer_length * 0.3))
    ]
    draw.polygon(south_points, fill=GRAY_MID)
    
    # Draw East pointer
    east_points = [
        (center + pointer_length, center),
        (center + int(pointer_length * 0.3), center + pointer_width),
        (center + int(pointer_length * 0.15), center),
        (center + int(pointer_length * 0.3), center - pointer_width)
    ]
    draw.polygon(east_points, fill=GRAY_MID)
    
    # Draw West pointer
    west_points = [
        (center - pointer_length, center),
        (center - int(pointer_length * 0.3), center + pointer_width),
        (center - int(pointer_length * 0.15), center),
        (center - int(pointer_length * 0.3), center - pointer_width)
    ]
    draw.polygon(west_points, fill=GRAY_MID)
    
    # Draw inner circle
    draw.ellipse(
        [center - inner_radius, center - inner_radius,
         center + inner_radius, center + inner_radius],
        fill=DARK_BG,
        outline=ACCENT,
        width=max(2, int(size * 0.02))
    )
    
    # Draw center dot
    dot_radius = max(3, int(size * 0.03))
    draw.ellipse(
        [center - dot_radius, center - dot_radius,
         center + dot_radius, center + dot_radius],
        fill=ACCENT
    )
    
    # Draw decorative rings
    ring_radius = int(outer_radius * 0.7)
    draw.ellipse(
        [center - ring_radius, center - ring_radius,
         center + ring_radius, center + ring_radius],
        outline=ACCENT,
        width=max(1, int(size * 0.008))
    )
    
    ring_radius_small = int(outer_radius * 0.5)
    draw.ellipse(
        [center - ring_radius_small, center - ring_radius_small,
         center + ring_radius_small, center + ring_radius_small],
        outline=ACCENT,
        width=max(1, int(size * 0.005))
    )
    
    return img

def add_text_to_icon(img, size, text, color, position='north'):
    """Add text label to icon"""
    draw = ImageDraw.Draw(img)
    center = size // 2
    
    # Try to use a font, fallback to default
    try:
        # Try different font sizes based on icon size
        font_size = max(8, int(size * 0.09))
        if size >= 512:
            font_size = 48
        elif size >= 192:
            font_size = 24
        elif size >= 128:
            font_size = 16
        else:
            font_size = 10
        
        # Try to find a system font
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    if position == 'north':
        y_pos = int(center * 0.52)
    elif position == 'south':
        y_pos = int(center * 1.48)
    elif position == 'east':
        x_pos = int(center * 1.48)
    elif position == 'west':
        x_pos = int(center * 0.52)
    else:
        return img
    
    if position == 'north':
        draw.text((center - 5, y_pos), text, fill=color, font=font)
    elif position == 'south':
        draw.text((center - 5, y_pos), text, fill=color, font=font)
    
    return img

def generate_maskable_icon(size):
    """Generate maskable icon with extra padding for Android"""
    # Create larger canvas for maskable (adds safe zone)
    safe_size = int(size * 1.2)
    img = Image.new('RGBA', (safe_size, safe_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = safe_size // 2
    icon_size = int(size * 0.8)
    icon_offset = (safe_size - icon_size) // 2
    
    # Draw background
    draw.ellipse(
        [0, 0, safe_size, safe_size],
        fill=DARK_BG,
        outline=ACCENT,
        width=max(3, int(safe_size * 0.02))
    )
    
    # Draw simplified compass for maskable
    outer_r = int(safe_size * 0.4)
    inner_r = int(safe_size * 0.3)
    
    # North pointer
    north_points = [
        (center, center - outer_r),
        (center + int(outer_r * 0.2), center - int(outer_r * 0.3)),
        (center, center - int(outer_r * 0.15)),
        (center - int(outer_r * 0.2), center - int(outer_r * 0.3))
    ]
    draw.polygon(north_points, fill=ACCENT)
    
    # Center circle
    draw.ellipse(
        [center - inner_r, center - inner_r,
         center + inner_r, center + inner_r],
        fill=DARK_BG,
        outline=ACCENT,
        width=max(3, int(safe_size * 0.02))
    )
    
    # Resize to target size
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def generate_all_icons():
    """Generate all icon sizes"""
    print("\n" + "=" * 60)
    print("🚀 CAMPUS COMPASS - PWA ICON GENERATOR")
    print("=" * 60)
    
    ensure_dir(OUTPUT_DIR)
    
    # Generate standard PNG icons
    print("\n📱 Generating PWA icons...")
    for size in ICON_SIZES:
        output_path = os.path.join(OUTPUT_DIR, f'icon-{size}.png')
        img = draw_compass_icon(size)
        
        # Add N label for larger icons
        if size >= 128:
            img = add_text_to_icon(img, size, 'N', ACCENT, 'north')
        
        img.save(output_path, 'PNG')
        print(f"   Generated: icon-{size}.png")
    
    # Generate favicon PNGs
    print("\n🌐 Generating favicon PNGs...")
    for size in FAVICON_SIZES:
        output_path = os.path.join(OUTPUT_DIR, f'favicon-{size}.png')
        img = draw_compass_icon(size)
        img.save(output_path, 'PNG')
        print(f"   Generated: favicon-{size}.png")
    
    # Generate Apple touch icon
    print("\n🍎 Generating Apple touch icon...")
    for size in APPLE_SIZES:
        output_path = os.path.join(OUTPUT_DIR, f'apple-touch-icon.png')
        img = draw_compass_icon(size)
        img = add_text_to_icon(img, size, 'N', ACCENT, 'north')
        img.save(output_path, 'PNG')
        print(f"   Generated: apple-touch-icon.png")
    
    # Generate maskable icon
    print("\n🤖 Generating Android maskable icon...")
    maskable_path = os.path.join(OUTPUT_DIR, 'maskable-icon.png')
    maskable_img = generate_maskable_icon(MASKABLE_SIZE)
    maskable_img.save(maskable_path, 'PNG')
    print(f"   Generated: maskable-icon.png (512x512 - for Android adaptive)")
    
    # Generate splash screen
    print("\n💧 Generating PWA splash screen...")
    splash_path = os.path.join(OUTPUT_DIR, 'splash-screen.png')
    splash_img = draw_compass_icon(1024)
    splash_img = add_text_to_icon(splash_img, 1024, 'Campus Compass', ACCENT, 'north')
    splash_img.save(splash_path, 'PNG')
    print(f"   Generated: splash-screen.png (1024x1024)")
    
    # Create favicon.ico
    print("\n📌 Creating favicon.ico...")
    ico_path = os.path.join(OUTPUT_DIR, 'favicon.ico')
    images = []
    for size in FAVICON_SIZES:
        png_path = os.path.join(OUTPUT_DIR, f'favicon-{size}.png')
        if os.path.exists(png_path):
            img = Image.open(png_path)
            images.append(img)
    
    if images:
        images[0].save(
            ico_path,
            format='ICO',
            sizes=[(s, s) for s in FAVICON_SIZES],
            append_images=images[1:]
        )
        print(f"   Generated: favicon.ico (includes {FAVICON_SIZES} sizes)")
    
    # Create a simple SVG version for reference
    print("\n💾 Creating SVG reference file...")
    svg_path = os.path.join(OUTPUT_DIR, 'brand-icon.svg')
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="48" fill="#1a1a1a" stroke="#00F0FF" stroke-width="2.5"/>
  <polygon points="50,12 60,45 50,48 40,45" fill="#00F0FF"/>
  <polygon points="50,88 60,55 50,52 40,55" fill="#333"/>
  <polygon points="88,50 55,60 52,50 55,40" fill="#333"/>
  <polygon points="12,50 45,60 48,50 45,40" fill="#333"/>
  <circle cx="50" cy="50" r="10" fill="#0D0D0D" stroke="#00F0FF" stroke-width="2"/>
  <circle cx="50" cy="50" r="3" fill="#00F0FF"/>
  <text x="50" y="26" font-family="Arial" font-size="9" fill="#00F0FF" text-anchor="middle" font-weight="bold">N</text>
</svg>'''
    
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"   Generated: brand-icon.svg")
    
    print("\n" + "=" * 60)
    print("✅ ICON GENERATION COMPLETE!")
    print("=" * 60)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   • PWA icons: {len(ICON_SIZES)} files")
    print(f"   • Favicon files: {len(FAVICON_SIZES) + 1} files (including .ico)")
    print(f"   • Apple Touch icon: 1 file")
    print(f"   • Maskable icon: 1 file")
    print(f"   • Splash screen: 1 file")
    print(f"   • SVG reference: 1 file")
    print(f"\n📁 All files saved to: {OUTPUT_DIR}/")
    
    print("\n📋 Next Steps:")
    print("   1. Verify icons in the static/images/icons/ folder")
    print("   2. Test favicon: http://localhost:5000/static/images/icons/favicon.ico")
    print("   3. Run Lighthouse audit to verify PWA icons")

def cleanup_old_icons():
    """Remove old icon files before generating new ones"""
    if not os.path.exists(OUTPUT_DIR):
        return
    
    response = input("\n⚠️ Delete old icons before generating new ones? (y/n): ")
    if response.lower() == 'y':
        for file in os.listdir(OUTPUT_DIR):
            if file.startswith('icon-') or file.startswith('favicon') or \
               file == 'apple-touch-icon.png' or file == 'maskable-icon.png' or \
               file == 'splash-screen.png' or file == 'brand-icon.svg':
                file_path = os.path.join(OUTPUT_DIR, file)
                os.remove(file_path)
                print(f"   Deleted: {file}")
        print("   Cleanup complete!")

if __name__ == '__main__':
    # Ask if user wants to cleanup old icons
    if os.path.exists(OUTPUT_DIR) and os.listdir(OUTPUT_DIR):
        cleanup_old_icons()
    
    # Generate all icons
    generate_all_icons()
    
    print("\n🎉 Done!")