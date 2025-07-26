"""
Display Service - Handles e-paper display operations
Supports multiple Waveshare models with color quantization
"""

import time
import io
from PIL import Image
import os

EPAPER_AVAILABLE = False
try:
    from waveshare_epd import epd5in79g, epd7in3sce
    EPAPER_AVAILABLE = True
    print("[DISPLAY] Waveshare e-paper libraries imported successfully")
except ImportError as e:
    print(f"[DISPLAY] Warning: E-paper libraries not available: {e}")
    print("[DISPLAY] Running in simulation mode")

SPECTRA_COLORS = [
    (0, 0, 0),        # Black
    (255, 255, 255),  # White
    (255, 0, 0),      # Red
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
]

def quantize_to_spectra(image):
    palette_img = Image.new("P", (1, 1))
    palette = sum(SPECTRA_COLORS, ()) + (0,) * (768 - 6*3)
    palette_img.putpalette(palette)
    return image.convert("RGB").quantize(palette=palette_img)

class DisplayService:
    def __init__(self, display_model="5in79g"):
        self.model = display_model.lower()
        self.epd = None
        self.width = 792
        self.height = 272
        self.initialized = False
        self.start_time = None

    def initialize(self):
        try:
            self.start_time = time.time()

            if EPAPER_AVAILABLE:
                if self.model == "5in79g":
                    print("[DISPLAY] Initializing 5.79\" e-paper...")
                    self.epd = epd5in79g.EPD()
                elif self.model == "7in3sce":
                    print("[DISPLAY] Initializing 7.3\" 6-color e-paper...")
                    self.epd = epd7in3sce.EPD()
                else:
                    raise ValueError(f"Unsupported display model: {self.model}")

                self.epd.init()
                self.width, self.height = self.epd.width, self.epd.height
                print(f"[DISPLAY] ✅ E-paper display initialized: {self.width}x{self.height}")
            else:
                print("[DISPLAY] ⚠️ Running in simulation mode (no e-paper hardware)")

            self.initialized = True
            return True

        except Exception as e:
            print(f"[DISPLAY] ❌ Failed to initialize display: {e}")
            return False

    def display_frame(self, frame_data):
        try:
            image = Image.open(io.BytesIO(frame_data))

            if image.size != (self.width, self.height):
                print(f"[DISPLAY] ⚠️ Resizing frame from {image.size} to {self.width}x{self.height}")
                image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

            if image.mode != 'RGB':
                image = image.convert('RGB')

            if self.model == "7in3sce":
                image = quantize_to_spectra(image)

            if EPAPER_AVAILABLE and self.epd:
                print(f"[DISPLAY] 📺 Displaying frame on e-paper ({len(frame_data)} bytes)")
                self.epd.display(self.epd.getbuffer(image))
            else:
                timestamp = int(time.time())
                filename = f"/tmp/epaper_frame_{timestamp}.png"
                image.save(filename)
                print(f"[DISPLAY] 💾 Simulation: Frame saved to {filename}")

            return True

        except Exception as e:
            print(f"[DISPLAY] ❌ Error displaying frame: {e}")
            return False

    def show_startup_screen(self):
        try:
            startup_image = Image.new('RGB', (self.width, self.height), color='white')
            img_byte_arr = io.BytesIO()
            startup_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            success = self.display_frame(img_byte_arr)
            if success:
                print("[DISPLAY] ✅ Startup screen displayed")
            else:
                print("[DISPLAY] ⚠️ Failed to display startup screen")

        except Exception as e:
            print(f"[DISPLAY] ❌ Error showing startup screen: {e}")

    def clear_display(self):
        try:
            if EPAPER_AVAILABLE and self.epd:
                self.epd.Clear()
                print("[DISPLAY] 🧹 Display cleared")
            else:
                print("[DISPLAY] 🧹 Simulation: Display would be cleared")
        except Exception as e:
            print(f"[DISPLAY] ❌ Error clearing display: {e}")

    def shutdown(self):
        try:
            if EPAPER_AVAILABLE and self.epd:
                print("[DISPLAY] 💤 Putting e-paper display to sleep...")
                self.epd.sleep()

            print("[DISPLAY] ✅ Display service shutdown complete")

        except Exception as e:
            print(f"[DISPLAY] ❌ Error during shutdown: {e}")

    def get_display_stats(self):
        uptime = time.time() - self.start_time if self.start_time else 0
        return {
            "initialized": self.initialized,
            "hardware_available": EPAPER_AVAILABLE,
            "width": self.width,
            "height": self.height,
            "model": self.model,
            "uptime_seconds": int(uptime)
        }
