#!/usr/bin/env python3
"""Audit the private source library and create web-ready image derivatives."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
except ImportError:  # pragma: no cover - friendly CLI failure
    sys.exit("Pillow is required. Install it with: python3 -m pip install -r requirements-assets.txt")

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "assets" / "asset-manifest.json"
ASSET_ROOT = REPO_ROOT / "assets"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".heic"}
GALLERY_SECTIONS = {"recent-tables", "meal-prep"}
VISUAL_MATCH_LIMIT = 0.05


def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def image_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_image(path: Path) -> Image.Image:
    """Load an image detached from its file, using macOS ImageIO for HEIC when needed."""
    try:
        with Image.open(path) as image:
            return image.copy()
    except (UnidentifiedImageError, OSError) as original_error:
        if path.suffix.lower() != ".heic":
            raise original_error
        with tempfile.TemporaryDirectory() as temp_dir:
            converted = Path(temp_dir) / "converted.png"
            try:
                subprocess.run(
                    ["sips", "-s", "format", "png", str(path), "--out", str(converted)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except (FileNotFoundError, subprocess.CalledProcessError) as error:
                raise OSError(
                    f"Could not decode {path.name}; install HEIC support or convert it to JPEG first"
                ) from error
            with Image.open(converted) as image:
                return image.copy()


def derivative_specs(entry: dict, defaults: dict) -> list[tuple[str, dict]]:
    specs = [(entry["output"], entry)]
    if entry["section"] in GALLERY_SECTIONS:
        gallery_entry = {
            **entry,
            "maxEdge": int(entry.get("galleryMaxEdge", defaults["galleryMaxEdge"])),
            "quality": int(entry.get("galleryQuality", defaults["galleryQuality"])),
        }
        specs.append((f"gallery/{entry['output']}", gallery_entry))
    return specs


def visual_vector_image(original: Image.Image) -> tuple[float, ...]:
    """Return a crop/resize-normalized grayscale vector for derivative matching."""
    image = ImageOps.exif_transpose(original)
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, "white")
        image = Image.alpha_composite(background, rgba).convert("RGB")
    else:
        image = image.convert("RGB")
    image = ImageOps.fit(image, (48, 48), Image.Resampling.LANCZOS).convert("L")
    values = [float(value) for value in image.getdata()]
    mean = statistics.fmean(values)
    spread = math.sqrt(statistics.fmean((value - mean) ** 2 for value in values)) or 1.0
    return tuple((value - mean) / spread for value in values)


def visual_vector(path: Path) -> tuple[float, ...]:
    return visual_vector_image(load_image(path))


def visual_score(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return statistics.fmean((a - b) ** 2 for a, b in zip(left, right))


def audit(verbose: bool = False) -> int:
    manifest = load_manifest()
    source_root = REPO_ROOT / manifest["sourceRoot"]
    sources = image_files(source_root)
    entries = manifest["images"]
    mapped = {entry["source"] for entry in entries}
    ignored = {entry["source"] for entry in manifest.get("ignored", [])}
    found = {relative(path, source_root) for path in sources}

    print(f"Source library: {len(sources)} images")
    print(f"Manifest:       {len(mapped)} mapped, {len(ignored)} intentionally ignored")

    issues = 0
    missing_sources = sorted(mapped - found)
    unmapped_sources = sorted(found - mapped - ignored)
    missing_outputs: list[str] = []

    if missing_sources:
        issues += len(missing_sources)
        print("\nMissing source files:")
        for name in missing_sources:
            print(f"  - {name}")

    if unmapped_sources:
        issues += len(unmapped_sources)
        print("\nNew or unmapped source files:")
        for name in unmapped_sources:
            print(f"  - {name}")

    hashes: dict[str, list[str]] = defaultdict(list)
    for path in sources:
        hashes[file_hash(path)].append(relative(path, source_root))
    duplicate_groups = [names for names in hashes.values() if len(names) > 1]
    print(f"Exact source duplicates: {len(duplicate_groups)} group(s)")
    for names in duplicate_groups:
        print("  - " + " = ".join(names))

    defaults = manifest["defaults"]
    vectors: dict[Path, tuple[float, ...]] = {}
    verified = 0
    expected_derivatives = sum(len(derivative_specs(entry, defaults)) for entry in entries)
    visual_mismatches: list[tuple[str, str, float]] = []
    for entry in entries:
        source = source_root / entry["source"]
        if not source.exists():
            continue
        for output_name, derivative_entry in derivative_specs(entry, defaults):
            output = ASSET_ROOT / output_name
            if not output.exists():
                missing_outputs.append(output_name)
                continue
            try:
                if derivative_entry.get("size") or derivative_entry.get("alphaMask"):
                    source_vector = visual_vector_image(prepare_image(source, derivative_entry, defaults))
                else:
                    vectors.setdefault(source, visual_vector(source))
                    source_vector = vectors[source]
                vectors.setdefault(output, visual_vector(output))
                score = visual_score(source_vector, vectors[output])
            except OSError as error:
                issues += 1
                print(f"Could not compare {entry['source']}: {error}")
                continue
            if score <= VISUAL_MATCH_LIMIT:
                verified += 1
                if verbose:
                    print(f"  match {score:.5f}: {entry['source']} -> assets/{output_name}")
            else:
                visual_mismatches.append((entry["source"], output_name, score))

    if missing_outputs:
        issues += len(missing_outputs)
        print("\nMissing web derivatives (run `python3 scripts/assets.py sync`):")
        for name in missing_outputs:
            print(f"  - assets/{name}")

    if visual_mismatches:
        issues += len(visual_mismatches)
        print("\nMapped files whose source no longer resembles the web derivative:")
        for source, output, score in visual_mismatches:
            print(f"  - {source} -> assets/{output} (score {score:.3f})")
        print("  Review these, then regenerate approved changes with `sync --force`.")

    print(f"Visual source-to-web matches: {verified}/{expected_derivatives} verified")
    if not issues:
        print("Audit clean: every source image is accounted for and every derivative matches.")
    return 1 if issues else 0


def flatten_transparency(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, "white")
        return Image.alpha_composite(background, rgba).convert("RGB")
    return image.convert("RGB")


def prepare_image(source: Path, entry: dict, defaults: dict) -> Image.Image:
    image = flatten_transparency(ImageOps.exif_transpose(load_image(source)))

    if entry.get("size"):
        size = tuple(int(value) for value in entry["size"])
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    else:
        max_edge = int(entry.get("maxEdge", defaults["maxEdge"]))
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)

    if entry.get("alphaMask"):
        with Image.open(ASSET_ROOT / entry["alphaMask"]) as mask_image:
            alpha = mask_image.getchannel("A") if "A" in mask_image.getbands() else mask_image.convert("L")
            if alpha.size != image.size:
                alpha = alpha.resize(image.size, Image.Resampling.LANCZOS)
        image.putalpha(alpha)

    return image


def generate(source: Path, output: Path, entry: dict, defaults: dict) -> tuple[int, int]:
    image = prepare_image(source, entry, defaults)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(
        output,
        "WEBP",
        quality=int(entry.get("quality", defaults["quality"])),
        method=6,
    )
    return image.size


def sync(force: bool = False, section: str | None = None) -> int:
    manifest = load_manifest()
    source_root = REPO_ROOT / manifest["sourceRoot"]
    defaults = manifest["defaults"]
    selected = [
        entry for entry in manifest["images"]
        if section is None or entry["section"] == section
    ]
    if section is not None and not selected:
        sys.exit(f"No manifest entries use section: {section}")

    generated = 0
    skipped = 0
    for entry in selected:
        source = source_root / entry["source"]
        if not source.exists():
            print(f"Missing source, skipped: {entry['source']}")
            continue
        for output_name, derivative_entry in derivative_specs(entry, defaults):
            output = ASSET_ROOT / output_name
            if output.exists() and not force:
                skipped += 1
                continue
            size = generate(source, output, derivative_entry, defaults)
            generated += 1
            print(f"Generated assets/{output_name} ({size[0]}x{size[1]})")

    print(f"Done: {generated} generated, {skipped} existing derivatives left unchanged.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")
    audit_parser = subparsers.add_parser("audit", help="find new, missing, duplicate, or changed source images")
    audit_parser.add_argument("--verbose", action="store_true", help="print every verified source-to-output mapping")
    sync_parser = subparsers.add_parser("sync", help="generate missing WebP derivatives listed in the manifest")
    sync_parser.add_argument("--force", action="store_true", help="also replace existing derivatives")
    sync_parser.add_argument("--section", help="only process one manifest section")
    args = parser.parse_args()

    if args.command in {None, "audit"}:
        return audit(getattr(args, "verbose", False))
    return sync(args.force, args.section)


if __name__ == "__main__":
    raise SystemExit(main())
