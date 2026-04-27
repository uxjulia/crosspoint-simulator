"""
PlatformIO library build script for the Crosspoint Simulator.

Handles two things automatically when this lib is included as a lib_dep:

1. Patches BookMetadataCache.h — SpineEntry::cumulativeSize is declared as
   size_t, which is 8 bytes on 64-bit hosts (macOS/Linux) but 4 bytes on
   ESP32-C3.  This mismatch breaks binary cache serialization in the simulator.
   Replaced with uint32_t, which is the correct explicit size on both platforms.
   Applied idempotently — safe to run on every build.

2. Registers a "run_simulator" custom target so the compiled binary can be
   launched directly from PlatformIO.

Important limitation: when this file is loaded only through library.json as a
library build hook, PlatformIO CLI can use the target, but the consuming
project's IDE task list may not show it. To expose "Run Simulator" in the
PlatformIO IDE UI, the consuming firmware repo still needs a tiny project-level
post: extra_script pointing at this file inside .pio/libdeps/$PIOENV/simulator.
"""

Import("env")
import os, subprocess


# --- BookMetadataCache patch ---

def _patch_book_metadata_cache(env):
    target = os.path.join(
        env["PROJECT_DIR"], "lib", "Epub", "Epub", "BookMetadataCache.h"
    )
    if os.path.isfile(target):
        _apply_patch(target)


def _apply_patch(filepath):
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
    print("Patched BookMetadataCache: size_t -> uint32_t for simulator: %s" % filepath)


_patch_book_metadata_cache(env)


# --- run_simulator custom target ---

def _run_simulator(source, target, env):
    binary = env.subst("$BUILD_DIR/program")
    subprocess.run([binary], cwd=os.getcwd())


env.AddCustomTarget(
    name="run_simulator",
    dependencies=None,
    actions=_run_simulator,
    title="Run Simulator",
    description="Build and run the desktop simulator",
    always_build=True,
)
