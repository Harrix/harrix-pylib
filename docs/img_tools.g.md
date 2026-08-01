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
- [🔧 Function `optimize_image_with_tools`](#-function-optimize_image_with_tools)
- [🔧 Function `process_animated_avif`](#-function-process_animated_avif)
- [🔧 Function `process_static_avif`](#-function-process_static_avif)

</details>

## 🔧 Function `convert_gif_mp4_to_avif`

```python
def convert_gif_mp4_to_avif(source: Path | str, output: Path | str, project_root: Path | str) -> None
```

Convert GIF or MP4 to AVIF using ffmpeg.

Args:

- `source` (`Path | str`): Source GIF or MP4 file.
- `output` (`Path | str`): Destination AVIF file.
- `project_root` (`Path | str`): Folder containing `ffmpeg.exe`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.

Returns:

- `None`.

<details>
<summary>Code:</summary>

```python
def convert_gif_mp4_to_avif(
    source: Path | str,
    output: Path | str,
    project_root: Path | str,
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
def get_frame_rate(source: Path | str, project_root: Path | str) -> float
```

Detect frame rate from media file using ffmpeg output.

Args:

- `source` (`Path | str`): Media file to inspect.
- `project_root` (`Path | str`): Folder containing `ffmpeg.exe`.

Returns:

- `float`: Detected frames per second, or `10.0` when detection fails.

<details>
<summary>Code:</summary>

```python
def get_frame_rate(source: Path | str, project_root: Path | str) -> float:
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
def is_avif_animated(source: Path | str, project_root: Path | str) -> bool
```

Return `True` if AVIF contains more than one frame.

Args:

- `source` (`Path | str`): AVIF file to inspect.
- `project_root` (`Path | str`): Folder containing `ffmpeg.exe` and `avifdec.exe`.

Returns:

- `bool`: `True` when the file is animated.

<details>
<summary>Code:</summary>

```python
def is_avif_animated(source: Path | str, project_root: Path | str) -> bool:
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
def optimize_avif(source: Path | str, output: Path | str, project_root: Path | str) -> None
```

Optimize AVIF using ffmpeg or avifdec/avifenc depending on animation.

Args:

- `source` (`Path | str`): Source AVIF file.
- `output` (`Path | str`): Destination AVIF file.
- `project_root` (`Path | str`): Folder containing `ffmpeg.exe`, `avifenc.exe`, `avifdec.exe`.
- `quality` (`bool`): Use higher quality settings. Defaults to `False`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.

Returns:

- `None`.

<details>
<summary>Code:</summary>

```python
def optimize_avif(
    source: Path | str,
    output: Path | str,
    project_root: Path | str,
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
- `project_root` (`Path | str`): Folder containing `ffmpeg.exe`, `avifenc.exe`, `avifdec.exe`.
- `quality` (`bool`): Use higher quality settings. Defaults to `False`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.

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
def process_animated_avif(source: Path | str, output: Path | str, project_root: Path | str) -> None
```

Optimize animated AVIF with avifdec and avifenc or ffmpeg.

Args:

- `source` (`Path | str`): Source animated AVIF file.
- `output` (`Path | str`): Destination AVIF file.
- `project_root` (`Path | str`): Folder containing `ffmpeg.exe`, `avifenc.exe`, `avifdec.exe`.
- `quality` (`bool`): Use higher quality settings. Defaults to `False`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.

Returns:

- `None`.

<details>
<summary>Code:</summary>

```python
def process_animated_avif(
    source: Path | str,
    output: Path | str,
    project_root: Path | str,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> None:
    source = Path(source)
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
def process_static_avif(source: Path | str, output: Path | str, project_root: Path | str) -> None
```

Optimize static AVIF with ffmpeg.

Args:

- `source` (`Path | str`): Source static AVIF file.
- `output` (`Path | str`): Destination AVIF file.
- `project_root` (`Path | str`): Folder containing `ffmpeg.exe`.
- `quality` (`bool`): Use higher quality settings. Defaults to `False`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.

Returns:

- `None`.

<details>
<summary>Code:</summary>

```python
def process_static_avif(
    source: Path | str,
    output: Path | str,
    project_root: Path | str,
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
