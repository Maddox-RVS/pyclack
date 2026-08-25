# pyclack

**pyclack** is a Python port of [Clack](https://github.com/bombshell-dev/clack), the beautiful and minimal command-line prompt library for JavaScript, originally created by [Nate Moore (@natemoo-re)](https://github.com/natemoo-re).

pyclack brings Clack's interactive prompts, terminal UI components, and styling to Python while maintaining the same philosophy of providing a simple API for building beautiful command-line applications.

> [!NOTE]
> pyclack is an independent Python implementation inspired by Clack. It is not affiliated with or maintained by the Clack/Bombshell project.

![pyclack demo](assets/pyclack-demo.gif)

I miss-spelled "writing" 😔, but I'm too lazy to re-record and edit this GIF again so deal with it...

## Features

- Interactive prompts for text input, multiline input, passwords, confirmations, selections, autocomplete, dates, and filesystem paths
- Synchronous and asynchronous APIs
- Animated spinners and progress bars
- Streaming output
- Task logging and semantic logging
- Intro, outro, cancellation, notes, and boxed messages
- Cross-platform terminal support for Windows, Linux, and macOS
- Terminal cursor, echo, and keyboard input control
- Customizable themes and symbols
- Reusable terminal rendering system
- Type-safe Python API with bundled type information

# Installation & Setup

## Quick Start (Recommended)

The easiest way to get started with pyclack is via pip or uv. These methods will install the latest stable version directly into your active environment.

**Using pip:**  
```bash
pip install pyclack
```

**Using uv** (recommended for fast virtual environment management):   
```bash
uv add pyclack
```

### Developer Installation & Local Development Build

> **Prerequisites:**
> - uv (needed to manage project enviornment and to run the project)

If you are developing with the repository and need to test changes locally, follow these steps. This process uses uv sync to ensure your virtual environment is perfectly synchronized with the project's dependencies.

1). Clone the Repository:
```bash
git clone https://github.com/Maddox-RVS/pyclack.git
cd pyclack
```
2). Create and Sync Virtual Environment:
This command reads the project's dependency definitions in `pyproject.toml` and sets up a
pristine, isolated virtual environment based on those requirements.
```bash
uv sync --frozen
```
3). Run the Project:
You can now run the application using the local package installation:
```bash
uv run examples/my_pyclack_text_script.py
```
