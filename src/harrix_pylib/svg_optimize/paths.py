"""Parse and optimize SVG path data."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"

CURVE_COMMANDS = frozenset({"C", "c", "S", "s", "Q", "q", "T", "t", "A", "a"})
COMMAND_ARGS = {
    "M": 2,
    "m": 2,
    "L": 2,
    "l": 2,
    "H": 1,
    "h": 1,
    "V": 1,
    "v": 1,
    "C": 6,
    "c": 6,
    "S": 4,
    "s": 4,
    "Q": 4,
    "q": 4,
    "T": 2,
    "t": 2,
    "A": 7,
    "a": 7,
    "Z": 0,
    "z": 0,
}


def format_path_data(commands: list[tuple[str, list[float]]]) -> str:
    """Format path commands into a compact d attribute."""
    parts: list[str] = []
    for index, (cmd, args) in enumerate(commands):
        if cmd in {"Z", "z"}:
            parts.append("z")
            continue
        formatted_args = _format_args_spaced(args)
        if index == 0 and cmd == "M":
            parts.append(f"M{formatted_args}")
        elif parts and parts[-1] == "z" and cmd == "m":
            parts.append(f"m{formatted_args}")
        elif cmd in {"h", "v"}:
            parts.append(f"{cmd}{_format_args_spaced(args).replace(' ', '')}")
        elif cmd == "l":
            parts.append(f"l{_format_args_spaced(args)}")
        else:
            parts.append(f"{cmd}{formatted_args}")
    return "".join(parts)


def optimize_path_data(path_data: str) -> str:
    """Optimize a path d attribute string."""
    commands = parse_path_data(path_data)
    if not _is_valid_command_list(commands):
        return _minimal_path_cleanup(path_data)
    commands = _optimize_commands(commands)
    return format_path_data(commands)


def optimize_paths(root: etree._Element) -> bool:
    """Optimize path d attributes. Returns True if any path changed."""
    changed = False
    for elem in root.iter(f"{{{SVG_NS}}}path"):
        d = elem.get("d")
        if not d:
            continue
        optimized = optimize_path_data(d)
        if optimized != d:
            elem.set("d", optimized)
            changed = True
    return changed


def parse_path_data(path_data: str) -> list[tuple[str, list[float]]]:
    """Parse SVG path data into command tuples."""
    tokens = re.findall(
        r"[MmZzLlHhVvCcSsQqTtAa]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?",
        path_data.replace(",", " "),
    )
    commands: list[tuple[str, list[float]]] = []
    index = 0
    command = "M"
    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command in {"Z", "z"}:
                commands.append((command, []))
            continue

        arg_count = COMMAND_ARGS[command]
        args: list[float] = []
        while len(args) < arg_count and index < len(tokens) and not tokens[index].isalpha():
            args.append(float(tokens[index]))
            index += 1
        if not args:
            break
        commands.append((command, args))
        if command in {"M", "m"}:
            command = "l" if command == "m" else "L"
    return commands


def _format_args_spaced(args: list[float]) -> str:
    return " ".join(_format_number(value) for value in args)


def _format_number(value: float) -> str:
    value = _trim_number(value)
    if value == int(value):
        return str(int(value))
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def _is_valid_command_list(commands: list[tuple[str, list[float]]]) -> bool:
    for cmd, args in commands:
        if cmd in {"Z", "z"}:
            continue
        if len(args) != COMMAND_ARGS[cmd]:
            return False
    return bool(commands)


def _minimal_path_cleanup(path_data: str) -> str:
    tokens = re.findall(
        r"[MmZzLlHhVvCcSsQqTtAa]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?",
        path_data.replace(",", " "),
    )
    parts: list[str] = []
    for token in tokens:
        if token.isalpha():
            parts.append(token)
        else:
            number = _format_number(float(token))
            if parts and not parts[-1].isalpha() and not number.startswith("-"):
                parts.append(" ")
            parts.append(number)
    return "".join(parts).replace("  ", " ")


def _optimize_commands(commands: list[tuple[str, list[float]]]) -> list[tuple[str, list[float]]]:
    result: list[tuple[str, list[float]]] = []
    pos = [0.0, 0.0]
    start = [0.0, 0.0]
    for cmd, args in commands:
        if cmd in CURVE_COMMANDS:
            trimmed = [_trim_number(value) for value in args]
            result.append((cmd, trimmed))
            pos = _update_pos_for_curve(cmd, trimmed, pos)
            continue
        if cmd in {"M", "m"}:
            if len(args) < _MIN_POINT_ARGS:
                result.append((cmd, args))
                continue
            x, y = _resolve_point(cmd, args, pos)
            if result and result[-1][0] in {"z", "Z"}:
                result.append(("m", [x - pos[0], y - pos[1]]))
            else:
                result.append(("M", [x, y]))
            pos = [x, y]
            start = pos.copy()
            continue
        if cmd in {"L", "l"}:
            if len(args) < _MIN_POINT_ARGS:
                result.append((cmd, args))
                continue
            x, y = _resolve_point(cmd, args, pos)
            rel_cmd, rel_args = _relative_line(pos, [x, y])
            pos = [x, y]
            result.append((rel_cmd, rel_args))
            continue
        if cmd in {"H", "h"}:
            if len(args) < 1:
                result.append((cmd, args))
                continue
            x = pos[0] + args[0] if cmd == "h" else args[0]
            rel_cmd, rel_args = _relative_line(pos, [x, pos[1]])
            pos = [x, pos[1]]
            result.append((rel_cmd, rel_args))
            continue
        if cmd in {"V", "v"}:
            if len(args) < 1:
                result.append((cmd, args))
                continue
            y = pos[1] + args[0] if cmd == "v" else args[0]
            rel_cmd, rel_args = _relative_line(pos, [pos[0], y])
            pos = [pos[0], y]
            result.append((rel_cmd, rel_args))
            continue
        if cmd in {"Z", "z"}:
            pos = start.copy()
            result.append(("z", []))
            continue
        result.append((cmd, args))
    return result


def _relative_line(pos: list[float], target: list[float]) -> tuple[str, list[float]]:
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    if dy == 0 and dx != 0:
        return ("h", [dx])
    if dx == 0 and dy != 0:
        return ("v", [dy])
    return ("l", [dx, dy])


def _resolve_point(cmd: str, args: list[float], pos: list[float]) -> list[float]:
    if cmd.islower():
        return [pos[0] + args[0], pos[1] + args[1]]
    return [args[0], args[1]]


def _trim_number(value: float) -> float:
    if abs(value - round(value)) < _FLOAT_EPSILON:
        return round(value)
    return round(value, 4)


def _update_pos_for_curve(cmd: str, args: list[float], pos: list[float]) -> list[float]:
    if cmd in {"C", "c"}:
        return [pos[0] + args[4], pos[1] + args[5]] if cmd == "c" else [args[4], args[5]]
    if cmd in {"S", "s"}:
        return [pos[0] + args[2], pos[1] + args[3]] if cmd == "s" else [args[2], args[3]]
    if cmd in {"Q", "q"}:
        return [pos[0] + args[2], pos[1] + args[3]] if cmd == "q" else [args[2], args[3]]
    if cmd in {"A", "a"}:
        return [pos[0] + args[5], pos[1] + args[6]] if cmd == "a" else [args[5], args[6]]
    if cmd in {"T", "t"}:
        return [pos[0] + args[0], pos[1] + args[1]] if cmd == "t" else [args[0], args[1]]
    return pos


_FLOAT_EPSILON = 1e-6
_MIN_POINT_ARGS = 2
