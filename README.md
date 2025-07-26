# E-Paper Frame Display - Simplified Pi Implementation

Ultra-simplified Pi code that receives pre-rendered PNG frames from backend and displays them on e-paper.

## Features
- ✅ Single HTTP endpoint for frame display
- ✅ Automatic hardware detection (simulation mode if no e-paper)
- ✅ Minimal dependencies 
- ✅ Graceful error handling
- ✅ Status monitoring endpoints

## Installation

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

### 3. Install Waveshare Library (Pi only)
```bash
git clone https://github.com/waveshare/e-Paper.git
cp -r e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd ./
```

### 4. Run
```bash
sudo python3 main.py
```

## API Endpoints

### Display Frame
```bash
POST /api/display/frame
Content-Type: application/octet-stream
Body: PNG image data (792x272)
```

### Status Check
```bash
GET /api/status
```

### Display Info
```bash
GET /api/display/info
```

### Test
```bash
GET /api/test
```

## Testing from Backend

```bash
# Test from your .NET backend
curl -X POST http://pi-ip-address/api/display/frame \
  -H "Content-Type: application/octet-stream" \
  --data-binary @frame.png
```

## Simulation Mode

If no e-paper hardware is detected, the service runs in simulation mode:
- Frames are saved to `/tmp/epaper_frame_*.png`
- All endpoints work normally
- Perfect for development/testing

## Architecture

```
Backend (.NET) → Generate PNG Frame → HTTP POST → Pi → E-Paper Display
```

**That's it!** No complex protocols, no rendering logic, just pure display functionality.

## Files

- `main.py` - Application entry point
- `http_server.py` - Flask HTTP server with endpoints  
- `display_service.py` - E-paper display operations
- `requirements.txt` - Python dependencies

## Previous vs New

**Before:** 1000+ lines, complex protocol parsing, on-device rendering  
**After:** ~200 lines, single HTTP endpoint, pure display

Much simpler, much more reliable! 🚀