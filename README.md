# E-Paper Frame Display - Junction Relay Frame Mode

Simplified Pi implementation that receives pre-rendered PNG frames from Junction Relay backend and displays them on e-paper. Supports multiple Waveshare e-paper models with automatic hardware detection and Junction Relay protocol streaming.

## Supported E-Paper Models

| Model | Resolution | Description | Module |
|-------|------------|-------------|---------|
| **5.79g** | 792×272 | 5.79" 4-color E-Paper HAT (G) | `epd5in79g` |
| **7.3e** | 800×480 | 7.3" E-Paper HAT (E) | `epd7in3e` |
| **4.0e** | 640×400 | 4" E-Paper HAT Plus (E) | `epd4in01e` |

## Features
- ✅ **Multi-Model Support**: Works with 3 different Waveshare e-paper displays
- ✅ **Junction Relay Protocol**: Full support for prefixed frame data (LLLLTTRR format)
- ✅ **Multiple Data Types**: Handles JSON (Type 00), Gzip (Type 01), and Frame (Type 02) payloads
- ✅ **Automatic Hardware Detection**: Simulation mode if no e-paper hardware
- ✅ **Command Line Configuration**: Specify display model via arguments
- ✅ **Status Monitoring**: Comprehensive endpoint monitoring with model information

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

### 4. Run with Display Model
```bash
# Default 5.79" 4-color display
sudo python3 main.py

# 7.3" E-Paper HAT
sudo python3 main.py --model 7.3e

# 4" E-Paper HAT Plus
sudo python3 main.py -m 4.0e

# List all supported models
python3 main.py --list-models
```

## Command Line Options

```bash
python3 main.py [OPTIONS]

Options:
  -m, --model MODEL     E-paper display model (default: 5.79g)
  --list-models         List supported display models and exit
  -h, --help            Show help message

Examples:
  python3 main.py                    # Use default 5.79g display
  python3 main.py --model 7.3e       # Use 7.3" E-Paper HAT
  python3 main.py -m 4.0e            # Use 4" E-Paper HAT Plus
  python3 main.py --list-models      # Show supported models
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

### Status Check
```bash
GET /api/status

Response includes:
- Display model and description
- Hardware availability
- Frame statistics
- Uptime information
```

### Display Info
```bash
GET /api/display/info

Response includes:
- Model-specific resolution
- Supported capabilities
- Hardware status
```

### Supported Models
```bash
GET /api/display/models

Returns:
- List of all supported models
- Current active model
- Model descriptions
```

### Test
```bash
GET /api/test

Simple connectivity test with model info
```

## Protocol Support

### Junction Relay Stream Data Types
The Pi supports all Junction Relay protocol data types:

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
# Backend automatically detects display resolution via /api/display/info
```

### Direct Frame Testing
```bash
# Test with 7.3" display (800x480)
curl -X POST http://pi-ip-address/api/display/frame \
  -H "Content-Type: application/octet-stream" \
  --data-binary @frame_800x480.png

# Test with 4" display (640x400)  
curl -X POST http://pi-ip-address/api/display/frame \
  -H "Content-Type: application/octet-stream" \
  --data-binary @frame_640x400.png
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

### Model Detection
```bash
# Check what model is running
curl http://pi-ip-address/api/display/info

# List all supported models
curl http://pi-ip-address/api/display/models
```

## Simulation Mode

If no e-paper hardware is detected, the service runs in simulation mode:
- Frames are saved to `/tmp/epaper_frame_{model}_{timestamp}.png`
- All endpoints work normally with model-specific filenames
- Perfect for development/testing without hardware

## Architecture

### Frame Mode Flow
```
Junction Relay Backend (.NET)
    ↓ RenderingMode = "FrameEngine"
    ↓ Auto-detects Pi resolution via /api/display/info
FrameEngine Service
    ↓ Renders PNG frame (SkiaSharp) at correct resolution
Stream Manager (HTTP/COM)
    ↓ Adds LLLLTTRR prefix + PNG bytes
