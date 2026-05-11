"""
PlatformIO library build script for the Crosspoint Simulator.

Handles two things automatically when this lib is included as a lib_dep:

1. Patches BookMetadataCache -- SpineEntry::cumulativeSize and its fast read
   path can use size_t, which is 8 bytes on 64-bit hosts (macOS/Linux) but
   4 bytes on ESP32-C3. This mismatch breaks binary cache serialization in the
   simulator. Replaced with uint32_t, which is the correct explicit size on both
   platforms. Applied idempotently -- safe to run on every build.

2. Patches GfxRenderer::setOrientation so simulator builds notify HalDisplay
   when the logical orientation changes. Without this, the framebuffer content
   can rotate while the SDL window keeps its startup portrait/landscape shape.

3. Registers a backward-compatible "run_simulator" custom target.

This file can be loaded more than once in the same PlatformIO process:
- once from this library's `library.json` build hook
- again indirectly when a consuming firmware repo adds the separate
  `run_simulator_project.py` helper for IDE task exposure

Use a process-wide sentinel so the custom target is registered only once even
when multiple registration paths exist.
"""

Import("env")
import os
import builtins
import re

RUN_SIMULATOR_TARGET_KEY = "_crosspoint_run_simulator_target_registered"
RUN_SIMULATOR_TARGET_OWNER_OPTION = "custom_run_simulator_target_owner"


# --- BookMetadataCache patch ---

def _patch_book_metadata_cache(env):
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


_patch_book_metadata_cache(env)


# --- GfxRenderer simulator orientation hook patch ---

def _patch_gfx_renderer_orientation_hook(env):
    header = os.path.join(
        env["PROJECT_DIR"], "lib", "GfxRenderer", "GfxRenderer.h"
    )
    if not os.path.isfile(header):
        return

    with open(header, "r") as f:
        content = f.read()

    if "setSimulatorOrientation(static_cast<int>(o))" in content:
        return

    pattern = re.compile(
        r"(?m)^(?P<indent>\s*)void\s+setOrientation\(\s*(?:const\s+)?"
        r"Orientation\s+o\s*\)\s*\{\s*orientation\s*=\s*o;\s*\}"
    )

    match = pattern.search(content)
    if not match:
        print(
            "Simulator note: could not auto-patch GfxRenderer::setOrientation. "
            "For runtime SDL orientation changes, add a SIMULATOR-only call to "
            "display.setSimulatorOrientation(static_cast<int>(o))."
        )
        return

    indent = match.group("indent")
    replacement = (
        f"{indent}void setOrientation(const Orientation o) {{\n"
        f"{indent}  orientation = o;\n"
        f"#ifdef SIMULATOR\n"
        f"{indent}  display.setSimulatorOrientation(static_cast<int>(o));\n"
        f"#endif\n"
        f"{indent}}}"
    )

    content = content[: match.start()] + replacement + content[match.end() :]

    with open(header, "w") as f:
        f.write(content)
    print("Patched GfxRenderer orientation hook for simulator: %s" % header)


_patch_gfx_renderer_orientation_hook(env)


# --- run_simulator custom target ---

def _run_simulator(source, target, env):
    import subprocess

    binary = env.subst("$BUILD_DIR/program")
    subprocess.run([binary], cwd=os.getcwd())


target_owner = env.GetProjectOption(RUN_SIMULATOR_TARGET_OWNER_OPTION, "").strip().lower()

if target_owner != "project" and not getattr(builtins, RUN_SIMULATOR_TARGET_KEY, False):
    setattr(builtins, RUN_SIMULATOR_TARGET_KEY, True)
    env.AddCustomTarget(
        name="run_simulator",
        dependencies="$PROGPATH",
        actions=_run_simulator,
        title="Run Simulator",
        description="Build and run the desktop simulator",
        always_build=True,
    )
