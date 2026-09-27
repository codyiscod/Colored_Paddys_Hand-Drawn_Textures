# This script was made without AI, except for debugging a few errors

from pathlib import Path
from PIL import Image, ImageChops
from packpng import make_packpng
import shutil

SCRIPT_DIR = Path(__file__).parent.resolve()

MC_PACK = SCRIPT_DIR / "minecraft-assets"
PADDY_PACK = SCRIPT_DIR / "Paddy's_Hand-Drawn_Textures_26.1_v0.11wip"
COLORED_PACK = SCRIPT_DIR / f"Colored_{PADDY_PACK.name}"

MC_ASSETS = MC_PACK / "assets"
PADDY_ASSETS = PADDY_PACK / "assets"
COLORED_ASSETS = COLORED_PACK / "assets"


asset_count = 0

# loop through all assets
for paddy_asset in PADDY_ASSETS.rglob("*.png"):
    # find matching MC asset
    relative_path = paddy_asset.relative_to(PADDY_ASSETS)
    mc_asset = MC_ASSETS / relative_path

    if not mc_asset.exists():
        print(f"Skipping (no MC asset): {relative_path}")
        continue

    # open, convert, and resize images
    paddy = Image.open(paddy_asset).convert("RGBA")
    mc = Image.open(mc_asset).convert("RGBA").resize(paddy.size, Image.Resampling.NEAREST)

    # mask them together
    mask = ImageChops.multiply(paddy.getchannel("A"), mc.getchannel("A"))
    result = ImageChops.multiply(paddy.convert("RGB"), mc.convert("RGB")).convert("RGBA")
    result.putalpha(mask)

    # save using the same folder structure
    colored_asset = COLORED_ASSETS / relative_path
    colored_asset.parent.mkdir(parents=True, exist_ok=True)
    result.save(colored_asset)

    print(f"Created: {colored_asset}")
    asset_count += 1


# make pack.png & pack.mcmeta
make_packpng(COLORED_PACK, COLORED_ASSETS)
shutil.copyfile(PADDY_PACK / "pack.mcmeta", COLORED_PACK / "pack.mcmeta")

input(f"Converted {asset_count} assets! Press Enter to exit")