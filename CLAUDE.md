# CLAUDE.MD - Python Project Standards

## Code Structure Guidelines

### Standard Project Organization

```
project_root/
├── core/                       # Core shared functionality
│   ├── constants.py           # Application-wide constants and configurations
│   ├── logger_config.py       # Centralized logging setup
│   ├── models.py              # Data models and dataclasses
│   ├── tools.py               # Shared utility functions
│   └── config_manager.py      # Configuration management (optional)
├── operators/                  # Operations, operators, or commands (optional)
├── ui/                         # UI panels, menus, or interface elements (optional)
├── utils/                      # Additional utilities (optional)
└── vendor/                     # Third-party dependencies (optional)
```

### Module Organization Rules
- **core/**: Contains shared functionality used across the entire project
  - `constants.py`: All application constants, enums, and static configurations
  - `logger_config.py`: Logger setup and configuration
  - `models.py`: Data models using dataclasses
  - `tools.py`: Utility functions that don't fit elsewhere

- **Feature Modules**: Organize by functionality type
  - `operators/`: Operations that perform actions (business logic)
  - `ui/`: User interface elements (UI code)
  - `utils/`: Additional helper functions and utilities

- **Separation of Concerns**:
  - Keep business logic separate from UI code
  - UI code should be thin wrappers that call logic functions
  - Shared utilities and helpers go in `core/tools.py` or `utils/`

## Python Code Documentation Standards

### File Header Format
Every Python file must start with this header:

```python
"""
Feature/Subsystem Name
    Description:
        Clear description of what this module does and its main purpose.
        Can span multiple lines if needed.
"""
```

### Documentation Style
- Use **single-line docstrings** for all functions, classes, and methods
- Format: `"""Brief description of what this does."""`
- Place docstring on the line immediately after the function/class definition
- NO multi-line docstrings with `"""` on separate lines

### What NOT to Use
- ❌ NO `#` comments anywhere in code
- ❌ NO `# TODO` comments
- ❌ NO inline comments
- ❌ NO multi-line docstrings with separate lines for `"""`
- ❌ NO f-strings in logging statements
- ❌ NO `.format()` in logging statements

### What to Use Instead
- ✅ Single-line docstrings for documentation
- ✅ Descriptive variable and function names
- ✅ Extract complex logic into well-named functions
- ✅ C-style formatting in logging: `%s`, `%d`, `%f`, `%r`

## Path Handling Standards

### ALWAYS Use pathlib.Path
```python
from pathlib import Path

def process_file(filename):
    """Processes the specified configuration file."""
    config_dir = Path("configs")
    file_path = config_dir / filename

    if not file_path.exists():
        return None

    content = file_path.read_text()
    return content
```

### Path Operations
- ✅ Use `Path()` for all path operations
- ✅ Use `/` operator to join paths: `Path("dir") / "file.txt"`
- ✅ Use Path methods: `.exists()`, `.is_file()`, `.is_dir()`, `.mkdir()`, `.read_text()`, `.write_text()`
- ✅ Convert to string only when necessary: `str(path)` or `path.as_posix()`

- ❌ NEVER use string operations for paths
- ❌ NEVER use `os.path` module
- ❌ NEVER concatenate strings to build paths

## Logging Standards

### Logging Setup
Create `core/logger_config.py` for centralized logging:

```python
"""
Logger Configuration
    Description:
        Configures application-wide logging with consistent formatting
        and output destinations.
"""

import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.DEBUG, log_file=None):
    """Configures the root logger with console and optional file output."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )

    logging.debug("Logging initialized with level %s", logging.getLevelName(log_level))
```

### Logging Usage Rules

#### 1. One Debug Log Per Method
Place ONE `logger.debug()` at the end of each method summarizing what happened:

```python
def calculate_total(items, tax_rate):
    """Calculates total price including tax."""
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax
    logger.debug("Calculated total %f from %d items with tax rate %f", total, len(items), tax_rate)
    return total
```

#### 2. Log Levels and When to Use Them

- **DEBUG**: End of every method execution (use liberally)
  - What the method accomplished
  - Key parameters and results
  - Method flow completion

- **INFO**: Significant system events only (use sparingly)
  - Application startup/shutdown
  - Major state transitions
  - Configuration loaded
  - Database connected

- **WARNING**: Unexpected but handled situations
  - Missing optional configuration
  - Deprecated feature usage
  - Performance degradation
  - Fallback to defaults

- **ERROR**: Actual errors and exceptions
  - Failed operations
  - Exception details
  - Critical failures

#### 3. C-Style Formatting
ALWAYS use C-style string formatting in logging:

```python
logger.debug("Processed %d items in %f seconds", item_count, elapsed_time)
logger.info("Application started with config %s", config_path)
logger.warning("Cache miss for key %s, using default %r", key, default_value)
logger.error("Failed to connect to %s:%d - %s", host, port, error_message)
```

Format placeholders:
- `%s` - String (also works for Path objects)
- `%d` - Integer
- `%f` - Float
- `%r` - Repr (shows quotes and type info, useful for debugging)

#### 4. What to Log

```python
def save_project(project_id, data, output_dir):
    """Saves project data to the specified directory."""
    output_path = Path(output_dir) / f"{project_id}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        content = json.dumps(data, indent=2)
        output_path.write_text(content)
        logger.debug("Saved project %s to %s with %d fields", project_id, output_path, len(data))
        return True
    except Exception as e:
        logger.error("Failed to save project %s to %s: %s", project_id, output_path, str(e))
        return False
```

## Complete Example

```python
"""
Order Processing Module
    Description:
        Handles order processing including validation, calculation,
        and persistence of customer orders.
"""

import logging
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Order:
    """Represents a customer order with items and pricing."""
    order_id: str
    items: list
    tax_rate: float
    discount: float = 0.0

class OrderProcessor:
    """Processes customer orders and manages order persistence."""

    def __init__(self, data_dir, tax_rate):
        """Initializes processor with data directory and tax rate."""
        self.data_dir = Path(data_dir)
        self.tax_rate = tax_rate
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("OrderProcessor initialized with data_dir %s and tax_rate %f", self.data_dir, tax_rate)

    def calculate_total(self, order):
        """Calculates order total with tax and discount applied."""
        subtotal = sum(item.price * item.quantity for item in order.items)
        tax = subtotal * order.tax_rate
        discount_amount = subtotal * order.discount
        total = subtotal + tax - discount_amount
        logger.debug("Calculated total %f for order %s with %d items", total, order.order_id, len(order.items))
        return total

    def save_order(self, order, total):
        """Persists order data to filesystem."""
        order_file = self.data_dir / f"order_{order.order_id}.txt"

        try:
            content = f"{order.order_id},{total},{len(order.items)}"
            order_file.write_text(content)
            logger.debug("Saved order %s to %s with total %f", order.order_id, order_file, total)
            return True
        except Exception as e:
            logger.error("Failed to save order %s: %s", order.order_id, str(e))
            return False

    def process_order(self, order):
        """Processes complete order workflow from calculation to storage."""
        if not order.items:
            logger.warning("Attempted to process empty order %s", order.order_id)
            return None

        total = self.calculate_total(order)

        if self.save_order(order, total):
            logger.debug("Successfully processed order %s with total %f", order.order_id, total)
            return total

        logger.error("Order processing failed for order %s", order.order_id)
        return None
```

## Error Handling Standards

### Raise Exceptions Instead of Returning None
Functions that look up or find something should raise `ValueError` on failure instead of returning `None`:

```python
def find_socket_by_name(node, socket_name):
    """Finds a socket by name in the given node."""
    for socket in node.inputs:
        if socket.name == socket_name:
            logger.debug("Found socket %s in node %s", socket_name, node.name)
            return socket
    raise ValueError("Node %s has no socket named %s" % (node.name, socket_name))
```

### When to Raise vs Return None
- ✅ **Raise `ValueError`**: When the function's purpose is to find/get something specific
  - `get_camera_background_image()` - raises if no valid background image
  - `find_target_input()` - raises if socket not found
  - `get_view_layer_position()` - raises if view layer not in scene

- ✅ **Return None or empty**: When absence is a valid, expected state
  - `get_optional_config()` - config may not exist
  - Empty list when filtering finds no matches

### Exception Handling Pattern
Catch exceptions at the appropriate level - where you can handle them meaningfully:

```python
def process_all_passes(render_node, output_node):
    """Connects all passes from render node to output node."""
    for output in render_node.outputs:
        try:
            target = find_target_input(output_node, output.name)
        except ValueError as e:
            logger.warning("Skipping pass %s: %s", output.name, e)
            continue

        connect_nodes(output, target)

    logger.debug("Processed passes from %s to %s", render_node.name, output_node.name)
```

### Exception Types
Use Python's built-in exceptions:
- `ValueError` - Invalid value or state (most common)
- `TypeError` - Wrong type passed
- `RuntimeError` - Operation failed at runtime
- `FileNotFoundError` - File/path doesn't exist

### Blender Operator Pattern
In Blender operators, catch exceptions and report to user:

```python
def execute(self, context):
    """Executes the operator."""
    try:
        result = some_function_that_may_raise(context.scene)
    except ValueError as e:
        self.report({"WARNING"}, str(e))
        return {"CANCELLED"}

    logger.debug("Operation completed with result %s", result)
    return {"FINISHED"}
```

### UI Code Pattern
In UI drawing code, use fallback values silently:

```python
def draw_item(self, context, layout, item):
    """Draws a list item."""
    try:
        position = get_item_position(context.scene, item)
    except ValueError:
        position = 0

    layout.label(text="Position: %d" % position)
```

## Key Principles

1. **Code Structure**: Keep `core/` for shared functionality, separate `operators/` and `ui/`
2. **Documentation**: Single-line docstrings, no hash comments
3. **Paths**: Always use `pathlib.Path`, never string operations
4. **Logging**: One debug log per method, C-style formatting, appropriate log levels
5. **Clarity**: Self-documenting code through naming, not comments
6. **Error Handling**: Raise `ValueError` instead of returning `None` for lookup/find functions

## Naming Conventions

### Function Naming
- **Public functions**: Use descriptive names without prefix (e.g., `get_sorted_view_layers`)
- **Private/local functions**: Prefix with underscore (e.g., `_get_max_sort_order`, `_export_camera_to_alembic`)
- **Property getters/setters**: Prefix with underscore (e.g., `_get_active_view_layer_index`)

### Module-Level Variables
- **Private constants**: Use uppercase with underscore prefix (e.g., `_VIEW_LAYER_CLIPBOARD`)
- **Private class lists**: Use uppercase with underscore prefix (e.g., `_CLASSES`, `_MODULES`)

### File Naming in Blender Addons
- **Operators**: Use descriptive names with `_ops` suffix or action name (e.g., `vl_list_ops.py`, `export_camera.py`, `render_nodes.py`)
- **UI Panels**: Use descriptive names with `_panel` or `_ui` suffix (e.g., `render_panel.py`, `export_panel.py`, `vl_list_ui.py`)

## Type Hints

### Required Pattern
Always use type hints with `TYPE_CHECKING` pattern for bpy types:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context, Scene, ViewLayer
```

### Multi-line Function Signatures
For functions with multiple parameters, place closing parenthesis and return type on the same line as the last parameter:

```python
def create_render_layers_node(
    tree: NodeTree,
    view_layer: ViewLayer,
    location: tuple[float, float]) -> CompositorNodeRLayers:
    """Creates a Render Layers node for the specified view layer."""
```

NOT:
```python
def create_render_layers_node(
    tree: NodeTree,
    view_layer: ViewLayer,
    location: tuple[float, float]
) -> CompositorNodeRLayers:
```

## Project-Specific Notes

### qq_pipeline Specifics
- **Version**: 2.0.3
- **Tech Stack**: PySide6 (Qt), Python 3.x
- **DCC Integration**: Nuke and Blender
- **Key Models**: Project, Shot, ProjectPath (in `core/models.py`)
- **Modes**: Controlled via `QQ_PIPELINE_MODE` environment variable (nuke/blender)
- **Platform**: Primary target is Windows

### Module Overview
- **qq_manager**: Project management GUI (creates, opens, saves projects)
- **qq_nuke**: Nuke integration (scripts, precomps, renders, ACES, paths)
- **qq_blender**: Blender integration (project management, templates)
- **vendor**: Third-party libraries (fileseq, parse_exr_header)
