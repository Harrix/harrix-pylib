---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `img_tools.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `convert_gif_mp4_to_avif`](#-function-convert_gif_mp4_to_avif)
- [🔧 Function `get_frame_rate`](#-function-get_frame_rate)
- [🔧 Function `is_avif_animated`](#-function-is_avif_animated)
- [🔧 Function `optimize_avif`](#-function-optimize_avif)
- [🔧 Function `optimize_image_with_tools`](#-function-optimize_image_with_tools
  )
- [🔧 Function `process_animated_avif`](#-function-process_animated_avif)
- [🔧 Function `process_static_avif`](#-function-process_static_avif)
- [🔧 Function `_exe`](#-function-_exe)
- [🔧 Function `_ffmpeg_output`](#-function-_ffmpeg_output)
- [🔧 Function `_is_avif_animated_with_avifdec`](#-function-_is_avif_animated_wi
  th_avifdec)
- [🔧 Function `_reduce_frames`](#-function-_reduce_frames)
- [🔧 Function `_resize_frames`](#-function-_resize_frames)
- [🔧 Function `_run_checked`](#-function-_run_checked)
- [🔧 Function `_scale_vf`](#-function-_scale_vf)
- [🔧 Function `_sequence_pattern`](#-function-_sequence_pattern)

</details>

## 🔧 Function `convert_gif_mp4_to_avif`

```python
def convert_gif_mp4_to_avif(source: Path, output: Path, project_root: Path) -> None
```

Convert GIF or MP4 to AVIF using ffmpeg.

<details>
<summary>Code:</summary>

```python
def convert_gif_mp4_to_avif(
    source: Path,
    output: Path,
    project_root: Path,
    *,
    max_size: int | None = None,
) -> None:
    ffmpeg = _exe(project_root, "ffmpeg")
    args = [str(ffmpeg), "-i", str(source)]
    scale_vf = _scale_vf(max_size)
    if scale_vf:
        args.extend(["-vf", scale_vf])
    args.extend(
        [
            "-c:a",
            "copy",
            "-c:v",
            "libaom-av1",
            "-crf",
            "30",
            "-cpu-used",
            "4",
            "-pix_fmt",
            "yuv420p",
            "-y",
            str(output),
        ]
    )
    _run_checked(args)
```

</details>

## 🔧 Function `get_frame_rate`

```python
def get_frame_rate(source: Path, project_root: Path) -> float
```

Detect frame rate from media file using ffmpeg output.

<details>
<summary>Code:</summary>

```python
def get_frame_rate(source: Path, project_root: Path) -> float:
    ffmpeg = _exe(project_root, "ffmpeg")
    output = _ffmpeg_output(source, ffmpeg)
    fps = _DEFAULT_FPS
    for line in output.splitlines():
        match = re.search(r"(\d+(?:\.\d+)?)\s*fps", line)
        if not match:
            continue
        detected = float(match.group(1))
        if _MIN_VALID_FPS < detected < _MAX_VALID_FPS:
            fps = detected
            if "Stream #0:1" in line:
                break
    return fps
```

</details>

## 🔧 Function `is_avif_animated`

```python
def is_avif_animated(source: Path, project_root: Path) -> bool
```

Return True if AVIF contains more than one frame.

<details>
<summary>Code:</summary>

```python
def is_avif_animated(source: Path, project_root: Path) -> bool:
    ffmpeg = _exe(project_root, "ffmpeg")
    output = _ffmpeg_output(source, ffmpeg)
    duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)", output)
    frame_match = re.search(r"(\d+)\s+frames?", output, re.IGNORECASE)
    if duration_match:
        hours = int(duration_match.group(1))
        minutes = int(duration_match.group(2))
        seconds = float(duration_match.group(3))
        if hours * 3600 + minutes * 60 + seconds > _MIN_ANIMATED_DURATION_SECONDS:
            return True
    if frame_match and int(frame_match.group(1)) > 1:
        return True
    return _is_avif_animated_with_avifdec(source, project_root)
