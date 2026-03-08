"""
Create a simple placeholder icon for NetScan
"""

from PIL import Image, ImageDraw

# Create a 256x256 icon
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a rounded rectangle background (dark blue)
padding = 20
draw.rounded_rectangle(
    [padding, padding, size - padding, size - padding],
    radius=40,
    fill=(30, 60, 120, 255)
)

# Draw WiFi signal arcs (white)
center_x = size // 2
center_y = size // 2 + 20

# Arcs for WiFi signal
for i, radius in enumerate([40, 65, 90, 115]):
    width = 8 - (i * 1.5)
    bbox = [
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius
    ]
    draw.arc(
        bbox,
        start=200,
        end=340,
        fill=(255, 255, 255, 255),
        width=int(width)
    )

# Draw center dot
dot_radius = 12
draw.ellipse(
    [
        center_x - dot_radius,
        center_y - dot_radius,
        center_x + dot_radius,
        center_y + dot_radius
    ],
    fill=(255, 255, 255, 255)
)

# Draw antenna line at bottom
draw.rectangle(
    [center_x - 4, center_y + 30, center_x + 4, center_y + 80],
    fill=(255, 255, 255, 255)
)

# Save as PNG first (easier to create)
img.save('assets/icon.png', 'PNG')

# Create multiple sizes for ICO
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
images = []

for size in sizes:
    resized = img.resize(size, Image.Resampling.LANCZOS)
    images.append(resized)

# Save as ICO if possible
try:
    images[0].save(
        'assets/icon.ico',
        format='ICO',
        sizes=sizes,
        append_images=images[1:]
    )
    print("Icon created successfully: assets/icon.ico")
except Exception as e:
    print(f"Could not create ICO file: {e}")
    print("PNG icon saved: assets/icon.png")
    print("You can convert PNG to ICO using online tools.")
