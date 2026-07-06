"""
GPU Traffic Light (GPU 红绿灯)
===============================
A skeuomorphic desktop widget that monitors NVIDIA/AMD GPU usage
and displays it as a realistic traffic light indicator.

- Green  (< 30%) : Idle / Low load
- Yellow (30-60%): Moderate load
- Red    (> 60%) : High load

The indicator sits on your desktop as a borderless, always-on-top
widget with system tray integration. Lights blink to draw attention
and the widget supports drag, edge-snap, and mouse-wheel scaling.

Author : Marvis AI
License: MIT
Platform: Windows 10/11 (requires Python 3.8+)
"""

import tkinter as tk
import subprocess
import csv
import io
import threading
import time
import sys

import win32event
import win32api
import winerror
from PIL import Image, ImageDraw, ImageTk

# ──────────────────────────────────────────────────────────
#  Layout constants (internal resolution ×3 for crispness)
# ──────────────────────────────────────────────────────────
SCALE   = 3
PAD     = 20
LR      = 70                     # light radius (78 % of body width)
GAP     = 20
SW_IMG  = PAD * 2 + LR * 2      # 180
SH_IMG  = PAD * 2 + LR * 6 + GAP * 2  # 500
IMG_W   = SW_IMG + 16           # 196
IMG_H   = SH_IMG + 26           # 526
RAD     = 16                    # corner radius of housing

# Thresholds
LO = 30
HI = 60

# Behaviour
BLINK_ON  = 600
BLINK_OFF = 300
SNAP_DIST = 20
POLL_MS   = 2000

# ── Colours ──────────────────────────────────────────────
SHELL_BG   = (58, 58, 58)
SHELL_HL   = (90, 90, 90)
SHELL_SH   = (28, 28, 28)
SHELL_EDGE = (48, 48, 48)
CHAMFER_HL = (105, 105, 105)
CHAMFER_SH = (20, 20, 20)
VISOR_BG   = (30, 30, 30)
VISOR_HL   = (55, 55, 55)
WELL_C     = (6, 6, 6)

OFF_COLORS = [(18, 0, 0), (18, 14, 0), (0, 14, 0)]
ON_COLORS  = [(235, 50, 50), (255, 200, 20), (40, 180, 60)]
ON_CTR     = [(255, 120, 120), (255, 240, 140), (130, 240, 150)]

TRANSP = (1, 1, 1)


# ──────────────────────────────────────────────────────────
#  PIL drawing helpers
# ──────────────────────────────────────────────────────────
def rr(d, x1, y1, x2, y2, r, **kw):
    """Shorthand for rounded_rectangle."""
    d.rounded_rectangle([x1, y1, x2, y2], r, **kw)


def radial(draw, cx, cy, r, outer, inner, steps=20):
    """Draw concentric gradient ellipses from *outer* to *inner*."""
    for s in range(steps):
        t = s / (steps - 1)
        cr = int(r * (1 - t))
        rr_c = outer[0] + int((inner[0] - outer[0]) * t)
        gg   = outer[1] + int((inner[1] - outer[1]) * t)
        bb   = outer[2] + int((inner[2] - outer[2]) * t)
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr],
                     fill=(rr_c, gg, bb))


def fresnel(draw, cx, cy, r, alpha):
    """Draw concentric Fresnel-like rings on a lens."""
    for ratio in [0.38, 0.46, 0.54, 0.62, 0.70, 0.78, 0.86, 0.94]:
        cr = int(r * ratio)
        a = int(alpha * (0.6 + 0.4 * (ratio - 0.38) / 0.56))
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr],
                     outline=(255, 255, 255, a), width=1)


