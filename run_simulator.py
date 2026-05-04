"""
PlatformIO library build script for the Crosspoint Simulator.

Handles two things automatically when this lib is included as a lib_dep:

1. Patches BookMetadataCache — SpineEntry::cumulativeSize and its fast read
   path can use size_t, which is 8 bytes on 64-bit hosts (macOS/Linux) but
   4 bytes on ESP32-C3. This mismatch breaks binary cache serialization in the
   simulator. Replaced with uint32_t, which is the correct explicit size on both
   platforms. Applied idempotently — safe to run on every build.

2. Registers a backward-compatible "run_simulator" custom target.

This file can be loaded more than once in the same PlatformIO process:
- once from this library's `library.json` build hook
- again from a consuming firmware repo's `post:` extra_script for IDE task exposure

Use a process-wide sentinel so the custom target is registered only once even
when both paths load the script.
"""

Import("env")
import os


# --- BookMetadataCache patch ---

def _patch_book_metadata_cache(source, target, env):
    header = os.path.join(
        env["PROJECT_DIR"], "lib", "Epub", "Epub", "BookMetadataCache.h"
    )
    if os.path.isfile(header):
        _apply_header_patch(header)

    source = os.path.join(
        env["PROJECT_DIR"], "lib", "Epub", "Epub", "BookMetadataCache.cpp"
    )
    if os.path.isfile(source):
        _apply_source_patch(source)


def _apply_header_patch(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    original = content

    # lutOffset is a member variable written as uint32_t in buildBookBin but
    # declared as size_t, which is 8 bytes on 64-bit hosts. load() reads
    # sizeof(lutOffset) bytes, so an 8-byte read shifts the file position and
    # corrupts the spineCount/tocCount fields that follow.
    content = content.replace(
        "  size_t lutOffset;",
        "  uint32_t lutOffset; // simulator patch",
        1,
    )

    content = content.replace(
        "    size_t cumulativeSize;",
        "    uint32_t cumulativeSize; // simulator patch",
        1,
    )
    content = content.replace("const size_t cumulativeSize", "const uint32_t cumulativeSize")

    if content == original:
        return  # nothing to patch

    with open(filepath, "w") as f:
        f.write(content)
    print("Patched BookMetadataCache header: size_t -> uint32_t for simulator: %s" % filepath)


def _apply_source_patch(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    original = content

    # getSpineCumulativeSize() skips directly to the stored cumulativeSize
    # field. Once the header is patched, that field is a 4-byte uint32_t; the
    # fast read path must use the same width or a 64-bit host will over-read
    # into the following tocIndex bytes and inflate book progress.
    content = content.replace(
        "  size_t cumulativeSize = 0;\n"
        "  serialization::readPod(bookFile, cumulativeSize);\n"
        "  return cumulativeSize;",
        "  uint32_t cumulativeSize = 0; // simulator patch\n"
        "  serialization::readPod(bookFile, cumulativeSize);\n"
        "  return cumulativeSize;",
        1,
    )

    if content == original:
        return  # nothing to patch

    with open(filepath, "w") as f:
        f.write(content)
    print("Patched BookMetadataCache source: size_t -> uint32_t for simulator: %s" % filepath)

env.AddPreAction("$BUILD_DIR/program", _patch_book_metadata_cache)


# --- run_simulator custom target ---
env.AddCustomTarget(
    name="run_simulator",
    dependencies="$BUILD_DIR/program",
    actions="$BUILD_DIR/program",
    title="Run Simulator",
    description="Build and run the desktop simulator",
    always_build=True,
)
