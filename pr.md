1. Overview
This PR represents a complete modernization of the AM32 build infrastructure. It transitions the project from a legacy Makefile setup to a modular CMake architecture.

The goal is to solve long-standing issues with incremental builds, cross-platform compatibility (Windows/Linux/macOS), and IDE integration, while introducing "industrial-grade" CI/CD pipelines similar to modern firmware projects like Betaflight.

2. Problem Statement & Motivation
The existing build system served the project well but has accumulated several technical debts:

No Incremental Builds: The current Makefile passes all sources to GCC in a single command. This forces a full recompilation of every file even if only one line is changed, slowing down the development loop significantly.

Fragile Tooling: The dependency on shell tools (uname, cut, grep) creates friction on Windows (requiring MinGW/Cygwin) and complicates CI setup.

Broken IDE Support: Modern editors like VSCode rely on compile_commands.json for Intellisense. The current makefile cannot generate this, leading to broken navigation ("Go to Definition") and false error reporting.

Monolithic Configuration: Adding new targets requires editing a central file, increasing the risk of merge conflicts and breaking existing targets.

3. Solution: The "Industrial Pro" CMake Architecture
This PR introduces a structured, modular CMake system:

A. Modular Target Definition
Old Way: A complex define macro inside one large Makefile.

New Way: Each MCU target (e.g., F051, V203) has its own isolated configuration file in cmake/targets/.

Benefit: Adding a new target is now copy-paste safe and isolated. If the F421 config is broken, it won't prevent F051 from building.

B. True Incremental Compilation
Mechanism: CMake compiles sources to object files (.o) individually using Ninja.

Benefit: Changing main.c re-compiles only main.c and re-links. Rebuild times drop from seconds to milliseconds.

C. Native VSCode Integration
Mechanism: The build system automatically generates compile_commands.json and .vscode/launch.json.

Benefit: Developers get perfect Intellisense immediately. Debugging configurations (OpenOCD/SVD paths) are auto-generated for every target—just select "Debug F051" and click Play.

D. Toolchain Management (manage_tools.cmake)
Mechanism: A dedicated script automatically downloads the correct ARM GCC and RISC-V GCC versions into a local tools/ folder.

Benefit: "It works on my machine" is solved. CI and local developers use the exact same compiler version, regardless of OS.

4. New CI/CD Pipelines (GitHub Actions)
This PR upgrades the GitHub Actions workflow to be more robust and informative:

Bloat Watchdog: A bot now comments on every PR with a Size Report, showing the Flash/RAM usage difference for every target compared to main.

Nightly Builds: Automated nightly releases provide users with the latest features without waiting for stable tags.

Code Quality:

Clang-Format: Enforces consistent code style.

CodeQL: Scans for security vulnerabilities (buffer overflows, logic errors).

Release Automation: Pushing a git tag (e.g., v1.98) automatically builds, signs, zips, checksums, and creates a Draft Release for final review.


5. Developer Experience Improvements
One-Command Flash: cmake --build build --target flash_AM32_F051... flashes the board directly.

Static Analysis: clang-tidy runs during compilation to catch bugs early.

Documentation: A doc target generates HTML documentation from code comments via Doxygen.

Reproducible Builds: Timestamps and user paths are stripped from the binary to ensure bit-perfect reproducibility.

6. Verification
I have tested this on my fork across Windows (PowerShell) and Linux (Ubuntu):

[x] All targets (ARM & RISC-V) build successfully.

[x] .hex output sizes match the legacy makefile builds.

[x] VSCode debugging attaches correctly with SVD peripheral view.

[x] CI pipelines pass (Build, Style, Size Report).


AM32/
├── CMakeLists.txt                  # Main cmakeLists
└── cmake/
    ├── modules/                    # Logic (Compiler flags, Signing, Launch Gen)
    ├── targets/                    # Data (F051.cmake, F421.cmake, etc.)
    ├── toolchains/                 # Cross-compile definitions
    └── manage_tools.cmake          # Tool downloader