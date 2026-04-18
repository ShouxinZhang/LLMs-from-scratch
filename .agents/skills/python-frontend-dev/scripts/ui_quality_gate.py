#!/usr/bin/env python3
from __future__ import annotations

import argparse
from module_dispatch import discover_module_scripts, load_module_main, resolve_module_script


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dispatch Python frontend UI quality gate to a module-local script.")
    parser.add_argument("--module", default=None, help="Game module name, for example: pixel_coin_game")
    parser.add_argument("--list-modules", action="store_true", help="List available game modules and exit.")
    args, remaining = parser.parse_known_args(argv)

    if args.list_modules:
        for module_name in sorted(discover_module_scripts("ui_quality_gate")):
            print(module_name)
        return 0

    _, script_path = resolve_module_script("ui_quality_gate", args.module)
    delegated_main = load_module_main(script_path)
    return delegated_main(remaining)


if __name__ == "__main__":
    raise SystemExit(main())