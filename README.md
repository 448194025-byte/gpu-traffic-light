# GPU Traffic Light

> A skeuomorphic desktop GPU-monitoring widget 鈥?because your GPU deserves a real traffic light.

![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

<p align="center">
  <i>Screenshot placeholder 鈥?coming soon</i>
</p>

A borderless, always-on-top desktop widget that reads GPU 3D-engine utilisation via Windows Performance Counters and renders a photorealistic three-lamp traffic light with:

- **Green**  鈥?idle / low load (锛?0 %)
- **Yellow** 鈥?moderate load (30鈥?0 %)
- **Red**    鈥?high load (锛?0 %)

The active lamp blinks to catch your eye. Right-click hides to the system tray; mouse-wheel scales the widget; drag-and-drop snaps to screen edges.

## Features

- **Photorealistic rendering** 鈥?radial-gradients, Fresnel lens rings, specular highlights, chamfered metal housing, rivets, visors, and light wells 鈥?all procedurally generated with PIL at 3脳 internal resolution
- **Blinking indicator** 鈥?600 ms on / 300 ms off
- **System tray** 鈥?close hides to tray; double-click tray icon to restore; right-click menu to quit
- **Edge snapping** 鈥?snaps to screen edges within 20 px when dropped
- **Mouse-wheel scaling** 鈥?0.3脳 to 2.0脳
- **Single instance** 鈥?Windows mutex guard
- **Lightweight** 鈥?~2 s GPU polling interval, negligible CPU footprint

## Requirements

- Windows 10 or 11
- Python 3.8 or later

### Python packages

```bash
pip install -r requirements.txt
```

| Package   | Purpose                  |
|-----------|--------------------------|
| Pillow    | Image generation         |
| pywin32   | Mutex & Windows API      |
| pystray   | System tray integration  |

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/gpu-traffic-light.git
cd gpu-traffic-light
pip install -r requirements.txt
python gpu_traffic_light.py
```

## Usage

| Action                | How                            |
|-----------------------|--------------------------------|
| Move widget           | Left-drag anywhere on widget   |
| Resize                | Mouse-wheel scroll             |
| Hide to tray          | Right-click on widget          |
| Show from tray        | Double-click tray icon         |
| Quit permanently      | Tray icon 鈫?right-click 鈫?閫€鍑?|

The widget starts in the top-right corner of your primary monitor.

## How It Works

`gpu_traffic_light.py` queries the Windows `typeperf` counter:

```
\GPU Engine(*)\Utilization Percentage
```

It filters for `engtype_3D` entries and takes the maximum as the current GPU load. The image is rendered with `PIL.ImageDraw`, cached for the four states (all-off / red / yellow / green), and displayed on a transparent `tkinter` canvas.

## Project Structure

```
gpu-traffic-light/
鈹溾攢鈹€ gpu_traffic_light.py   # Main application
鈹溾攢鈹€ requirements.txt
鈹溾攢鈹€ LICENSE
鈹斺攢鈹€ README.md
```

## License

MIT 鈥?see [LICENSE](LICENSE) for details.
