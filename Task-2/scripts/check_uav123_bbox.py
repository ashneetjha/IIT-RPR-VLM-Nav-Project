from pathlib import Path
from PIL import Image, ImageDraw

image_path = Path(
    "UAV123_10fps/data_seq/UAV123_10fps/group1/000445.jpg"
)

annotation_path = Path(
    "UAV123_10fps/anno/UAV123_10fps/group1_2.txt"
)

output_path = Path(
    "outputs/uav123_group1_2_frame445_bbox.jpg"
)

# Read first annotation row
with annotation_path.open("r") as f:
    first_row = f.readline().strip()

x, y, w, h = map(float, first_row.split(","))

# Open image
image = Image.open(image_path).convert("RGB")

# Convert x, y, width, height -> x1, y1, x2, y2
x1 = x
y1 = y
x2 = x + w
y2 = y + h

# Draw bounding box
draw = ImageDraw.Draw(image)
draw.rectangle(
    [x1, y1, x2, y2],
    outline="red",
    width=5
)

# Save result
output_path.parent.mkdir(parents=True, exist_ok=True)
image.save(output_path)

print("IMAGE:", image_path)
print("IMAGE SIZE:", image.size)
print("ANNOTATION:", first_row)
print("BOX:")
print(f"  x={x}")
print(f"  y={y}")
print(f"  width={w}")
print(f"  height={h}")
print("CONVERTED BOX:")
print(f"  x1={x1}")
print(f"  y1={y1}")
print(f"  x2={x2}")
print(f"  y2={y2}")
print("OUTPUT:", output_path)