# ──────────────────────────────────────────────────────────
#  Image generation
# ──────────────────────────────────────────────────────────
def gen_img(active):
    """
    Generate a single RGBA frame of the traffic light.

    Parameters
    ----------
    active : int
        -1 = all dark,  0 = red,  1 = yellow,  2 = green.
    """
    img = Image.new('RGBA', (IMG_W, IMG_H), TRANSP + (0,))
    d = ImageDraw.Draw(img)
    ox, oy = 8, 4
    w, h = SW_IMG, SH_IMG

    # ── Metal housing (3D look) ──────────────────────────
    rr(d, ox + 1, oy + 1, ox + w + 2, oy + h + 2, RAD + 1,
       fill=(15, 15, 15))
    rr(d, ox, oy, ox + w, oy + h, RAD, fill=SHELL_EDGE)
    rr(d, ox + 2, oy + 2, ox + w - 2, oy + h - 2, RAD - 2,
       fill=SHELL_BG)

    # Left chamfer highlight
    for i in range(5):
        a = int(50 - i * 8)
        d.line([(ox + RAD + i, oy + 3),
                (ox + RAD + i, oy + h - 3)],
               fill=(*CHAMFER_HL, a), width=1)
    # Right shadow
    for i in range(4):
        d.line([(ox + w - 1 - i, oy + RAD),
                (ox + w - 1 - i, oy + h - RAD)],
               fill=SHELL_SH, width=1)
    # Top edge
    d.line([(ox + RAD, oy + 1), (ox + w - RAD, oy + 1)],
           fill=CHAMFER_HL, width=1)

    # Corner rivets
    for rx, ry in [(ox + 8, oy + 8), (ox + w - 8, oy + 8),
                   (ox + 8, oy + h - 8), (ox + w - 8, oy + h - 8)]:
        d.ellipse([rx - 3, ry - 3, rx + 3, ry + 3],
                  fill=(70, 70, 70), outline=(40, 40, 40))
        d.ellipse([rx - 1, ry - 1, rx + 1, ry + 1],
                  fill=(100, 100, 100))

    # ── Bottom mount ─────────────────────────────────────
    cx = IMG_W // 2
    fy = oy + h
    rr(d, cx - 12, fy, cx + 12, fy + 10, 3,
       fill=(45, 45, 45), outline=(70, 70, 70))
    d.rectangle([cx - 5, fy + 4, cx + 5, fy + 16],
                fill=(35, 35, 35), outline=(55, 55, 55))
    d.line([(cx - 2, fy + 6), (cx - 2, fy + 14)], fill=(60, 60, 60))
    d.ellipse([cx - 3, fy, cx + 3, fy + 6],
              fill=(60, 60, 60), outline=(35, 35, 35))

    # ── Three lights ─────────────────────────────────────
    for i in range(3):
        lx = IMG_W // 2
        ly = oy + PAD + LR + i * (LR * 2 + GAP)

        # Visor (hood above light)
        vh = int(LR * 0.35)
        d.chord([lx - LR - 10, ly - LR - vh,
                 lx + LR + 10, ly - LR + 12],
                0, 180, fill=VISOR_BG, outline=VISOR_HL, width=2)

        # Light well (recessed socket)
        wm = 4
        d.ellipse([lx - LR - wm, ly - LR - wm,
                   lx + LR + wm, ly + LR + wm], fill=WELL_C)
        d.ellipse([lx - LR - wm, ly - LR - wm,
                   lx + LR + wm, ly + LR + wm],
                  outline=(20, 20, 20), width=2)

        if i == active:
            # ══  ON  ═════════════════════════════════════
            # Outer glow
            for g in range(8):
                gr = LR + g * 3
                al = int(35 * (1 - g / 8))
                ge = Image.new('RGBA', (IMG_W, IMG_H), (0, 0, 0, 0))
                gd = ImageDraw.Draw(ge)
                gd.ellipse([lx - gr, ly - gr, lx + gr, ly + gr],
                           fill=(*ON_COLORS[i], al))
                d._image.paste(ge, (0, 0), ge)

            # Lens gradient
            radial(d, lx, ly, LR, ON_COLORS[i], ON_CTR[i], 20)
            # Fresnel texture
            fresnel(d, lx, ly, LR, 35)

            # Specular highlight arc
            hl = LR * 0.5
            d.arc([lx - hl - 3, ly - hl - 8,
                   lx + hl - 3, ly + hl - 8],
                  140, 70, fill=(255, 255, 255, 200), width=3)
            # Bottom shadow
            d.arc([lx - LR + 5, ly, lx + LR - 5, ly + LR + 5],
                  0, 55, fill=(0, 0, 0, 35), width=2)
        else:
            # ══  OFF  ════════════════════════════════════
            # Dark glass lens with subtle reflection
            d.ellipse([lx - LR, ly - LR, lx + LR, ly + LR],
                      fill=OFF_COLORS[i])
            for s in range(6):
                t = s / 5
                cr = int(LR * (1 - t))
                al = int(10 * t)
                d.ellipse([lx - cr, ly - cr, lx + cr, ly + cr],
                          fill=(*OFF_COLORS[i][:3], al))
            # Ambient reflection
            d.arc([lx - LR * 0.5, ly - LR * 0.5 - 4,
                   lx + LR * 0.1, ly + LR * 0.1 - 4],
                  130, 60, fill=(255, 255, 255, 25), width=1)
            fresnel(d, lx, ly, LR, 8)

    # Make transparent colour key actually transparent
    arr = img.load()
    for yy in range(IMG_H):
        for xx in range(IMG_W):
            if arr[xx, yy][:3] == TRANSP:
                arr[xx, yy] = (1, 1, 1, 0)

    return img


