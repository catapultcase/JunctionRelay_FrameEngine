# E-Paper Frame Display - Simplified Pi Implementation

Lightweight display daemon for Raspberry Pi that receives pre-rendered PNG frames and shows them on Waveshare e-paper displays.

---

## ✅ Features

- 🖼️ Accepts full PNG frames via HTTP POST
- 📐 Supports multiple display models:
  - 5.79" (792x272) 4-color
  - 7.3" (800x480) 6-color Spectra
- 🖥️ Auto-select resolution based on model
- 🎨 Handles color quantization for 6-color displays
- 🧪 Simulation mode if no hardware is present
- 🌐 REST endpoints for status and testing
- ⚙️ Minimal dependencies, fast startup

---

## 🖥️ Supported Displays

| Model     | Argument     | Resolution | Colors                        |
|-----------|--------------|------------|-------------------------------|
| 5.79"     | `5in79g`     | 792×272    | Black, White, Red, Yellow     |
| 7.3" (E)  | `7in3sce`    | 800×480    | Black, White, Red, Yellow, Green, Blue |

---

## 🧑‍💻 Installation

### 1. Clone and Setup
```bash
git clone https://github.com/catapultcase/JunctionRelay_FrameEngine
cd JunctionRelay_FrameEngine
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Waveshare Library (on Pi)
```bash
git clone https://github.com/waveshare/e-Paper.git
cp -r e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd ./waveshare_epd
```

---

## 🚀 Running

### Run for 5.79" Display (default)
```bash
sudo python3 main.py
```

### Run for 7.3" Spectra Display
```bash
sudo python3 main.py --model 7in3sce
```

---

## 🔌 API Endpoints

| Method | Path                  | Description                  |
|--------|-----------------------|------------------------------|
| POST   | `/api/display/frame`  | Send PNG frame               |
| GET    | `/api/status`         | Get service and display info |
| GET    | `/api/display/info`   | Static display metadata      |
| GET    | `/api/test`           | Health check                 |

---

## 🧪 Test Frame Upload

```bash
curl -X POST http://<pi-ip>/api/display/frame \
  -H "Content-Type: application/octet-stream" \
  --data-binary @frame.png
```

---

## 🧪 Simulation Mode

If e-paper hardware is not detected:
- Frames are saved to `/tmp/epaper_frame_TIMESTAMP.png`
- All HTTP APIs continue working

Great for local development without hardware.

---

## 🧱 Architecture

```
Backend (.NET, etc)
    ↓
Render PNG Frame
    ↓
HTTP POST to Pi
    ↓
Pi Displays via SPI
```

---

## 📁 File Overview

| File               | Description                          |
|--------------------|--------------------------------------|
| `main.py`          | App entry point, handles CLI and startup |
| `display_service.py` | Handles hardware control and image rendering |
| `http_server.py`   | Flask-based HTTP API for receiving frames |
| `requirements.txt` | Python dependencies                  |

---

## 🛠️ Next Steps

- Add support for additional Waveshare models
- Enable basic image caching
- Add systemd service for auto-start

---

Made with ❤️ for the JunctionRelay project.
