# GPU 红绿灯

> 拟物化桌面 GPU 监控小工具 — 你的显卡值得一盏真正的红绿灯。

![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

一款无边框、始终置顶的桌面小组件，通过 Windows 性能计数器读取 GPU 3D 引擎利用率，渲染一盏逼真的红绿灯：

- **绿灯** — 空闲 / 低负载（＜30 %）
- **黄灯** — 中等负载（30–60 %）
- **红灯** — 高负载（＞60 %）

当前亮起的灯会闪烁提示。右键隐藏到系统托盘，滚轮缩放，拖拽自动吸附屏幕边缘。

## 特性

- **照片级渲染** — 径向渐变、菲涅尔透镜纹理、镜面高光、金属倒角外壳、铆钉、遮光罩、灯井凹陷，全部由 PIL 程序化生成，内部 3 倍分辨率
- **灯效闪烁** — 亮 600 ms / 灭 300 ms
- **系统托盘** — 关闭即隐藏至托盘，双击恢复，右键菜单彻底退出
- **边缘吸附** — 拖拽松手时，距屏幕边缘 20 px 内自动吸附
- **滚轮缩放** — 0.3× 到 2.0×
- **单实例保护** — Windows Mutex 防止重复运行
- **轻量** — GPU 轮询间隔约 2 秒，CPU 占用可忽略

## 环境要求

- Windows 10 或 11
- Python 3.8 及以上

### Python 依赖

```bash
pip install -r requirements.txt
```

| 包名     | 用途             |
|----------|------------------|
| Pillow   | 图像生成         |
| pywin32  | 互斥锁与系统 API |
| pystray  | 系统托盘         |

## 安装

```bash
git clone https://github.com/448194025-byte/gpu-traffic-light.git
cd gpu-traffic-light
pip install -r requirements.txt
python gpu_traffic_light.py
```

## 使用

| 操作       | 方式                     |
|------------|--------------------------|
| 移动位置   | 在小组件上按住左键拖动   |
| 缩放大小   | 鼠标滚轮                 |
| 隐藏到托盘 | 右键点击小组件           |
| 从托盘恢复 | 双击托盘图标             |
| 彻底退出   | 托盘图标右键 → 退出      |

小组件启动后默认位于主显示器右上角。

## 工作原理

`gpu_traffic_light.py` 调用 Windows `typeperf` 查询计数器：

```
\GPU Engine(*)\Utilization Percentage
```

筛选 `engtype_3D` 条目，取最大值作为当前 GPU 负载。图像由 `PIL.ImageDraw` 渲染，缓存四种状态（全灭 / 红 / 黄 / 绿），在透明 `tkinter` 画布上绘制。

## 项目结构

```
gpu-traffic-light/
├── gpu_traffic_light.py   # 主程序
├── README.md              # 英文说明
├── README_CN.md           # 中文说明
├── requirements.txt
├── LICENSE
└── .gitignore
```

## 许可证

MIT — 详见 [LICENSE](LICENSE)。
