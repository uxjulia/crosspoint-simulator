# CrossPoint Simulator

A desktop simulator for [CrossPoint](https://github.com/crosspoint-reader/crosspoint-reader)-based firmware. Compiles the firmware natively and renders the e-ink display in an SDL2 window — no device required.

> **Platform support:** macOS and Linux/WSL use different native compiler and library flags. Start from `sample-platformio-macos.ini` on macOS, or `sample-platformio-linux-wsl.ini` on Linux/WSL. Native Windows is not supported; use WSL and follow the Linux instructions.

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

Add the simulator to your firmware's platformio.ini as a lib_dep and configure the [env:simulator] environment. Use the sample file for your host OS:

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
  post:.pio/libdeps/$PIOENV/simulator/run_simulator.py
```

For a local symlinked dependency:

```ini
extra_scripts =
  pre:scripts/gen_i18n.py
  pre:scripts/git_branch.py
  pre:scripts/build_html.py
  post:../crosspoint-simulator/run_simulator.py
```

Use the symlink form only when your firmware repo and `crosspoint-simulator` repo are checked out side by side and your `lib_deps` entry is:

```ini
simulator=symlink://../crosspoint-simulator
```

That one `post:` line only exposes the task in the consuming project UI. The actual logic still lives in this simulator repo.

For local development, replace the git reference with a symlink after you've cloned the repository:

```ini
simulator=symlink://../crosspoint-simulator
```

If you also want the PlatformIO IDE `Run Simulator` task while using that symlink, point `post:` at the real sibling-repo script path:

```ini
post:../crosspoint-simulator/run_simulator.py
```

## Setup

Place EPUB books at `./fs_/books/` relative to the project root. This maps to the `/books/` path on the physical SD card.

## Build and run

The simulator is a desktop GUI app, but it is still launched by a normal command. The CLI command builds the native binary and then starts the SDL window.

```bash
pio run -e simulator
.pio/build/simulator/program
```

Or use the custom PlatformIO target to build and run in one step:

```bash
pio run -e simulator -t run_simulator
```

If the IDE task is wired in via the optional `post:` hook above, clicking `Run Simulator` does the same thing as that command: it launches the GUI window, not a text-mode simulation.

## Controls

| Key    | Action                             |
| ------ | ---------------------------------- |
| ↑ / ↓  | Page back / forward (side buttons) |
| ← / →  | Left / right front buttons         |
| Return | Confirm / Select                   |
| Escape | Back                               |
| P      | Power                              |

## Notes

**Cache**: On first open of an ebook, an "Indexing..." popup will appear while the section cache is built. If you see rendering issues after a code change that affects layout, delete `./fs_/.crosspoint/` to clear stale caches.

**HAL compatibility:** The simulator implements the HAL interface defined in `lib/hal/*.h`. If your firmware adds a new method to a HAL class and calls it, the simulator will fail to link until a matching stub is added to the relevant Hal\*.cpp here. For most cases this is a one-liner no-op. Open a PR if the change is applicable to all CrossPoint-based forks.