# ──────────────────────────────────────────────────────────
#  System tray icon
# ──────────────────────────────────────────────────────────
def tray_icon():
    """Generate a 64×64 RGBA icon for the system tray."""
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rr(d, 16, 6, 48, 100, 5,
       fill=(58, 58, 58), outline=(90, 90, 90), width=1)
    for i, c in enumerate([(235, 50, 50), (255, 200, 20), (40, 180, 60)]):
        lx, ly = 32, int(20 + 22 * i)
        r = 8
        d.ellipse([lx - r - 1, ly - r - 1, lx + r + 1, ly + r + 1],
                  fill=(8, 8, 8))
        d.ellipse([lx - r, ly - r, lx + r, ly + r], fill=c)
        d.arc([lx - 3, ly - 5, lx + 2, ly - 1],
              140, 50, fill=(255, 255, 255, 180), width=1)
    return img


# ──────────────────────────────────────────────────────────
#  GPU usage polling via Windows Performance Counter
# ──────────────────────────────────────────────────────────
def gpu():
    """
    Query the 3D engine utilisation percentage from typeperf.

    Returns
    -------
    int
        0-100 if successful, -1 on failure.
    """
    try:
        r = subprocess.run(
            ['typeperf', '-sc', '1',
             r'\GPU Engine(*)\Utilization Percentage'],
            capture_output=True, text=True,
            timeout=10, creationflags=0x08000000)
        rd = csv.reader(io.StringIO(r.stdout.strip()))
        h = next(rd, None)
        row = next(rd, None)
        if not h or not row:
            return -1
        mx = 0.0
        for i, c in enumerate(h):
            if 'engtype_3D' in c and i < len(row):
                try:
                    v = float(row[i].strip().strip('"'))
                    if v > mx:
                        mx = v
                except ValueError:
                    pass
        return round(mx)
    except Exception:
        return -1