```

</details>

## 🔧 Function `optimize_avif`

```python
def optimize_avif(source: Path, output: Path, project_root: Path) -> None
```

Optimize AVIF using ffmpeg or avifdec/avifenc depending on animation.

<details>
<summary>Code:</summary>

```python
def optimize_avif(
    source: Path,
    output: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> None:
    if is_avif_animated(source, project_root):
        process_animated_avif(source, output, project_root, quality=quality, max_size=max_size)
    else:
        process_static_avif(source, output, project_root, quality=quality, max_size=max_size)
```

</details>

## 🔧 Function `optimize_image_with_tools`

```python
def optimize_image_with_tools(filename: Path | str, output_filename: Path | str) -> str
```

Optimize a raster image using ffmpeg, avifenc, or avifdec.

Supports `.gif`, `.mp4`, and `.avif` files.

Args:

- `filename` (`Path | str`): Source image path.
- `output_filename` (`Path | str`): Destination path.
- `project_root` (`Path | str`): Folder containing ffmpeg.exe, avifenc.exe,
  avifdec.exe.
- `quality` (`bool`): Use higher quality settings. Defaults to `False`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to
  `None`.

Returns:

- `str`: Status message.

<details>
<summary>Code:</summary>

```python
def optimize_image_with_tools(
    filename: Path | str,
    output_filename: Path | str,
    *,
    project_root: Path | str,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    source = Path(filename)
    target = Path(output_filename)
    root = Path(project_root)
    ext = source.suffix.lower()
    target.parent.mkdir(parents=True, exist_ok=True)

    if ext in {".gif", ".mp4"}:
        convert_gif_mp4_to_avif(source, target, root, max_size=max_size)
        return f"✅ File {source.name} successfully converted to AVIF."
    if ext == ".avif":
        optimize_avif(source, target, root, quality=quality, max_size=max_size)
        return f"✅ File {source.name} successfully optimized."
    msg = f"🔵 File {source.name} is not supported by external tools."
    raise ValueError(msg)
```

</details>

## 🔧 Function `process_animated_avif`

```python
def process_animated_avif(source: Path, output: Path, project_root: Path) -> None
```

Optimize animated AVIF with avifdec and avifenc or ffmpeg.

<details>
<summary>Code:</summary>

```python
def process_animated_avif(
    source: Path,
    output: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> None:
    original_frame_rate = get_frame_rate(source, project_root)
    target_frame_rate = min(original_frame_rate, _MAX_ANIMATED_FPS)
    frames_to_keep_ratio = target_frame_rate / original_frame_rate
    avifdec = _exe(project_root, "avifdec")
    avifenc = _exe(project_root, "avifenc")
    ffmpeg = _exe(project_root, "ffmpeg")

    with tempfile.TemporaryDirectory(prefix="avif_frames_") as temp_dir:
        temp_path = Path(temp_dir)
        frame_base = temp_path / "frame.png"
        _run_checked([str(avifdec), str(source), str(frame_base), "--index", "all"])

        frame_files = sorted(temp_path.glob("frame-*.png"))
        if not frame_files:
            msg = f"No frames extracted from {source.name}"
            raise RuntimeError(msg)

        if original_frame_rate > _MAX_ANIMATED_FPS:
            frame_files = _reduce_frames(frame_files, frames_to_keep_ratio, temp_path)

        if max_size is not None:
            _resize_frames(frame_files, ffmpeg, max_size)

        min_quality = 15 if quality else 25
        max_quality = 20 if quality else 30

        if len(frame_files) > _MANY_FRAMES_THRESHOLD:
            pattern = _sequence_pattern(frame_files[0])
            _run_checked(
                [
                    str(ffmpeg),
                    "-r",
                    str(target_frame_rate),
                    "-f",
                    "image2",
                    "-i",
                    str(pattern),
                    "-c:v",
                    "libaom-av1",
                    "-crf",
                    str(min_quality + 10),
                    "-cpu-used",
                    "4",
                    "-pix_fmt",
                    "yuv420p",
                    "-y",
                    str(output),
                ]
            )
        else:
            args = [str(avifenc), *[str(path) for path in frame_files], "--fps", str(target_frame_rate)]
            args.extend(["--min", str(min_quality), "--max", str(max_quality), str(output)])
            _run_checked(args)
```

</details>

## 🔧 Function `process_static_avif`

```python
def process_static_avif(source: Path, output: Path, project_root: Path) -> None
```

Optimize static AVIF with ffmpeg.

<details>
<summary>Code:</summary>

```python
def process_static_avif(
    source: Path,
    output: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> None:
    crf = 18 if quality else 28
    ffmpeg = _exe(project_root, "ffmpeg")
    args = [
        str(ffmpeg),
        "-i",
        str(source),
        "-c:v",
        "libaom-av1",
        "-crf",
        str(crf),
        "-cpu-used",
        "4",
        "-pix_fmt",
        "yuv420p",
    ]
    scale_vf = _scale_vf(max_size)
    if scale_vf:
        args.extend(["-vf", scale_vf])
    args.extend(["-frames:v", "1", "-y", str(output)])
    _run_checked(args)
```

</details>

## 🔧 Function `_exe`

```python
def _exe(project_root: Path, name: str) -> Path
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _exe(project_root: Path, name: str) -> Path:
    return project_root / f"{name}.exe"
```

</details>

## 🔧 Function `_ffmpeg_output`

```python
def _ffmpeg_output(source: Path, ffmpeg: Path) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _ffmpeg_output(source: Path, ffmpeg: Path) -> str:
    process = subprocess.run(
        [str(ffmpeg), "-i", str(source), "-f", "null", "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return "\n".join(filter(None, [(process.stdout or "").strip(), (process.stderr or "").strip()]))
```

</details>

## 🔧 Function `_is_avif_animated_with_avifdec`

```python
def _is_avif_animated_with_avifdec(source: Path, project_root: Path) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_avif_animated_with_avifdec(source: Path, project_root: Path) -> bool:
    avifdec = _exe(project_root, "avifdec")
    with tempfile.TemporaryDirectory(prefix="avif_check_") as temp_dir:
        temp_path = Path(temp_dir)
        first_frame = temp_path / "check_frame.png"
        _run_checked([str(avifdec), str(source), str(first_frame), "--index", "0"])
        if not list(temp_path.glob("*.png")):
            return False
        second_frame = temp_path / "check_frame2.png"
        process = subprocess.run(
            [str(avifdec), str(source), str(second_frame), "--index", "1"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        return process.returncode == 0 and any(temp_path.glob("*check_frame2*.png"))
```

</details>

## 🔧 Function `_reduce_frames`

```python
def _reduce_frames(frame_files: list[Path], frames_to_keep_ratio: float, temp_path: Path) -> list[Path]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _reduce_frames(frame_files: list[Path], frames_to_keep_ratio: float, temp_path: Path) -> list[Path]:
    original_count = len(frame_files)
    target_count = max(1, round(original_count * frames_to_keep_ratio))
    keep_indexes = {
        round(index * (original_count - 1) / (target_count - 1)) if target_count > 1 else 0
        for index in range(target_count)
    }
    kept_frames: list[Path] = []
    for index, frame_path in enumerate(frame_files):
        if index not in keep_indexes:
            frame_path.unlink(missing_ok=True)
            continue
        new_name = f"kept-frame-{len(kept_frames):06d}.png"
        new_path = temp_path / new_name
        frame_path.rename(new_path)
        kept_frames.append(new_path)
    return kept_frames
```

</details>

## 🔧 Function `_resize_frames`

```python
def _resize_frames(frame_files: list[Path], ffmpeg: Path, max_size: int) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _resize_frames(frame_files: list[Path], ffmpeg: Path, max_size: int) -> None:
    scale_vf = _scale_vf(max_size)
    if scale_vf is None:
        return
    for frame_path in frame_files:
        temp_path = frame_path.with_name(f"temp_{frame_path.name}")
        _run_checked(
            [str(ffmpeg), "-y", "-i", str(frame_path), "-vf", scale_vf, str(temp_path)],
        )
        temp_path.replace(frame_path)
```

</details>

## 🔧 Function `_run_checked`

```python
def _run_checked(args: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _run_checked(args: list[str]) -> str:
    process = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if process.returncode != 0:
        details = (process.stderr or process.stdout or "").strip()
        msg = details or f"Command failed: {' '.join(args)}"
        raise RuntimeError(msg)
    return (process.stdout or "").strip()
```

</details>

## 🔧 Function `_scale_vf`

```python
def _scale_vf(max_size: int | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _scale_vf(max_size: int | None) -> str | None:
    if max_size is None:
        return None
    return f"scale='if(gt(iw,ih),min({max_size},iw),-1)':'if(gt(iw,ih),-1,min({max_size},ih))'"
```

</details>

## 🔧 Function `_sequence_pattern`

```python
def _sequence_pattern(frame_file: Path) -> Path
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _sequence_pattern(frame_file: Path) -> Path:
    stem = frame_file.stem
    match = re.search(r"\d+", stem)
    if not match:
        return frame_file
    prefix = stem[: match.start()]
    suffix = frame_file.suffix
    return frame_file.with_name(f"{prefix}%06d{suffix}")
```

</details>
