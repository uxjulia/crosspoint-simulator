# CrossPoint Simulator

A desktop simulator for [CrossPoint](https://github.com/crosspoint-reader/crosspoint-reader)-based firmware. Compiles the firmware natively and renders the e-ink display in an SDL2 window. No device required. Can be used with forks of Crosspoint but any new methods added to the firmware will need to be stubbed.

> [!NOTE]
> **Platform support:** macOS and Linux/WSL use different native compiler and library flags. Start from `sample-platformio-macos.ini` on macOS, or `sample-platformio-linux-wsl.ini` on Linux/WSL. Native Windows is not supported; use WSL and follow the Linux instructions.

> [!WARNING]
> This has been tested on ARM64 macOS (Apple Silicon, M4) and Ubuntu under WSL on Windows. Other platforms may need additional libraries or platform-specific stubs.

## Prerequisites

SDL2 must be installed on the host machine. Linux/WSL users also need OpenSSL development headers for MD5 support.

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

No scripts need to be copied into the firmware repo for the simulator to build. The simulator library automatically patches consumer-side compatibility issues from its own build script when PlatformIO fetches it as a dependency.

If you only want a self-contained simulator dependency, stop there.

If you also want the `Run Simulator` task to appear in the upstream repo's PlatformIO IDE task list (under the "Custom" folder), add one project-level hook in the consuming firmware repo:

For a normal fetched dependency:

```ini
extra_scripts =
  pre:scripts/gen_i18n.py
  pre:scripts/git_branch.py
  pre:scripts/build_html.py
  post:.pio/libdeps/$PIOENV/simulator/run_simulator.py # <-- add this line
```

For a local symlinked dependency:

```ini
extra_scripts =
  pre:scripts/gen_i18n.py
  pre:scripts/git_branch.py
  pre:scripts/build_html.py
  post:../crosspoint-simulator/run_simulator.py # <-- add this line
```

Use the symlink form only when the `Crosspoint` repo and this `crosspoint-simulator` repo are checked out side by side and your `lib_deps` entry is:

```ini
simulator=symlink://../crosspoint-simulator
```

That one `post:` line only exposes the task in the consuming project UI. The actual logic still lives in this simulator repo.


## Setup

Place EPUB books at `./fs_/books/` in the Crosspoint repo's root. This maps to the `/books/` path on the physical SD card.

## Build and run

Run this command from the Crosspoint project after you have added the `[env:simulator]` config to Crosspoint's `platformio.ini` file. Alternatively, if you added the `post:` hook above, you can click "Build" from Platformio's IDE task list and then "Run Simulator" (nested under the "Custom" folder)

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

When the simulator is on the sleep screen, pressing any mapped simulator key wakes it. Under the hood the simulator relaunches itself and reports a synthetic power-button wake, because the native build has no real ESP deep-sleep resume path.

## Notes

**Cache**: On first open of an ebook, an "Indexing..." popup will appear while the section cache is built. If you see rendering issues after a code change that affects layout, delete `./fs_/.crosspoint/` to clear stale caches.

> [!WARNING]
> **Upstream compatibility:** The simulator mirrors interfaces used by Crosspoint. If Crosspoint adds or changes methods in a shared library and the simulator build reaches that code path, the simulator can fail to compile or link until a matching implementation or stub is added here. In many cases this is just a small no-op shim. Open a PR if the change is broadly applicable to CrossPoint-based forks.
