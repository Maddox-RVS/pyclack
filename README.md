# pyclack

**pyclack** is a Python port of [Clack](https://github.com/bombshell-dev/clack), the beautiful and minimal command-line prompt library for JavaScript, originally created by [Nate Moore (@natemoo-re)](https://github.com/natemoo-re).

pyclack brings Clack's interactive prompts, terminal UI components, and styling to Python while maintaining the same philosophy of providing a simple API for building beautiful command-line applications.

> [!NOTE]
> pyclack is an independent Python implementation inspired by Clack. It is not affiliated with or maintained by the Clack/Bombshell project.

![pyclack demo](assets/pyclack-demo.gif)

I miss-spelled "writing" 😔, but I'm too lazy to re-record and edit this GIF again so deal with it...

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

---

# Documentation

pyclack is divided into two main concepts:

- **Prompts** interact with the user and return a value.
- **Widgets** render information to the terminal and generally return `None`.

The synchronous APIs live under `pyclack.prompts` and `pyclack.widgets`.

Asynchronous wrappers are provided under `pyclack.prompts_asyc` and `pyclack.widgets_asyc`. The `asyc` spelling is part of the current package API.

---

# Prompts

All prompts block until the user submits, cancels, or an `abort_time` expires.

A successful prompt returns its documented value.

A cancelled prompt raises `CancelException` rather than returning a special sentinel value.

## Prompt overview

| Prompt | Purpose | Successful return |
| --- | --- | --- |
| `ask()` | Single-line text input | `str` |
| `password()` | Hidden text input | `str` |
| `confirm()` | Yes/no confirmation | `bool` |
| `pick_date()` | Date selection within a range | `date` |
| `multiline()` | Multi-line text input | `str` |
| `select()` | Single selection from options | `ClackOption[T]` |
| `multiselect()` | Multiple selection from options | `list[ClackOption[T]]` |
| `autocomplete()` | Filtered single selection | `ClackOption[T]` |
| `autocomplete_multiselect()` | Filtered multiple selection | `list[ClackOption[T]]` |
| `select_key()` | Selection by pressing a key | `ClackOption[str]` |
| `select_path()` | Filesystem path selection | `Path` |

The public prompt imports are:

```python
from pyclack.prompts import (
    ask,
    autocomplete,
    autocomplete_multiselect,
    confirm,
    multiline,
    multiselect,
    password,
    pick_date,
    select,
    select_key,
    select_path,
)
```

## Common prompt options

Several prompts support an `abort_time`.

```python
from pyclack.prompts import ask

name: str = ask(
    message="Name",
    abort_time=10.0
)
```

If the timeout expires, the prompt enters its cancellation path.

Validation functions use the convention:

```python
from pyclack.prompts import ask

def validate_name(value: str) -> str | None:
    if not value:
        return "Name cannot be empty"

name: str = ask(
    message="Name",
    validate=validate_name
)
```

Return `None` when the value is valid. Return a string containing the validation error when it is invalid.

---

# `ask()`

`ask()` collects a single line of text.

### Input

```python
from pyclack.prompts import ask

name: str = ask(
    message="What is your name?",
    placeholder="(e.g. Bobby)"
)
```

Parameters:

- `message: str` - prompt message
- `placeholder: str | None` - text displayed when the input is empty
- `initial_value: str | None` - initial text in the prompt
- `validate: Callable[[str], str | None] | None` - optional validator
- `abort_time: float | None` - optional timeout in seconds

### Output

```python
from pyclack.prompts import ask

name: str = ask("Name")
```

The returned value is the entered `str`.

### Cancellation

`e.value` is the current input buffer.

```python
from pyclack.prompts import CancelException, ask

try:
    name: str = ask("Name")
except CancelException as e:
    current_name: str | None = e.value
```

---

# `password()`

`password()` collects text without displaying the entered characters normally.

### Input

```python
from pyclack.prompts import password

secret: str = password(
    message="Password",
    show_nothing=False
)
```

Parameters:

- `message: str` - prompt message
- `mask: Symbol | None` - custom masking symbol
- `show_nothing: bool` - hide the entered characters completely
- `clear_on_error: bool` - clear the input after validation failure
- `validate: Callable[[str], str | None] | None` - optional validator
- `abort_time: float | None` - optional timeout in seconds

The default mask comes from the active theme.

### Output

```python
from pyclack.prompts import password

secret: str = password("Password")
```

The returned value is the actual entered `str`, not the masked representation.

### Cancellation

`e.value` is the current password input.

```python
from pyclack.prompts import CancelException, password

try:
    secret: str = password("Password")
except CancelException as e:
    current_secret: str | None = e.value
```

---

# `confirm()`

`confirm()` presents two choices and returns a boolean.

### Input

```python
from pyclack.prompts import confirm

confirmed: bool = confirm("Continue?")
```

Parameters:

- `message: str` - prompt message
- `active: str` - label for `True`
- `inactive: str` - label for `False`
- `vertical: bool` - render the choices vertically
- `default_option: bool` - initial selection
- `abort_time: float | None` - optional timeout in seconds

### Output

```python
from pyclack.prompts import confirm

confirmed: bool = confirm("Continue?")
```

The result is `True` or `False`.

### Cancellation

`e.value` is the currently selected boolean.

```python
from pyclack.prompts import CancelException, confirm

try:
    confirmed: bool = confirm("Continue?")
except CancelException as e:
    current_choice: bool | None = e.value
```

---

# `pick_date()`

`pick_date()` selects a date constrained by a minimum and maximum date.

### Input

```python
from datetime import date

from pyclack.prompts import pick_date

release_date: date = pick_date(
    message="Release date",
    initial_date=date.today(),
    min_date=date(2026, 1, 1),
    max_date=date(2030, 12, 31)
)
```

Parameters:

- `message: str` - prompt message
- `initial_date: date` - the initial date the prompt should start with
- `min_date: date` - the minimum date the prompt will accept
- `max_date: date` - the maximum date the prompt will accept
- `validate: Callable[[date], str | None] | None` - optional validator
- `abort_time: float | None` - optional timeout in seconds

The date is entered as `mm/dd/yyyy`.

### Output

```python
from datetime import date

from pyclack.prompts import pick_date

release_date: date = pick_date(
    "Release date",
    initial_date=date.today(),
    min_date=date(2026, 1, 1),
    max_date=date(2030, 12, 31)
)
```

The successful return value is a `datetime.date`.

### Cancellation

The current date fields are converted to a `YYYY-MM-DD` string and stored in `e.value`.

```python
from datetime import date

from pyclack.prompts import CancelException, pick_date

try:
    release_date: date = pick_date(
        "Release date",
        initial_date=date.today(),
        min_date=date(2026, 1, 1),
        max_date=date(2030, 12, 31)
    )
except CancelException as e:
    current_date: str | None = e.value
```

---

# `multiline()`

`multiline()` collects text containing multiple lines.

### Input

```python
from pyclack.prompts import multiline

description: str = multiline(
    message="Description",
    placeholder="Enter a description...",
    show_submit=True
)
```

Parameters:

- `message: str` - prompt message
- `placeholder: str | None` - text displayed when the input is empty
- `initial_value: str | None` - the initial text in the prompt
- `validate: Callable[[str], str | None] | None` - optional validator
- `show_submit: bool` - whether to show a submit button or not
- `abort_time: float | None` - optional timeout in seconds

When `show_submit=False`, pressing Enter twice submits.

When `show_submit=True`, Tab moves focus to the submit button and Enter submits while it is focused.

### Output

```python
from pyclack.prompts import multiline

description: str = multiline("Description")
```

The returned `str` contains the entered newline characters.

### Cancellation

`e.value` is the current multiline input.

```python
from pyclack.prompts import CancelException, multiline

try:
    description: str = multiline("Description")
except CancelException as e:
    current_description: str | None = e.value
```

---

# `ClackOption`

Selection prompts use `ClackOption`, a generic dataclass containing:

```python
from pyclack import ClackOption

option: ClackOption[str] = ClackOption[str](
    value="python",
    label="Python"
)
```

Its fields are:

```python
from pyclack import ClackOption

option: ClackOption[str] = ClackOption[str](
    value="python",
    label="Python",
    hint="Recommended",
    disabled=False
)
```

- `value: V` - the actual value associated with the option
- `label: str` - text displayed to the user
- `hint: str | None` - optional additional text
- `disabled: bool` - whether the option can be selected

## Generic typing convention

When the type of `value` is known, parameterize **both** the annotation and the constructor.

```python
from pyclack import ClackOption

integer_option: ClackOption[int] = ClackOption[int](
    value=3,
    label="Three"
)
```

For a string:

```python
from pyclack import ClackOption

string_option: ClackOption[str] = ClackOption[str](
    value="python",
    label="Python"
)
```

For a custom type:

```python
from dataclasses import dataclass

from pyclack import ClackOption

@dataclass
class Language:
    name: str
    version: str

language: Language = Language(
    name="Python",
    version="3.13"
)

option: ClackOption[Language] = ClackOption[Language](
    value=language,
    label="Python 3.13"
)
```

Do not drop the generic parameter when the type is already known.

Prefer:

```python
from pyclack import ClackOption

integer_option: ClackOption[int] = ClackOption[int](
    value=3,
    label="Three"
)
```

over:

```python
from pyclack.prompts import ClackOption

integer_option: ClackOption[int] = ClackOption(
    value=3,
    label="Three"
)
```

---

# `select()`

`select()` lets the user choose exactly one option.

### Input

```python
from pyclack import ClackOption
from pyclack.prompts import select

options: list[ClackOption[str]] = [
    ClackOption[str](
        value="python",
        label="Python"
    ),
    ClackOption[str](
        value="rust",
        label="Rust"
    ),
    ClackOption[str](
        value="go",
        label="Go"
    ),
]

selected: ClackOption[str] = select(
    message="Choose a language",
    options=options
)
```

Parameters:

- `message: str` - prompt message
- `options: list[ClackOption[T]]` - a list of options for the select prompt to iterate over
- `show_instructions: bool` - whether to show instructions on how to navigate the prompt
- `max_items: int` - the maximum number of lines that will be rendered with regards to the list of options (list is scrollable)
- `abort_time: float | None` - optional timeout in seconds

`max_items` controls the visible option window. The implementation keeps a minimum display size of five.

### Output

The return value is the selected `ClackOption`, not its `.value`.

```python
from pyclack import ClackOption
from pyclack.prompts import select

options: list[ClackOption[int]] = [
    ClackOption[int](value=1, label="One"),
    ClackOption[int](value=2, label="Two"),
    ClackOption[int](value=3, label="Three")
]

selected: ClackOption[int] = select(
    message="Choose a number",
    options=options,
)

number: int = selected.value
```

### Cancellation

`e.value` is the currently highlighted `ClackOption`.

```python
from pyclack import ClackOption, CancelException
from pyclack.prompts import select

options: list[ClackOption[str]] = [
    ClackOption[str](value="python", label="Python"),
    ClackOption[str](value="rust", label="Rust")
]

try:
    selected: ClackOption[str] = select(
        message="Language",
        options=options,
    )
except CancelException as e:
    selected_before_cancel: ClackOption[str] | None = e.value
```

An empty option list, or an option list where every option is disabled, raises `RuntimeError`.

---

# `multiselect()`

`multiselect()` lets the user select multiple options.

### Input

```python
from pyclack.prompts import multiselect
from pyclack import ClackOption

options: list[ClackOption[str]] = [
    ClackOption[str](value="git", label="Git"),
    ClackOption[str](value="docker", label="Docker"),
    ClackOption[str](value="pytest", label="Pytest")
]

selected: list[ClackOption[str]] = multiselect(
    message="Select tools",
    options=options
)
```

Parameters:

- `message: str` - prompt message
- `options: list[ClackOption[T]]` - a list of options for the select prompt to iterate over
- `show_instructions: bool` - whether to show instructions on how to navigate the prompt
- `max_items: int` - the maximum number of lines that will be rendered with regards to the list of options (list is scrollable)
- `abort_time: float | None` - optional timeout in seconds

Space selects or deselects the focused option.

### Output

```python
from pyclack.prompts import multiselect
from pyclack import ClackOption

options: list[ClackOption[str]] = [
    ClackOption[str](value="git", label="Git"),
    ClackOption[str](value="docker", label="Docker")
]

selected: list[ClackOption[str]] = multiselect(
    message="Select tools",
    options=options
)

tools: list[str] = [
    option.value
    for option in selected
]
```

### Cancellation

`e.value` is the list of options selected so far.

```python
from pyclack.prompts import multiselect
from pyclack import ClackOption, CancelException

options: list[ClackOption[str]] = [
    ClackOption[str](value="git", label="Git"),
    ClackOption[str](value="docker", label="Docker")
]

try:
    selected: list[ClackOption[str]] = multiselect(
        message="Select tools",
        optins=options
    )
except CancelException as e:
    selected_before_cancel: list[ClackOption[str]] | None = e.value
```

An empty option list, or an option list where every option is disabled, raises `RuntimeError`.

---

# `autocomplete()`

`autocomplete()` combines text filtering with single-option selection.

### Input

```python
from pyclack.prompts import autocomplete
from pyclack import ClackOption

options: list[ClackOption[str]] = [
    ClackOption[str](value="python", label="Python"),
    ClackOption[str](value="rust", label="Rust"),
    ClackOption[str](value="javascript", label="JavaScript")
]

selected: ClackOption[str] = autocomplete(
    message="Language",
    options=options,
    placeholder="Type to search..."
)
```

Parameters:

- `message: str` - prompt message
- `options: list[ClackOption[T]]` - a list of options for the select prompt to iterate over
- `placeholder: str` - text displayed when the input is empty
- `show_instructions: bool` - whether to show instructions on how to navigate the prompt
- `max_items: int` - the maximum number of lines that will be rendered with regards to the list of options (list is scrollable)
- `filter: Callable[[str, list[ClackOption[T]]], list[ClackOption[T]]] | None` - optional filter to use for search
- `abort_time: float | None` - optional timeout in seconds

The default filter is used when `filter=None`.

A custom filter receives the current search string and the full option list.

```python
from pyclack.prompts import autocomplete
from pyclack import ClackOption

def filter_options(
    search: str,
    options: list[ClackOption[str]],
) -> list[ClackOption[str]]:
    search_lower: str = search.lower()

    return [
        option
        for option in options
        if search_lower in option.label.lower()
    ]

options: list[ClackOption[str]] = [
    ClackOption[str](value="python", label="Python"),
    ClackOption[str](value="rust", label="Rust")
]

selected: ClackOption[str] = autocomplete(
    message="Language",
    options=options,
    filter=filter_options
)
```

### Output

The selected `ClackOption` is returned.

```python
from pyclack.prompts import autocomplete
from pyclack import ClackOption

options: list[ClackOption[int]] = [
    ClackOption[int](value=1, label="One"),
    ClackOption[int](value=2, label="Two")
]

selected: ClackOption[int] = autocomplete(
    message="Number",
    options=options
)

number: int = selected.value
```

### Cancellation

`e.value` is the currently highlighted enabled option, or `None` if there is no usable selected option.

```python
from pyclack.prompts import autocomplete
from pyclack import ClackOption, CancelException

options: list[ClackOption[str]] = [
    ClackOption[str](value="python", label="Python"),
    ClackOption[str](value="rust", label="Rust"),
]

try:
    selected: ClackOption[str] = autocomplete(
        message="Language",
        options=options
    )
except CancelException as e:
    selected_before_cancel: ClackOption[str] | None = e.value
```

An empty option list, or an option list where every option is disabled, raises `RuntimeError`.

---

# `autocomplete_multiselect()`

`autocomplete_multiselect()` combines autocomplete filtering with multiple selection.

### Input

```python
from pyclack.prompts import autocomplete_multiselect
from pyclack import ClackOption

options: list[ClackOption[str]] = [
    ClackOption[str](value="git", label="Git"),
    ClackOption[str](value="docker", label="Docker"),
    ClackOption[str](value="pytest", label="Pytest")
]

selected: list[ClackOption[str]] = autocomplete_multiselect(
    message="Select tools",
    options=options
)
```

Parameters:

- `message: str` - prompt message
- `options: list[ClackOption[T]]` - a list of options for the select prompt to iterate over
- `placeholder: str` - text displayed when the input is empty
- `show_instructions: bool` - whether to show instructions on how to navigate the prompt
- `max_items: int` - the maximum number of lines that will be rendered with regards to the list of options (list is scrollable)
- `filter: Callable[[str, list[ClackOption[T]]], list[ClackOption[T]]] | None` - optional filter to use for search
- `abort_time: float | None` - optional timeout in seconds

Space selects or deselects the highlighted option.

### Output

```python
from pyclack.prompts import autocomplete_multiselect
from pyclack import ClackOption

options: list[ClackOption[int]] = [
    ClackOption[int](value=1, label="One"),
    ClackOption[int](value=2, label="Two")
]

selected: list[ClackOption[int]] = autocomplete_multiselect(
    message="Select numbers",
    options=options
)

numbers: list[int] = [
    option.value
    for option in selected
]
```

### Cancellation

`e.value` is the current list of selected options. If nothing has been selected, it is an empty list.

```python
from pyclack.prompts import autocomplete_multiselect
from pyclack import ClackOption, CancelException

options: list[ClackOption[str]] = [
    ClackOption[str](value="git", label="Git"),
    ClackOption[str](value="docker", label="Docker"),
]

try:
    selected: list[ClackOption[str]] = autocomplete_multiselect(
        message="Select tools",
        options=options
    )
except CancelException as e:
    selected_before_cancel: list[ClackOption[str]] | None = e.value
```

An empty option list, or an option list where every option is disabled, raises `RuntimeError`.

---

# `select_key()`

`select_key()` selects an option by pressing its key.

The option value must be a valid string key.

### Input

```python
from pyclack.prompts import select_key
from pyclack import ClackOption

options: list[ClackOption[str]] = [
    ClackOption[str](value="y", label="Yes"),
    ClackOption[str](value="n", label="No"),
    ClackOption[str](value="s", label="Skip")
]

selected: ClackOption[str] = select_key(
    message="Choose an action",
    options=options,
    case_sensitive=True
)
```

Parameters:

- `message: str` - prompt message
- `options: list[ClackOption[str]]` - a list of options for the select prompt to iterate over
- `case_sensitive: bool` - whether to treat capital and lower case variations of the same letters as identical or not
- `abort_time: float | None` - optional timeout in seconds

Pressing Enter selects the first option.

### Output

```python
from pyclack.prompts import select_key
from pyclack import ClackOption

options: list[ClackOption[str]] = [
    ClackOption[str](value="y", label="Yes"),
    ClackOption[str](value="n", label="No")
]

selected: ClackOption[str] = select_key(
    message="Continue?",
    options=options
)

key: str = selected.value
```

### Cancellation

`e.value` is the first option in the option list.

```python
from pyclack.prompts import select_key
from pyclack import ClackOption, CancelException

options: list[ClackOption[str]] = [
    ClackOption[str](value="y", label="Yes"),
    ClackOption[str](value="n", label="No")
]

try:
    selected: ClackOption[str] = select_key(
        message="Continue?",
        options=options
    )
except CancelException as e:
    default_option: ClackOption[str] | None = e.value
```

The prompt raises `RuntimeError` for invalid or duplicate key values, empty options, or all-disabled options.

---

# `select_path()`

`select_path()` provides an autocomplete-style filesystem selector.

### Input

```python
from pathlib import Path

from pyclack.prompts import select_path

selected_path: Path = select_path(
    message="Select a path",
    root=Path.cwd(),
    directory=False
)
```

Parameters:

- `message: str` - prompt message
- `placeholder: str` - text displayed when the input is empty
- `show_instructions: bool` - whether to show instructions on how to navigate the prompt
- `max_items: int` - the maximum number of lines that will be rendered with regards to the list of options (list is scrollable)
- `root: Path` - the directory the prompt starts in and prioritizes
- `directory: bool` - whether to only show directories or not
- `abort_time: float | None` - optional timeout in seconds

When `directory=False`, both files and directories can be shown.

When `directory=True`, only directories are shown.

The default `root` is the current working directory.

### Output

```python
from pathlib import Path

from pyclack.prompts import select_path

selected_path: Path = select_path(message="Select a file")
```

The successful return value is a `Path`.

If the root path does not exist, `FileNotFoundError` is raised.

### Cancellation

`e.value` is the currently selected `Path`, or `None` if there is no selected path.

```python
from pathlib import Path

from pyclack.prompts import select_path
from pyclack import CancelException

try:
    selected_path: Path = select_path(message="Select a file")
except CancelException as e:
    selected_before_cancel: Path | None = e.value
```

---

# Cancellation

Cancellation is deliberately consistent across pyclack.

Pressing Escape or Ctrl+C cancels an active prompt. A prompt may also cancel itself when its `abort_time` expires.

The prompt raises `CancelException`:

```python
from pyclack.prompts import ask
from pyclack import CancelException

try:
    value: str = ask(message="Value")
except CancelException as e:
    current_value: str | None = e.value
```

`CancelException` itself is generic:

```python
from pyclack import CancelException

exception: CancelException[str] = CancelException(message="error ocurred", value="partial input")
```

Its `value` attribute is the state the prompt chooses to preserve:

```python
from pyclack import CancelException

exception: CancelException[str] = CancelException(message="error ocurred", value="partial input")

value: str | None = exception.value
```

## Cancellation values

| Prompt | Successful return | `e.value` |
| --- | --- | --- |
| `ask()` | `str` | current `str` or `None` |
| `password()` | `str` | current `str` or `None` |
| `confirm()` | `bool` | current `bool` or `None` |
| `pick_date()` | `date` | current date fields as `YYYY-MM-DD` text `str` or `None` |
| `multiline()` | `str` | current `str` or `None` |
| `select()` | `ClackOption[T]` | currently highlighted option `ClackOption[T]` or `None` |
| `multiselect()` | `list[ClackOption[T]]` | currently selected options `list[ClackOption[T]] or `None`` |
| `autocomplete()` | `ClackOption[T]` | currently highlihgted option `ClackOption[T]` or `None` |
| `autocomplete_multiselect()` | `list[ClackOption[T]]` | currently selected options `list[ClackOption[T]]` or `None` |
| `select_key()` | `ClackOption[str]` | first option `ClackOption[str]` or `None` |
| `select_path()` | `Path` | currently highlighted path `Path` or `None` |

The important convention is that cancellation is communicated by the exception, while `e.value` preserves useful component state.

---

# Widgets

Widgets render terminal UI instead of collecting a user-entered value.

The public synchronous widget API is:

```python
from pyclack.widgets import (
    Activity,
    Progress,
    ProgressStyle,
    Spinner,
    TaskLog,
    box,
    cancel,
    intro,
    log,
    note,
    outro,
    stream,
)
```

Simple rendering widgets don't return anything.

Stateful widgets such as `Spinner`, `Progress`, `Activity`, and `TaskLog` are objects whose methods control their lifecycle.

---

# `intro()`

`intro()` renders an introductory message.

### Input

```python
from pyclack.widgets import intro

intro(title="My Application")
```

It accepts:

- `title: str` - the widget title
- `custom_style: Style | None` - a text custom style to apply to the widget title

---

# `outro()`

`outro()` renders an ending message.

```python
from pyclack.widgets import outro

outro(message="Done!")
```

It accepts:

- `message: str` - the widget message
- `custom_style: Style | None` - a text custom style to apply to the widget message

---

# `cancel()`

`cancel()` renders a cancellation message.

```python
from pyclack.widgets import cancel

cancel(message="Operation cancelled.")
```

It accepts:

- `message: str` - the cancellation message displayed by the widget

---

# `note()`

`note()` renders a titled note.

```python
from pyclack.widgets import note

note(title="Configuration", message="Using configuration from pyproject.toml.")
```

Parameters:

- `title: str` - the widget title
- `message: str` - the message displayed inside the note box

---

# `box()`

`box()` renders text inside a bordered box.

```python
from pyclack import Alignment
from pyclack.widgets import box

box(
    content="Build complete.",
    title="Status",
    content_align=Alignment.CENTER,
    title_align=Alignment.LEFT,
    rounded=True
)
```

Parameters:

- `content: str` - the content text to display inside the box
- `title: str` - the title for the box widget
- `content_align: Alignment` - the alignment of the content inside the box
- `title_align: Alignment` - the alignment of the title on the box
- `width: int | None` - the maximum allowed width of the box in the terminal, if None then no max is applied
- `rounded: bool` - wether to use rounded corner for the box or not
- `title_padding: int` - the spacing on either side of the title on the box
- `content_padding: int` - the spacing on either side of the content in the box

---

# `log`

`log` is a semantic logging interface.

```python
from pyclack.widgets import log

log.message(msg="Starting build")
log.info(msg="Using Python 3.13")
log.warning(msg="Configuration file not found")
log.error(msg="Compilation failed")
log.success(msg="Build complete")
log.step(msg="Installing dependencies")
```

These functions accept:

- `msg: str` - the message to display

The semantic levels are:

- `message()`
- `info()`
- `warning()`
- `warn()`
- `error()`
- `success()`
- `step()`

`warn()` is the warning alias.

---

# `TaskLog`

`TaskLog` is for a task that accumulates messages while it is running.

### Input

```python
from pyclack.widgets import TaskLog

task: TaskLog = TaskLog(
    title="Building project",
    limit=5,
    retain_log=False,
)
```

Parameters:

- `title: str` - the title displayed by the widget
- `limit: int | None` - maximum number of messages retained/displayed
- `retain_log: bool` - retain the complete log instead of trimming the stored log to the limit

### Adding messages

```python
from pyclack.widgets import TaskLog

task: TaskLog = TaskLog(title="Building")

task.message(msg="Compiling main.py")
task.message(msg="Compiling utils.py")
task.success(msg="Build complete")
```

Once `success()` is called, the task is marked successful and subsequent `message()` calls are ignored.

### Reading the log

```python
from pyclack.widgets import TaskLog

task: TaskLog = TaskLog(title="Building")

task.message(msg="Compiling")
task.message(msg="Linking")

messages: list[str] = task.get_log()
```

The initial title is part of the stored log.

### Cancellation

Ctrl+C while a `TaskLog` is active raises `CancelException`.

The current implementation raises it without a value, so:

```python
from pyclack import CancelException
from pyclack.widgets import TaskLog, cancel

task: TaskLog = TaskLog(title="Building")

try:
    task.message(msg="Compiling")
    # ... do some work ...
    # task.message(msg="progress update")
    # ... more progress updates ...
except CancelException:
    cancel('Compiling cancelled!')
    exit(0)
```

---

# `Spinner`

`Spinner` renders an animated spinner while work is being performed.

### Input

```python
from pyclack.widgets import Spinner

spinner: Spinner = Spinner(
    show_timer=False,
    show_elipse=True,
    spinner_delay=80,
    elipse_delay=500,
)
```

Parameters:

- `show_timer: bool`- whether to display a timer for time elapsed since spinner has started on the widget
- `show_elipse: bool` - whether to display a loading elipse after the spinner message or not
- `spinner_delay: float` - milliseconds between spinner frames
- `elipse_delay: float` - milliseconds between ellipsis frames
- `spinner_frames: SpinnerSymbols | None` - a custom set of spinner frames to use for the spinner animation, uses themes default if None

### Lifecycle

```python
from pyclack.widgets import Spinner

spinner: Spinner = Spinner()

spinner.start(msg="Installing dependencies")
# ... do some work ...
spinner.stop(msg="Dependencies installed")
```

### Updating the message

```python
from pyclack.widgets import Spinner

spinner: Spinner = Spinner()

spinner.start(msg="Installing")
# ... do some work ...
spinner.set_message(msg="Installing package 2/5")
```

### Cancellation and errors

```python
from pyclack.widgets import Spinner

spinner: Spinner = Spinner()

spinner.start(msg="Installing")
# ... do some interrupted work ...
spinner.cancel(msg="Installation cancelled")
```

```python
from pyclack.widgets import Spinner

spinner: Spinner = Spinner()

spinner.start(msg="Installing")
# ... do some failed work ...
spinner.error(msg="Installation failed")
```

### Clearing

```python
from pyclack.widgets import Spinner

spinner: Spinner = Spinner()

spinner.start(msg="Installing")
# ... do some work ...
spinner.clear()
```

### Checking cancellation

```python
from pyclack.widgets import Spinner

spinner: Spinner = Spinner()

cancelled: bool = spinner.is_cancelled()
```

Ctrl+C raises a `CancelException` while the spinner is running. The spinner restores the terminal state during cleanup.

```python
from pyclack.widget import Spinner, cancel

spinner: Spinner = Spinner()

spinner.start(msg="Installing")
try:
    # ... do some work ...
except CancelException:
    spinner.cancel("Installation cancelled")
    cancel('Operation cancelled')
    exit(0)
spinner.stop(msg="Dependencies installed")
```

---

# `Progress`

`Progress` renders a progress bar with optional spinner, ellipsis, and timer behavior.

### Input

```python
from pyclack.widgets import Progress, ProgressStyle

progress: Progress = Progress(
    max=100,
    size=30,
    style=ProgressStyle.HEAVY,
    show_timer=False,
    show_elipse=True,
)
```

Parameters include:

- `max: int` - maximum progress value
- `size: int` - visual width of the progress bar
- `style: ProgressStyle` - either LIGHT, HEAVY, or BLOCK
- `show_timer: bool` - whether to display a timer for time elapsed since the progress bar has started on the widget
- `show_elipse: bool` - whether to display a loading elipse after the loading message or not
- `spinner_delay: float` - milliseconds between spinner frames
- `elipse_delay: float` - milliseconds between ellipsis frames
- `spinner_frames: SpinnerSymbols | None` - a custom set of spinner frames to use for the spinner animation, uses themes default if None

### Basic lifecycle

```python
from pyclack.widgets import Progress

progress: Progress = Progress(max=100, size=30)

progress.start(msg="Downloading")

progress.advance(amount=25)
progress.advance(amount=25)

progress.stop(msg="Download complete")
```

The progress bar also has:
```python
progress.error(msg="Download failed")
```
```python
progress.clear()
```
```python
cancelled: bool = progress.is_cancelled()
```

The progress widget is stateful: it maintains the current progress and redraws its frame as that state changes.

Ctrl+C raises a `CancelException` while the progress bar is running. The progress bar restores the terminal state during cleanup.

```python
from pyclack.widgets import Progress
from pyclack import CancelException, cancel

progress: Progress = Progress(max=100, size=30)

progress.start(msg="Downloading")
try:
    for i in range(100):
        progress.advance()
except CancelException:
    progress.cancel(msg="Download cancelled")
    cancel("Operation cancelled")
    exit(0)
progress.stop(msg="Download complete")
```

---

# `Activity`

`Activity` combines a spinner with a sequence of activity messages.

### Input

```python
from pyclack.widgets import Activity

activity: Activity = Activity(
    limit=5,
    show_timer=False,
    show_elipse=True,
)
```

Parameters:

- `limit: int | None` - maximum number of messages retained/displayed
- `show_timer: bool` - whether to display a timer for time elapsed since the activity has started on the widget
- `show_elipse: bool` - whether to display a loading elipse after the spinner message or not
- `spinner_delay: float` - milliseconds between spinner frames
- `elipse_delay: float` - milliseconds between ellipsis frames
- `spinner_frames: SpinnerSymbols | None` - a custom set of spinner frames to use for the spinner animation, uses themes default if None

### Lifecycle

```python
from pyclack.widgets import Activity

activity: Activity = Activity()

start_result: None = activity.start(
    "Building",
)

message_result: None = activity.set_activity_message(
    "Compiling main.py",
)

message_result = activity.set_activity_message(
    "Compiling utils.py",
)

stop_result: None = activity.stop(
    "Build complete",
)
```

The activity and spinner messages are separate pieces of state.

```python
from pyclack.widgets import Activity

activity: Activity = Activity()

start_result: None = activity.start("Building")

spinner_result: None = activity.set_spinner_message(
    "Still building",
)

activity_result: None = activity.set_activity_message(
    "Compiling main.py",
)

current_activity: str = activity.get_activity_message()
```

It also supports:

```python
from pyclack.widgets import Activity

activity: Activity = Activity()

cancel_result: None = activity.cancel(
    "Build cancelled",
)

error_result: None = activity.error(
    "Build failed",
)

clear_result: None = activity.clear()

cancelled: bool = activity.is_cancelled()
```

---

# `stream`

The stream widget is designed for output where the number of messages is not known ahead of time.

Unlike the other widgets, `stream` directly accepts either a normal `Iterable[str]` or an `AsyncIterable[str]`.

```python
from collections.abc import Iterable

from pyclack.widgets import stream

messages: Iterable[str] = [
    "Downloading...",
    "Extracting...",
    "Installing...",
    "Complete",
]

result: None = stream.message(messages)
```

The three stream styles are:

- `stream.message()`
- `stream.info()`
- `stream.step()`

### Normal iterable

```python
from collections.abc import Iterator

from pyclack.widgets import stream

def messages() -> Iterator[str]:
    yield "Downloading..."
    yield "Extracting..."
    yield "Installing..."
    yield "Complete"

result: None = stream.message(messages())
```

### Info stream

```python
from collections.abc import Iterator

from pyclack.widgets import stream

def messages() -> Iterator[str]:
    yield "Connected"
    yield "Downloading"
    yield "Complete"

result: None = stream.info(messages())
```

### Step stream

```python
from collections.abc import Iterator

from pyclack.widgets import stream

def steps() -> Iterator[str]:
    yield "Installing dependencies"
    yield "Building project"
    yield "Running tests"

result: None = stream.step(steps())
```

### Async iterable

```python
from collections.abc import AsyncIterator

from pyclack.widgets import stream

async def messages() -> AsyncIterator[str]:
    yield "Connecting..."
    yield "Downloading..."
    yield "Complete"

result: None = stream.message(messages())
```

`stream.message()`, `stream.info()`, and `stream.step()` all accept:

```python
from collections.abc import AsyncIterable, Iterable

values: Iterable[str] | AsyncIterable[str]
```

The stream functions block until the supplied iterable is exhausted.

---

# Asynchronous APIs

pyclack provides asynchronous wrappers for the interactive prompts under `pyclack.prompts_asyc`.

```python
from pyclack.prompts_asyc import ask

async def get_name() -> str:
    name: str = await ask(
        "Name",
        None,
        None,
        None,
        None,
    )

    return name
```

The wrappers preserve the same behavior and return types as their synchronous counterparts.

The wrappers run the synchronous prompt implementation in a worker thread using `asyncio.to_thread()`, so the prompt can be awaited without blocking the asyncio event loop.

All prompt wrappers are available:

```python
from pyclack.prompts_asyc import (
    ask,
    autocomplete,
    autocomplete_multiselect,
    confirm,
    multiline,
    multiselect,
    password,
    pick_date,
    select,
    select_key,
    select_path,
)
```

The widget wrappers live under `pyclack.widgets_asyc`:

```python
from pyclack.widgets_asyc import (
    Activity,
    Progress,
    Spinner,
    TaskLog,
    box,
    cancel,
    intro,
    note,
    outro,
)
```

The asynchronous widget wrappers likewise delegate their synchronous operations through `asyncio.to_thread()`.

For example:

```python
from pyclack.widgets_asyc import Spinner

async def build() -> None:
    spinner: Spinner = Spinner()

    await spinner.start("Building")

    await do_async_build()

    await spinner.stop("Build complete")
```

The stream API is already asynchronous-iterable aware, so it does not require a separate `stream_asyc` namespace.

---

# Themes

Themes control the visual language used by prompts and widgets.

A theme contains:

- `active` style
- `submit` style
- `cancel` style
- `error` style
- `info` style
- `muted` style
- `text` style
- `cursor` style
- `symbols`

Themes are defined by `Theme` and collected by `Themes`.

The active theme can be changed with `set_active_theme()`:

```python
from pyclack.config import set_active_theme
from pyclack.renderer import Themes

set_active_theme(
    Themes.DEFAULT,
)
```

The current active theme can be retrieved with:

```python
from pyclack.config import get_active_theme

theme = get_active_theme()
```

The theme system is intentionally separate from the prompt and widget implementations. Prompts ask the active theme for their colors and symbols when they render.

This means changing the active theme changes the appearance of existing components without rewriting their rendering logic.

## Custom themes

A theme is composed from `Style`, `Theme`, `Symbols`, `Symbol`, and `SpinnerSymbols`.

```python
from pyclack.config import set_active_theme
from pyclack.renderer import SpinnerSymbols, Style, Symbol, Symbols, Theme

custom_theme: Theme = Theme(
    active=Style(fg_color="cyan"),
    submit=Style(fg_color="green"),
    cancel=Style(fg_color="red"),
    error=Style(fg_color="yellow"),
    info=Style(fg_color="blue"),
    muted=Style(fg_color="bright_black"),
    text=Style(fg_color="white"),
    cursor=Style(
        fg_color="bright_black",
        bg_color="white",
    ),
    symbols=Symbols(
        step_marker_active=Symbol("◆", "*"),
        step_marker_cancel=Symbol("■", "x"),
        step_marker_error=Symbol("▲", "x"),
        step_marker_submit=Symbol("◇", "o"),
        connector_bar_start=Symbol("┌", "T"),
        connector_bar_vertical=Symbol("│", "|"),
        connector_bar_end=Symbol("└", "-"),
        selection_widget_radio_active=Symbol("●", ">"),
        selection_widget_radio_inactive=Symbol("○", " "),
        selection_widget_checkbox_active=Symbol("◻", "[•]"),
        selection_widget_checkbox_selected=Symbol("◼", "[+]"),
        selection_widget_checkbox_inactive=Symbol("◻", "[ ]"),
        selection_widget_password_mask=Symbol("▪", "*"),
        box_drawing_horizontal_bar=Symbol("─", "-"),
        box_drawing_vertical_bar=Symbol("│", "|"),
        box_drawing_top_right_corner_rounded=Symbol("╮", "+"),
        box_drawing_left_connector=Symbol("├", "+"),
        box_drawing_bottom_right_corner_rounded=Symbol("╯", "+"),
        box_drawing_top_left_corner_rounded=Symbol("╭", "+"),
        box_drawing_bottom_left_corner_rounded=Symbol("╰", "+"),
        box_drawing_top_right_corner=Symbol("┐", "+"),
        box_drawing_bottom_right_corner=Symbol("┘", "+"),
        box_drawing_top_left_corner=Symbol("┌", "+"),
        box_drawing_bottom_left_corner=Symbol("└", "+"),
        log_level_info=Symbol("●", "i"),
        log_level_success=Symbol("◆", "*"),
        log_level_warn=Symbol("▲", "!"),
        log_level_error=Symbol("■", "x"),
        spinner=SpinnerSymbols(
            unicode_symbols=("◒", "◐", "◓", "◑"),
            ascii_symbols=("|", "/", "-", "\\"),
        ),
        progress_light=Symbol("─", "-"),
        progress_heavy=Symbol("━", "="),
        progress_block=Symbol("█", "#"),
    ),
)

set_active_theme(custom_theme)
```

The repository already contains several additional theme definitions covering different visual styles and color palettes. The theme architecture is designed so additional themes can be added without modifying individual prompts or widgets.

## Unicode and ASCII symbols

Every `Symbol` can contain both a Unicode representation and an ASCII fallback.

```python
from pyclack.renderer import Symbol

marker: Symbol = Symbol(
    "◆",
    "*",
)
```

The renderer automatically resolves the appropriate representation for the current terminal.

ASCII-only output can also be forced:

```python
from pyclack.config import set_print_mode_ascii

result: None = set_print_mode_ascii()
```

---

# Rendering

The rendering system is exposed under `pyclack.renderer`.

```python
from pyclack.renderer import (
    FrameBuilder,
    RenderFrame,
    SpinnerSymbols,
    Style,
    Symbol,
    Symbols,
    Text,
    Theme,
    Themes,
)
```

The basic rendering model is:

1. Build `Text` objects.
2. Add them to a `FrameBuilder`.
3. Build the frame.
4. Draw it with `RenderFrame`.

## `Text`

`Text` represents terminal text together with optional style information.

```python
from pyclack.renderer import Style, Text

style: Style = Style(
    fg_color="cyan",
    bold=True,
)

text: Text = Text(
    "Hello",
    style,
)
```

`Text` objects can be combined to construct more complex output.

## `FrameBuilder`

`FrameBuilder` collects the lines that make up one render frame.

```python
from pyclack.renderer import FrameBuilder, Text

builder: FrameBuilder = FrameBuilder()

line_one: None = builder.add_line(
    Text("First line"),
)

line_two: None = builder.add_line(
    Text("Second line"),
)

frame: tuple[Text, ...] = builder.build()
```

`add_lines()` can also be used for multiple lines.

```python
from pyclack.renderer import FrameBuilder, Text

builder: FrameBuilder = FrameBuilder()

result: None = builder.add_lines(
    Text("First"),
    Text("Second"),
    Text("Third"),
)

frame: tuple[Text, ...] = builder.build()
```

## `RenderFrame`

`RenderFrame` owns the currently rendered frame.

When a new frame is drawn, the previous frame is cleared before the new frame is printed.

```python
from pyclack.renderer import RenderFrame, Text

render_frame: RenderFrame = RenderFrame()

result: None = render_frame.draw_frame(
    Text("Loading..."),
)
```

A frame can later be cleared:

```python
from pyclack.renderer import RenderFrame, Text

render_frame: RenderFrame = RenderFrame()

draw_result: None = render_frame.draw_frame(
    Text("Loading..."),
)

clear_result: None = render_frame.clear_frame()
```

This frame-based model is what allows spinners, prompts, progress bars, and other components to redraw themselves without continuously appending new terminal lines.

---

# Terminal

The terminal subsystem lives under `pyclack.terminal`.

```python
from pyclack.terminal import (
    CursorController,
    EchoController,
    KeyReader,
    Stdout,
)
```

It provides the low-level terminal operations used by prompts and widgets.

## `KeyReader`

`KeyReader` reads individual keyboard input rather than waiting for a complete line.

Custom interactive components should normally use the existing terminal input abstraction rather than directly reading from `stdin`.

## `CursorController`

`CursorController` provides cursor-control escape sequences such as hiding and showing the cursor and moving/clearing rendered lines.

For example:

```python
from pyclack.terminal import CursorController

hide_sequence: str = CursorController.hide_cursor()
show_sequence: str = CursorController.show_cursor()
```

## `Stdout`

`Stdout` is the output abstraction used by pyclack's terminal components.

Custom widgets should use it instead of mixing arbitrary `print()` calls into frame rendering.

## `EchoController`

`EchoController` controls terminal echo behavior used by interactive components.

This is particularly important for prompts that need to control how Ctrl+C or keyboard input appears in the terminal.

When writing a custom interactive component, use the existing terminal controllers instead of implementing platform-specific terminal manipulation yourself.

---

# Building a custom prompt

If the built-in prompts do not fit your use case, pyclack exposes `PromptBase` specifically so a custom prompt can follow the same state-machine and rendering conventions.

A prompt is built around five states:

```python
from pyclack.prompts import PromptState

initial: PromptState = PromptState.INITIAL
active: PromptState = PromptState.ACTIVE
submit: PromptState = PromptState.SUBMIT
cancel: PromptState = PromptState.CANCEL
error: PromptState = PromptState.ERROR
```

The normal flow is:

```text
INITIAL
   |
   v
ACTIVE <----+
   |        |
   v        |
SUBMIT      |
   |        |
   +-- error
   |
   v
EXIT

ACTIVE/ERROR
   |
   +----> CANCEL
```

`PromptBase` provides the state machine. Your subclass supplies the behavior.

## Custom prompt structure

A custom prompt should:

1. Subclass `PromptBase`.
2. Store its input state on the prompt instance.
3. Create a `RenderFrame`.
4. Implement `handle_active()`.
5. Implement `handle_submit()`.
6. Implement `handle_error()` if validation is needed.
7. Implement `handle_cancel()`.
8. Raise `CancelException` from `handle_cancel()`.
9. Render through `FrameBuilder`, `Text`, the active `Theme`, and `RenderFrame`.
10. Expose a small public function that creates the prompt and returns its final value.

A minimal structure looks like this:

```python
from typing import override

from pyclack.prompts import CancelException, PromptBase
from pyclack.renderer import FrameBuilder, RenderFrame, Text


class CustomPrompt(PromptBase):
    def __init__(self, message: str) -> None:
        super().__init__()

        self.message: str = message
        self.value: str = ""
        self.render_frame: RenderFrame = RenderFrame()

        self.activate()

    @override
    def handle_active(
        self,
        key: str | None,
    ) -> bool:
        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(
            Text(self.message),
        )

        frame_builder.add_line(
            Text(self.value),
        )

        frame: tuple[Text, ...] = frame_builder.build()

        self.render_frame.draw_frame(
            *frame,
        )

        if key == "ENTER":
            return True

        if key:
            self.value += key

        return False

    @override
    def handle_submit(self) -> bool:
        return True

    @override
    def handle_cancel(self) -> None:
        raise CancelException[str](
            self.value,
        )
```

Then expose it through a small function:

```python
from pyclack.prompts import CancelException


def custom_prompt(message: str) -> str:
    prompt: CustomPrompt = CustomPrompt(message)

    return prompt.value
```

The exact rendering will normally be more involved, but the important convention is that the prompt owns its state and the base class owns the input/state-machine lifecycle.

## Validation

If the prompt can enter an invalid state, `handle_submit()` should return `False`.

That sends the prompt into `handle_error()`.

```python
from typing import override

from pyclack.prompts import PromptBase


class ValidatedPrompt(PromptBase):
    @override
    def handle_submit(self) -> bool:
        if self._is_valid():
            return True

        return False
```

`handle_error()` should render the error state and return:

- `False` to remain in the error state
- `True` to return to the active state

The base class handles the state transitions.

## Propagating the key after an error

Prompts that want the key that exits the error state to become the next active-state key can set:

```python
from pyclack.prompts import PromptBase


class CustomPrompt(PromptBase):
    def __init__(self) -> None:
        super().__init__()

        self.propogate_key_after_error: bool = True
```

This is the convention used by prompts such as `ask()` and `password()`.

---

# Building a custom widget

Widgets do not use the prompt state machine.

A custom widget should instead own its rendering state and use `RenderFrame` to redraw it.

A minimal stateful widget looks like:

```python
from pyclack.renderer import FrameBuilder, RenderFrame, Text


class CustomWidget:
    def __init__(self) -> None:
        self.render_frame: RenderFrame = RenderFrame()
        self.message: str = ""

    def start(self, message: str) -> None:
        self.message = message
        self._render()

    def set_message(self, message: str) -> None:
        self.message = message
        self._render()

    def clear(self) -> None:
        self.render_frame.clear_frame()

    def _render(self) -> None:
        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(
            Text(self.message),
        )

        frame: tuple[Text, ...] = frame_builder.build()

        self.render_frame.draw_frame(
            *frame,
        )
```

For a real pyclack widget, use the active theme instead of hard-coding visual styles:

```python
from pyclack.config import get_active_theme
from pyclack.renderer import FrameBuilder, RenderFrame, Text


class ThemedWidget:
    def __init__(self) -> None:
        self.render_frame: RenderFrame = RenderFrame()

    def render(self, message: str) -> None:
        theme = get_active_theme()

        frame_builder: FrameBuilder = FrameBuilder()

        frame_builder.add_line(
            Text(
                message,
                theme.text,
            ),
        )

        frame: tuple[Text, ...] = frame_builder.build()

        self.render_frame.draw_frame(
            *frame,
        )
```

This keeps the widget compatible with every active theme.

---

# Custom component conventions

When extending pyclack, follow the same architecture used by the built-in components.

### Prompts

- Use `PromptBase`.
- Keep interactive state on the prompt object.
- Use `PromptState` through the base state machine rather than implementing another input loop.
- Render every state through `RenderFrame`.
- Build output with `Text` and `FrameBuilder`.
- Pull colors and symbols from `get_active_theme()`.
- Handle cancellation through `CancelException`.
- Put the useful partial state in `CancelException.value`.
- Use `abort_time` when the prompt supports automatic cancellation.
- Expose a simple public function that returns the prompt's final value.

### Widgets

- Do not use `PromptBase`.
- Own the widget's state directly.
- Use `RenderFrame` for redrawable output.
- Use `FrameBuilder` and `Text` to construct frames.
- Pull visual properties from the active theme.
- Use `Stdout` and the terminal controllers for terminal manipulation.
- Clean up cursor/echo state when the widget finishes or is cancelled.

### Themes

- Never hard-code a component's visual language when the value belongs in the theme.
- Use `Theme` for styles.
- Use `Symbol` for individual symbols.
- Use `SpinnerSymbols` for animated spinner frames.
- Provide both Unicode and ASCII representations where appropriate.

This separation is what lets pyclack change its appearance without every prompt and widget needing its own styling configuration.

---

# Package layout

The important public portions of the package are organized as follows:

```text
pyclack/
├── config/
│   └── theme configuration
├── prompts/
│   ├── ask.py
│   ├── autocomplete.py
│   ├── autocomplete_multiselect.py
│   ├── confirm.py
│   ├── multiline.py
│   ├── multiselect.py
│   ├── password.py
│   ├── pick_date.py
│   ├── select.py
│   ├── select_key.py
│   ├── select_path.py
│   └── prompt_base.py
├── prompts_asyc/
│   └── asynchronous prompt wrappers
├── renderer/
│   ├── Text
│   ├── RenderFrame
│   ├── FrameBuilder
│   ├── Theme
│   ├── Style
│   ├── Symbol
│   └── Symbols
├── terminal/
│   ├── KeyReader
│   ├── CursorController
│   ├── Stdout
│   └── EchoController
├── widgets/
│   ├── Activity
│   ├── box
│   ├── cancel
│   ├── intro
│   ├── log
│   ├── note
│   ├── outro
│   ├── Progress
│   ├── Spinner
│   ├── TaskLog
│   └── stream
└── widgets_asyc/
    └── asynchronous widget wrappers
```

The package also includes `py.typed`, so type checkers can use pyclack's bundled type information.

---

# Example

A small application can combine prompts and widgets:

```python
from pyclack.prompts import (
    CancelException,
    ClackOption,
    ask,
    select,
)
from pyclack.widgets import intro, outro


def main() -> None:
    intro("Example")

    try:
        name: str = ask(
            "What is your name?",
        )

        languages: list[ClackOption[str]] = [
            ClackOption[str](
                "python",
                "Python",
            ),
            ClackOption[str](
                "rust",
                "Rust",
            ),
        ]

        language: ClackOption[str] = select(
            "Favorite language",
            languages,
        )

        outro(
            f"Hello {name}! You chose {language.value}.",
        )

    except CancelException:
        outro(
            "Operation cancelled.",
        )


if __name__ == "__main__":
    main()
```

The important pattern is simple:

```text
prompt -> value
widget -> terminal output
cancel -> CancelException
partial state -> e.value
selection -> ClackOption[T]
theme -> active Theme
custom prompt -> PromptBase
custom widget -> RenderFrame
```

That is the core of pyclack.
