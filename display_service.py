"""
Display Service - Handles e-paper display operations
Simplified to just display pre-rendered PNG frames
"""

import time
import io
from PIL import Image
import tempfile
import os

# Try to import the Waveshare e-paper library
try:
    import waveshare_epd.epd5in79g as epd5in79g
    EPAPER_AVAILABLE = True
    print("[DISPLAY] Waveshare e-paper library imported successfully")
except ImportError as e:
    EPAPER_AVAILABLE = False
    print(f"[DISPLAY] Warning: Waveshare e-paper library not available: {e}")
    print("[DISPLAY] Running in simulation mode")

class DisplayService:
    def __init__(self):
        self.epd = None
        self.width = 792
        self.height = 272
        self.initialized = False
        self.start_time = None
        
    def initialize(self):
        """Initialize the e-paper display"""
        try:
            self.start_time = time.time()
            
            if EPAPER_AVAILABLE:
                print("[DISPLAY] Initializing Waveshare 5.79\" e-paper display...")
                self.epd = epd5in79g.EPD()
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
        """Display a PNG frame on the e-paper"""
        try:
            # Load PNG data into PIL Image
            image = Image.open(io.BytesIO(frame_data))
            
            # Verify image dimensions
            if image.size != (self.width, self.height):
                print(f"[DISPLAY] ⚠️ Resizing frame from {image.size} to {self.width}x{self.height}")
                image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            if EPAPER_AVAILABLE and self.epd:
                # Send to real e-paper display
                print(f"[DISPLAY] 📺 Displaying frame on e-paper ({len(frame_data)} bytes)")
                self.epd.display(self.epd.getbuffer(image))
            else:
                # Simulation mode - save to file for testing
                timestamp = int(time.time())
                filename = f"/tmp/epaper_frame_{timestamp}.png"
                image.save(filename)
                print(f"[DISPLAY] 💾 Simulation: Frame saved to {filename}")
            
            return True
            
        except Exception as e:
            print(f"[DISPLAY] ❌ Error displaying frame: {e}")
            return False
            
    def show_startup_screen(self):
        """Show a simple startup screen"""
        try:
            # Create a simple startup image
            startup_image = Image.new('RGB', (self.width, self.height), color='white')
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            startup_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Display startup screen
            success = self.display_frame(img_byte_arr)
            if success:
                print("[DISPLAY] ✅ Startup screen displayed")
            else:
                print("[DISPLAY] ⚠️ Failed to display startup screen")
                
        except Exception as e:
            print(f"[DISPLAY] ❌ Error showing startup screen: {e}")
            
    def clear_display(self):
        """Clear the display to white"""
        try:
            if EPAPER_AVAILABLE and self.epd:
                self.epd.Clear()
                print("[DISPLAY] 🧹 Display cleared")
            else:
                print("[DISPLAY] 🧹 Simulation: Display would be cleared")
        except Exception as e:
            print(f"[DISPLAY] ❌ Error clearing display: {e}")
            
    def shutdown(self):
        """Shutdown the display service"""
        try:
            if EPAPER_AVAILABLE and self.epd:
                print("[DISPLAY] 💤 Putting e-paper display to sleep...")
                self.epd.sleep()
                
            print("[DISPLAY] ✅ Display service shutdown complete")
            
        except Exception as e:
            print(f"[DISPLAY] ❌ Error during shutdown: {e}")
            
    def get_display_stats(self):
        """Get display statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "initialized": self.initialized,
            "hardware_available": EPAPER_AVAILABLE,
            "width": self.width,
            "height": self.height,
            "uptime_seconds": int(uptime)
        }