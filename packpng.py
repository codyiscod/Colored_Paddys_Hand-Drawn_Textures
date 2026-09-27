# This script was pretty much entirely made with AI
# because I couldn't be bothered coding it lol

from PIL import Image, ImageDraw, ImageEnhance
from pathlib import Path
import numpy as np



# output image resolution
OUTPUT_SIZE = (512, 512)

# cube
CUBE_X = 256
CUBE_Y = 64
CUBE_SCALE = 2

# sides
TOP_WIDTH = 200
TOP_HEIGHT = 96
SIDE_HEIGHT = 256
LEFT_DARKNESS = 0.5
RIGHT_DARKNESS = 0.25

# BORDER_WIDTH = 1
# BORDER_OPACITY = 0

# how far down the side faces begin
SIDE_TOP_OFFSET = TOP_HEIGHT


# PERSPECTIVE TRANSFORM
def perspective_transform(texture, destination, size):
    """Map a rectangular texture onto a four-point polygon."""

    src_w, src_h = texture.size

    src = np.array([
        [0, 0],
        [src_w, 0],
        [src_w, src_h],
        [0, src_h]
    ], dtype=float)

    dst = np.array(destination, dtype=float)

    A = []
    B = []

    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u*x, -u*y])
        B.append(u)

        A.append([0, 0, 0, x, y, 1, -v*x, -v*y])
        B.append(v)

    coefficients = np.linalg.solve(
        np.array(A),
        np.array(B)
    )

    transformed = Image.new("RGBA", size)

    transformed.paste(
        texture.transform(
            size,
            Image.Transform.PERSPECTIVE,
            coefficients,
            resample=Image.Resampling.BICUBIC
        )
    )

    return transformed



def make_packpng(COLORED_PACK, COLORED_ASSETS):
    SIDE_TEXTURE = (COLORED_ASSETS / "minecraft" / "textures" / "block" / "barrel_side.png")
    TOP_TEXTURE = (COLORED_ASSETS / "minecraft" / "textures" / "block" / "barrel_top.png")
    image = Image.new("RGBA", OUTPUT_SIZE, "white") # make canvas


    # load textures
    side_texture = Image.open(SIDE_TEXTURE).convert("RGBA")
    top_texture = Image.open(TOP_TEXTURE).convert("RGBA")


    # calculate cube geometry
    size = TOP_WIDTH * CUBE_SCALE
    top_height = TOP_HEIGHT * CUBE_SCALE
    side_height = SIDE_HEIGHT * CUBE_SCALE
    side_top_offset = SIDE_TOP_OFFSET * CUBE_SCALE

    cx = CUBE_X
    cy = CUBE_Y

    top = (cx, cy - top_height)
    left = (cx - size, cy)
    right = (cx + size, cy)
    bottom = (cx, cy + top_height)

    # bottom of the cube
    left_bottom = (cx - size, cy + side_height)
    right_bottom = (cx + size, cy + side_height)
    bottom_bottom = (cx, cy + side_height + top_height)



    # LEFT FACE
    left_face = [
        (cx, cy + side_top_offset),
        left,
        left_bottom,
        bottom_bottom
    ]
    left_texture = perspective_transform(
        side_texture,
        left_face,
        image.size
    )
    left_texture = ImageEnhance.Brightness(left_texture).enhance(1.0 - LEFT_DARKNESS) # brightness

    # mask
    mask = Image.new("L", image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(left_face, fill=255)
    image.paste(left_texture, (0, 0), mask)



    # RIGHT FACE
    right_face = [
        (cx, cy + side_top_offset),
        right,
        right_bottom,
        bottom_bottom
    ]
    right_texture = perspective_transform(
        side_texture,
        right_face,
        image.size
    )
    right_texture = ImageEnhance.Brightness(right_texture).enhance(1.0 - RIGHT_DARKNESS) # brightness

    # mask
    mask = Image.new("L",image.size,0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(right_face,fill=255)
    image.paste(right_texture, (0, 0),  mask)



    # TOP FACE
    top_face = [
        top,
        right,
        bottom,
        left
    ]
    top_texture_image = perspective_transform(
        top_texture,
        top_face,
        image.size
    )

    # mask
    mask = Image.new("L", image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(top_face, fill=255)
    image.paste(top_texture_image, (0, 0), mask)



    # BORDER
    # border = Image.new("RGBA", OUTPUT_SIZE, (0, 0, 0, 0))
    # border_draw = ImageDraw.Draw(border)
    # border_alpha = int(255 * BORDER_OPACITY)
    # border_color = (0, 0, 0, border_alpha)

    # border_draw.line([top, right, bottom, left, top], fill=border_color, width=BORDER_WIDTH, joint="curve")
    # border_draw.line([left, left_bottom], fill=border_color, width=BORDER_WIDTH)
    # border_draw.line([right, right_bottom], fill=border_color, width=BORDER_WIDTH)
    # border_draw.line([left_bottom, bottom_bottom, right_bottom], fill=border_color, width=BORDER_WIDTH, joint="curve")
    # border_draw.line([(cx, cy + side_top_offset), bottom_bottom], fill=border_color, width=BORDER_WIDTH)

    # image = Image.alpha_composite(image, border)



    # show/save
    # image.show()
    image.save(COLORED_PACK / "pack.png")