"""Real FFmpeg normalization checks for image safety and orientation."""

from pathlib import Path

import pytest
from PIL import Image

from oc_worker.ffmpeg import extract_image_frame


def test_transparency_is_flattened_to_white(tmp_path: Path) -> None:
    source = tmp_path / "transparent.png"
    image = Image.new("RGBA", (120, 80), (255, 0, 0, 0))
    image.putpixel((60, 40), (0, 0, 255, 255))
    image.save(source)
    output = tmp_path / "normalized.jpg"

    extract_image_frame(source, output)

    normalized = Image.open(output)
    assert normalized.mode == "RGB"
    assert normalized.getpixel((0, 0)) == pytest.approx((255, 255, 255))


def test_exif_orientation_is_applied(tmp_path: Path) -> None:
    source = tmp_path / "phone-photo.jpg"
    image = Image.new("RGB", (80, 40), "red")
    exif = Image.Exif()
    exif[274] = 6
    image.save(source, exif=exif)
    output = tmp_path / "oriented.jpg"

    extract_image_frame(source, output)

    normalized = Image.open(output)
    assert normalized.size == (40, 80)
    assert normalized.getexif().get(274) is None
