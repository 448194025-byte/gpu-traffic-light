---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 37036b23036446f3adab123ffd44ca42_ffec146f790111f19641525400d9a7a1
    ReservedCode1: XlG8ZXwvQokbji9LqjxigiXmSmgOZ/uBErvS7MOpKZQGdz/OqeSirH3fwuEs99oHjXUjnkTf/qQHqzYwTfduXTpHyDXvKZds+t2JcT0LOlfZ8QIDNpBa1D2xNYC8cxq9OhfSqOlFfKjxSq1lxsloBDPBaRAe3QHrlJpK8zn04Mo74l5yOabO/WCIpPE=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 37036b23036446f3adab123ffd44ca42_ffec146f790111f19641525400d9a7a1
    ReservedCode2: XlG8ZXwvQokbji9LqjxigiXmSmgOZ/uBErvS7MOpKZQGdz/OqeSirH3fwuEs99oHjXUjnkTf/qQHqzYwTfduXTpHyDXvKZds+t2JcT0LOlfZ8QIDNpBa1D2xNYC8cxq9OhfSqOlFfKjxSq1lxsloBDPBaRAe3QHrlJpK8zn04Mo74l5yOabO/WCIpPE=
---

# GPU Traffic Light

> A skeuomorphic desktop GPU-monitoring widget — because your GPU deserves a real traffic light.

![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

<p align="center">
  <i>Screenshot placeholder — coming soon</i>
</p>

A borderless, always-on-top desktop widget that reads GPU 3D-engine utilisation via Windows Performance Counters and renders a photorealistic three-lamp traffic light with:

- **Green**  — idle / low load (＜30 %)
- **Yellow** — moderate load (30–60 %)
- **Red**    — high load (＞60 %)

The active lamp blinks to catch your eye. Right-click hides to the system tray; mouse-wheel scales the widget; drag-and-drop snaps to screen edges.

## Features

- **Photorealistic rendering** — radial-gradients, Fresnel lens rings, specular highlights, chamfered metal housing, rivets, visors, and light wells — all procedurally generated with PIL at 3× internal resolution
- **Blinking indicator** — 600 ms on / 300 ms off
- **System tray** — close hides to tray; double-click tray icon to restore; right-click menu to quit
- **Edge snapping** — snaps to screen edges within 20 px when dropped
- **Mouse-wheel scaling** — 0.3× to 2.0×
- **Single instance** — Windows mutex guard
- **Lightweight** — ~2 s GPU polling interval, negligible CPU footprint

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
| Quit permanently      | Tray icon → right-click → 退出 |

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
├── gpu_traffic_light.py   # Main application
├── requirements.txt
├── LICENSE
└── README.md
```

## License

MIT — see [LICENSE](LICENSE) for details.
