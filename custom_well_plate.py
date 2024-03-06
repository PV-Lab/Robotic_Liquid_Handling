Z_HEIGHT = 40

origin = (16, 68, Z_HEIGHT)
plate_coords = {}
for letter, row in zip("ABC", range(3)):
    for col in range(5):
        plate_coords[f"{letter}{1 + col}"] = (16 + 23 * col, 68 - 23 * row, Z_HEIGHT)

print(plate_coords)


# NOTE these coordinates are relative to deck slot 1 specifically. In order to get general coordinates,
# either subtract the distances between well centers or solve for the size of the plates w/ the labware
# creator