# ──────────────────────────────────────────────────────────
#  Main application
# ──────────────────────────────────────────────────────────
class App:
    """Desktop traffic-light widget for GPU monitoring."""

    def __init__(self):
        self.usage = -1
        self.running = True
        self.blink = True
        self.scale = 1.0
        self.imgs = {
            -1: gen_img(-1), 0: gen_img(0),
            1: gen_img(1), 2: gen_img(2),
        }
        self.root = tk.Tk()
        self.root.withdraw()
        self._win()
        self._tray()
        self._draw()
        self._blink()
        self._poll()

    # ── Window ───────────────────────────────────────────
    def _win(self):
        self.w = tk.Toplevel(self.root)
        self.w.overrideredirect(True)
        self.w.attributes('-topmost', True)
        self.w.attributes('-transparentcolor', '#010101')
        self.w.configure(bg='#010101')
        self.c = tk.Canvas(self.w, bg='#010101',
                           bd=0, highlightthickness=0)
        self.c.pack(fill='both', expand=True)
        self._rsz()
        sw = self.w.winfo_screenwidth()
        self.w.geometry(f'+{sw - self._w - 24}+24')
        self.c.bind('<Button-1>',
                    lambda e: setattr(self, '_dx', e.x)
                    or setattr(self, '_dy', e.y))
        self.c.bind('<B1-Motion>', lambda e: self.w.geometry(
            f'+{self.w.winfo_x() + e.x - self._dx}'
            f'+{self.w.winfo_y() + e.y - self._dy}'))
        self.c.bind('<ButtonRelease-1>', self._snap)
        self.c.bind('<Button-3>', lambda e: self._hide())
        self.c.bind('<MouseWheel>', self._zoom)
        self.visible = True

    # ── System tray ──────────────────────────────────────
    def _tray(self):
        import pystray
        self.tray = pystray.Icon(
            'GPUTraffic', tray_icon(), 'GPU 红绿灯',
            menu=pystray.Menu(
                pystray.MenuItem('显示 / 隐藏',
                                 self._toggle, default=True),
                pystray.MenuItem('退出', self._quit)))
        threading.Thread(target=self.tray.run, daemon=True).start()

    def _show(self, *_):  self.w.deiconify(); self.visible = True
    def _hide(self, *_):  self.w.withdraw();  self.visible = False

    def _toggle(self, *_):
        if self.visible:
            self._hide()
        else:
            self._show()

    def _quit(self, *_):
        self.running = False
        self.tray.stop()
        self.root.quit()

    # ── Sizing ───────────────────────────────────────────
    @property
    def _w(self):
        return int(IMG_W * self.scale)

    @property
    def _h(self):
        return int(IMG_H * self.scale)

    def _rsz(self):
        self.w.geometry(f'{self._w}x{self._h}')
        self.c.configure(width=self._w, height=self._h)

    def _scl(self, img):
        return img.resize((self._w, self._h), Image.NEAREST)

    # ── Light logic ──────────────────────────────────────
    def _ai(self):
        u = self.usage
        if u < 0:
            return -1
        if u < LO:
            return 2
        if u < HI:
            return 1
        return 0

    def _draw(self):
        if not self.running:
            return
        if not self.visible:
            self.w.after(POLL_MS, self._draw)
            return
        self.c.delete('all')
        ai = -1 if not self.blink else self._ai()
        self._tk = ImageTk.PhotoImage(self._scl(self.imgs[ai]))
        self.c.create_image(0, 0, anchor='nw', image=self._tk)
        if ai >= 0 and self.usage >= 0:
            oy = (4 + PAD + LR) * self.scale
            ly = oy + LR * self.scale + ai * (LR * 2 + GAP) * self.scale
            lx = IMG_W * self.scale // 2
            fs = max(10, int(20 * self.scale))
            self.c.create_text(lx, ly + 1, text=str(self.usage),
                               fill='white',
                               font=('Segoe UI', fs, 'bold'))
        self.w.after(POLL_MS, self._draw)

    def _blink(self):
        if not self.running:
            return
        self.blink = not self.blink
        self.w.after(BLINK_ON if self.blink else BLINK_OFF, self._blink)

    def _poll(self):
        def loop():
            while self.running:
                self.usage = gpu()
                time.sleep(2)
        threading.Thread(target=loop, daemon=True).start()

    # ── Interactions ─────────────────────────────────────
    def _snap(self, e=None):
        x = self.w.winfo_x()
        y = self.w.winfo_y()
        w = self.w.winfo_width()
        h = self.w.winfo_height()
        sw = self.w.winfo_screenwidth()
        sh = self.w.winfo_screenheight()
        nx, ny = x, y
        if abs(x + w - sw) < SNAP_DIST:
            nx = sw - w
        elif abs(x) < SNAP_DIST:
            nx = 0
        if abs(y) < SNAP_DIST:
            ny = 0
        elif abs(y + h - sh) < SNAP_DIST:
            ny = sh - h
        if nx != x or ny != y:
            self.w.geometry(f'+{nx}+{ny}')

    def _zoom(self, e):
        d = 0.06 if e.delta > 0 else -0.06
        self.scale = max(0.3, min(2.0, self.scale + d))
        self._rsz()
        sw = self.w.winfo_screenwidth()
        self.w.geometry(f'+{sw - self._w - 12}+{self.w.winfo_y()}')


# ──────────────────────────────────────────────────────────
#  Entry point — single-instance guard
# ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    m = win32event.CreateMutex(None, False, 'Global\\GPUTraffic6')
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        sys.exit(0)
    App().root.mainloop()
