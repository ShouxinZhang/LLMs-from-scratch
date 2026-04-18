from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))


def discover_module_scripts(script_name: str) -> dict[str, Path]:
    pattern = f"*/skills/scripts/{script_name}.py"
    return {
        path.relative_to(WORKSPACE_ROOT).parts[0]: path
        for path in WORKSPACE_ROOT.glob(pattern)
        if path.is_file()
    }


def resolve_module_script(script_name: str, module_name: str | None) -> tuple[str, Path]:
    discovered = discover_module_scripts(script_name)
    if module_name:
        script_path = discovered.get(module_name)
        if script_path is None:
            available = ", ".join(sorted(discovered)) or "(none)"
            raise SystemExit(f"[python-frontend-dev] module not found: {module_name}. available: {available}")
        return module_name, script_path

    if not discovered:
        raise SystemExit(f"[python-frontend-dev] no module script found for: {script_name}")

    if len(discovered) > 1:
        available = ", ".join(sorted(discovered))
        raise SystemExit(f"[python-frontend-dev] multiple modules available, use --module. available: {available}")

    return next(iter(discovered.items()))


def load_module_main(script_path: Path) -> Callable[[list[str] | None], int]:
    module_name = ".".join(script_path.relative_to(WORKSPACE_ROOT).with_suffix("").parts)
    module = importlib.import_module(module_name)
    main = getattr(module, "main", None)
    if not callable(main):
        raise SystemExit(f"[python-frontend-dev] main() not found in: {module_name}")
    return main