Pi HTTP Server (/api/data)
    ↓ Parses prefix, extracts PNG
E-Paper Display Service
    ↓ Model-specific display handling
Waveshare E-Paper Hardware
```

### Legacy Flow
```
Backend → Raw PNG (model resolution) → POST /api/display/frame → E-Paper Display
```

## Display Model Configuration

The system automatically configures itself based on the specified model:

### 5.79" 4-color E-Paper HAT (G) - Default
- **Resolution**: 792×272
- **Colors**: Black, White, Red, Yellow
- **Module**: `waveshare_epd.epd5in79g`

### 7.3" E-Paper HAT (E)
- **Resolution**: 800×480  
- **Colors**: Black, White, Red, Yellow
- **Module**: `waveshare_epd.epd7in3e`

### 4" E-Paper HAT Plus (E)
- **Resolution**: 640×400
- **Colors**: Black, White, Red, Yellow  
- **Module**: `waveshare_epd.epd4in01e`

## Backend Integration

### Automatic Resolution Detection
When using Junction Relay Frame Mode, the backend automatically detects the Pi's display resolution:

1. Backend queries `GET /api/display/info`
2. Receives model-specific width/height
3. Renders frames at correct resolution
4. Streams via Junction Relay protocol

### Manual Configuration
For direct integration, ensure your backend renders frames at the correct resolution for your display model.

## Files

- `main.py` - Application entry point with model selection and argument parsing
- `http_server.py` - Flask HTTP server with Junction Relay protocol and model info
- `display_service.py` - Multi-model e-paper display operations with dynamic imports
- `requirements.txt` - Python dependencies

## Frame Mode vs Payload Mode

| Mode | Backend Rendering | Pi Processing | Data Size | Latency | Model Support |
|------|------------------|---------------|-----------|---------|---------------|
| **Frame Mode** | ✅ Full rendering | ❌ Display only | ~7KB PNG | Low | ✅ All models |
| **Payload Mode** | ❌ JSON only | ✅ Full rendering | ~1KB JSON | High | ⚠️ Model-specific |

## Supported Configurations

### Junction Types
- ✅ **HTTP Junction** (direct device communication)
- ✅ **Gateway Junction (HTTP to ESP:NOW)** (via gateway device)
- ✅ **COM Junction** (serial communication)
- ✅ **Gateway Junction (COM to ESP:NOW)** (via COM gateway)

### Frame Layouts (All Models)
- ✅ **FRAME_SENSOR_GRID** - Tabular sensor display
- ✅ **FRAME_DASHBOARD** - Widget-based layout
- ✅ **FRAME_CALENDAR** - TV Guide style calendar
- ✅ **FRAME_CHART** - Data visualization
- ✅ **FRAME_QUAD** - Four-quadrant layout
- ✅ **FRAME_IMAGE** - Image overlay display

**Benefits of Multi-Model Frame Mode:**
- 🚀 **Performance**: No Pi-side rendering overhead on any model
- 🎨 **Consistency**: Server-side rendering ensures identical output across models
- 🔧 **Simplicity**: Pi becomes pure display device regardless of hardware
- 📊 **Rich Layouts**: Complex visualizations possible with SkiaSharp on all models
- 🌐 **Scalability**: Backend handles all rendering complexity and resolution management
- 📱 **Flexibility**: Single codebase supports multiple e-paper form factors

## Troubleshooting

### Model Detection Issues
```bash
# Check if model is recognized
python3 main.py --list-models

# Test with explicit model
python3 main.py --model 7.3e
```

### Hardware Issues
```bash
# Check hardware detection in logs
sudo python3 main.py --model 7.3e

# Look for simulation mode messages
tail -f /var/log/syslog | grep DISPLAY
```

### Resolution Mismatches
```bash
# Verify backend is getting correct resolution
curl http://pi-ip-address/api/display/info

# Check frame dimensions in logs
sudo python3 main.py --model 7.3e  # Watch for resize warnings
```