# Marginalia Simulator

A desktop simulator for [Marginalia](https://github.com/marginalia-os/marginalia-firmware)-based firmware. Compiles the firmware natively and renders the e-ink display in an SDL2 window. No device required. This fork keeps compatibility with inherited firmware APIs where those identifiers still exist in the codebase.

> [!NOTE]
> **Platform support:** macOS and Linux/WSL use different native compiler and library flags. Start from `sample-platformio-macos.ini` on macOS, or `sample-platformio-linux-wsl.ini` on Linux/WSL. Native Windows is not supported; use WSL and follow the Linux instructions.

> [!WARNING]
> This has been tested on ARM64 macOS (Apple Silicon, M4) and Ubuntu under WSL on Windows. Other platforms may need additional libraries or platform-specific stubs.

## Prerequisites

SDL2 and `curl` must be installed on the host machine. Linux/WSL users also need OpenSSL development headers for MD5 support.

```bash
# macOS
brew install sdl2

# Linux — Debian/Ubuntu (including WSL)
sudo apt install libsdl2-dev libssl-dev

# Linux — Fedora/RHEL
sudo dnf install SDL2-devel openssl-devel

# Linux — Arch
sudo pacman -S sdl2 openssl
```

## Integration

Add the simulator to your firmware's platformio.ini as a `lib_dep` and configure the `[env:simulator]` environment. Use the sample file for your host OS:

- `sample-platformio-macos.ini`
- `sample-platformio-linux-wsl.ini`

No scripts need to be copied into the firmware repo for the simulator to build. The simulator library automatically patches consumer-side compatibility issues from its own build script when PlatformIO fetches it as a dependency, including the common `GfxRenderer::setOrientation()` hook needed for SDL window resizing.

Keep the sample `build_src_filter` exclusions unless your firmware has already moved those files behind simulator guards. In the current inherited firmware layout, the simulator library supplies the host-side file-transfer and update shims while the lower-level `WebServer`, `WebSocketsServer`, and `NetworkClient` shims let shared network routes run on the desktop build.

The simulator defaults to the X4 panel shape. To simulate X3, add `-DSIMULATOR_DEVICE_X3` to the consuming firmware's simulator `build_flags`. That switches the framebuffer to 792x528 landscape, reports `gpio.deviceIsX3()` as true, and exposes the simulator tilt sensor by default.

If a fork has a custom renderer and the auto-patch cannot recognize it, its simulator build should notify the display when orientation changes:

```cpp
#ifdef SIMULATOR
display.setSimulatorOrientation(static_cast<int>(o));
#endif
```

Put that in the renderer's orientation setter after updating the renderer's own orientation state.
By default, the simulator keeps its own `JPEGDEC`, `PNGdec`, and QRCode compatibility shims so existing firmware projects can update this library without changing their simulator environment. To test against the native decoder libraries instead, follow the opt-in comments in the sample PlatformIO files: define `MARGINALIA_SIM_USE_NATIVE_DECODERS`, set `lib_compat_mode = off`, change simulator `lib_ignore` to `hal, WebSockets`, and add the native `PNGdec`/`JPEGDEC` dependencies. `WebSockets` is ignored only in native simulator builds because this repo supplies the host-backed `WebSocketsServer` implementation.

If you only want a self-contained simulator dependency, stop there.

If you also want the `Run Simulator` task to appear in the consuming repo's PlatformIO IDE task list (under the "Custom" folder), let the consuming project own the IDE task registration. Add `custom_run_simulator_target_owner = project` to `[env:simulator]`, then add one project-level hook:

For a normal fetched dependency:

```ini
custom_run_simulator_target_owner = project

extra_scripts =
  pre:scripts/gen_i18n.py
  pre:scripts/git_branch.py
  pre:scripts/build_html.py
  post:.pio/libdeps/$PIOENV/simulator/run_simulator_project.py
```

For a local symlinked dependency:

```ini
custom_run_simulator_target_owner = project

extra_scripts =
  pre:scripts/gen_i18n.py
  pre:scripts/git_branch.py
  pre:scripts/build_html.py
  post:../marginalia-simulator/run_simulator_project.py
```

Use the symlink form only when the `marginalia-firmware` repo and this `marginalia-simulator` repo are checked out side by side and your `lib_deps` entry is:

```ini
simulator=symlink://../marginalia-simulator
```

The `custom_run_simulator_target_owner = project` line tells the library-side hook not to register the same launcher a second time. Without that, closing one simulator window can immediately relaunch another because both the library hook and the project hook try to own `run_simulator`.

Do not point `post:` at `run_simulator.py` directly. That file is already auto-loaded via `library.json` and is the backward-compatible library hook.

The `post:` line above only exposes the task in the consuming project UI. The actual launcher logic still lives in this simulator repo.


## Setup

Place EPUB books at `./fs_/books/` in the Marginalia firmware repo's root. This maps to the `/books/` path on the physical SD card.

## Build and run

Run this command from the Marginalia firmware project after you have added the `[env:simulator]` config to `platformio.ini`. Alternatively, if you added the project hook above, you can click "Build" from PlatformIO's IDE task list and then "Run Simulator" (nested under the "Custom" folder).

```bash
pio run -e simulator -t run_simulator
```

## Controls

| Key    | Action                             |
| ------ | ---------------------------------- |
| ↑ / ↓  | Page back / forward (side buttons) |
| ← / →  | Left / right front buttons         |
| Return | Confirm / Select                   |
| Escape | Back                               |
| P      | Power                              |
| S      | Simulate sleep                     |

When the simulator is on the sleep screen, pressing any mapped simulator key wakes it. Under the hood the simulator relaunches itself and reports a synthetic power-button wake, because the native build has no real ESP deep-sleep resume path.

## Notes

**Host-backed network flows**: OPDS/catalog downloads and KOReader sync use the
host's `curl` binary through simulator implementations of `HTTPClient` and
`esp_http_client`. This keeps the firmware code path intact while allowing the
desktop build to reach real HTTP/HTTPS services.

**Mocked downloads**: Set `MARGINALIA_SIM_HTTP_MOCK_ROOT` to a folder of local
fixtures to make host-backed HTTP requests return local files by basename before
falling back to the real network. This is useful for SD-font testing because the
firmware can request its normal release URLs while the simulator serves a local
`fonts.json` and `.cpfont` files:

```bash
cd /path/to/firmware
python3 -m pip install -r lib/EpdFont/scripts/requirements.txt
python3 lib/EpdFont/scripts/build-sd-fonts.py \
  --only NotoSansExtended \
  --manifest \
  --base-url "https://github.com/marginalia-os/marginalia-fonts/releases/download/local/"
MARGINALIA_SIM_HTTP_MOCK_ROOT="$PWD/lib/EpdFont/scripts/output" \
  pio run -e simulator -t run
```

The mock still uses the firmware's normal manifest parsing, file download,
write-to-SD, `.cpfont` validation, registry refresh, and font-selection flow.

**File transfer**: The simulator provides host-backed `WebServer`,
`WebSocketsServer`, and `NetworkClient` shims so firmware-owned file-transfer
routes can run on the host. Firmware web servers that bind port 80 are exposed
on `http://127.0.0.1:8080/`; WebSocket servers that bind port 81 are exposed on
`ws://127.0.0.1:8081/`. This supports the browser file manager, WebSocket upload
progress, streamed downloads, and common WebDAV-style requests such as
`OPTIONS`, `PROPFIND`, `PUT`, `DELETE`, `MKCOL`, `MOVE`, and `COPY`. WebDAV
`LOCK` and `UNLOCK` remain compatibility-only unless the firmware implements
locking semantics.

**Firmware updates**: OTA and SD-card firmware flashing are non-destructive in
the simulator. The simulator stubs those update paths so the UI can be opened
without flashing firmware or changing boot partitions.

**Image previews**: The default simulator shims decode JPEG and PNG files on the
host and render a rough grayscale preview through the firmware's normal image
callbacks. This is meant to make image pages and PNG sleep overlays visible
while testing desktop flows. Native decoder libraries can be enabled with the
sample config's opt-in flags when decoder compatibility matters more than the
self-contained default. Neither mode simulates device-specific e-ink image
quality, refresh behaviour, or memory pressure.

**Cache**: On first open of an ebook, an "Indexing..." popup will appear while the section cache is built. If you see rendering issues after a code change that affects layout, delete `./fs_/.crosspoint/` to clear stale legacy caches. Package state lives under `./fs_/.marginalia/`.

> [!WARNING]
> **Upstream compatibility:** The simulator mirrors interfaces used by Marginalia and its inherited base. If firmware adds or changes methods in a shared library and the simulator build reaches that code path, the simulator can fail to compile or link until a matching implementation or stub is added here. In many cases this is just a small no-op shim. Open a PR if the change is broadly applicable.
