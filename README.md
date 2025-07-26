# E-Paper Frame Display - Junction Relay Frame Mode

Simplified Pi implementation that receives pre-rendered PNG frames from Junction Relay backend and displays them on e-paper. Supports both direct frame display and Junction Relay protocol streaming.

## Features
- ✅ **Junction Relay Protocol**: Full support for prefixed frame data (LLLLTTRR format)
- ✅ **Multiple Data Types**: Handles JSON (Type 00), Gzip (Type 01), and Frame (Type 02) payloads
- ✅ **Automatic Hardware Detection**: Simulation mode if no e-paper hardware
- ✅ **Status Monitoring**: Comprehensive endpoint monitoring

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

### Main Data Ingestion (Junction Relay Protocol)
```bash
POST /api/data
Content-Type: application/octet-stream
Body: Prefixed frame data (LLLLTTRR + PNG bytes)

Example prefix: 74820200
- 7482 = Frame size in bytes
- 02 = Frame data type 
- 00 = Routing field
```

### Direct Frame Display (Legacy)
```bash
POST /api/display/frame
Content-Type: application/octet-stream
Body: Raw PNG image data (792x272)
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

## Protocol Support

### Junction Relay Stream Data Types
The Pi now supports all Junction Relay protocol data types:

- **Type 00**: JSON payloads (for compatibility)
- **Type 01**: Gzip compressed JSON (for compatibility)  
- **Type 02**: Frame data (PNG images for display)

### LLLLTTRR Prefix Format
```
LLLLTTRR = 8-digit ASCII prefix
├── LLLL = 4-digit length hint
├── TT = 2-digit type field (00=JSON, 01=Gzip, 02=Frame)
└── RR = 2-digit routing field
```

## Testing

### From Junction Relay Backend (.NET)
```bash
# Frame mode streaming works automatically when junction 
# RenderingMode is set to "FrameEngine"
```

### Direct Frame Testing
```bash
curl -X POST http://pi-ip-address/api/display/frame \
  -H "Content-Type: application/octet-stream" \
  --data-binary @frame.png
```

### Protocol Testing
```bash
# Test with prefixed frame data
echo -n "74820200" > /tmp/test_frame.bin
cat frame.png >> /tmp/test_frame.bin
curl -X POST http://pi-ip-address/api/data \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/tmp/test_frame.bin
```

## Simulation Mode

If no e-paper hardware is detected, the service runs in simulation mode:
- Frames are saved to `/tmp/epaper_frame_*.png`
- All endpoints work normally
- Perfect for development/testing without hardware

## Architecture

### Frame Mode Flow
```
Junction Relay Backend (.NET)
    ↓ RenderingMode = "FrameEngine"
FrameEngine Service
    ↓ Renders PNG frame (SkiaSharp)
Stream Manager (HTTP/COM)
    ↓ Adds LLLLTTRR prefix + PNG bytes
Pi HTTP Server (/api/data)
    ↓ Parses prefix, extracts PNG
E-Paper Display Service
    ↓ Displays frame
Waveshare E-Paper Hardware
```

### Legacy Flow
```
Backend → Raw PNG → POST /api/display/frame → E-Paper Display
```

## Files

- `main.py` - Application entry point with enhanced logging
- `http_server.py` - Flask HTTP server with Junction Relay protocol support
- `display_service.py` - E-paper display operations
- `requirements.txt` - Python dependencies

## Frame Mode vs Payload Mode

| Mode | Backend Rendering | Pi Processing | Data Size | Latency |
|------|------------------|---------------|-----------|---------|
| **Frame Mode** | ✅ Full rendering | ❌ Display only | ~7KB PNG | Low |
| **Payload Mode** | ❌ JSON only | ✅ Full rendering | ~1KB JSON | High |

## Supported Configurations

### Junction Types
- ✅ **HTTP Junction** (direct device communication)
- ✅ **Gateway Junction (HTTP to ESP:NOW)** (via gateway device)
- ✅ **COM Junction** (serial communication)
- ✅ **Gateway Junction (COM to ESP:NOW)** (via COM gateway)

### Frame Layouts
- ✅ **FRAME_SENSOR_GRID** - Tabular sensor display
- ✅ **FRAME_DASHBOARD** - Widget-based layout
- ✅ **FRAME_CALENDAR** - TV Guide style calendar
- ✅ **FRAME_CHART** - Data visualization
- ✅ **FRAME_QUAD** - Four-quadrant layout
- ✅ **FRAME_IMAGE** - Image overlay display

**Benefits of Frame Mode:**
- 🚀 **Performance**: No Pi-side rendering overhead
- 🎨 **Consistency**: Server-side rendering ensures identical output
- 🔧 **Simplicity**: Pi becomes pure display device
- 📊 **Rich Layouts**: Complex visualizations possible with SkiaSharp
- 🌐 **Scalability**: Backend handles all rendering complexity