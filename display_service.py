"""
Display Service - Handles e-paper display operations with multi-model support
Simplified to just display pre-rendered PNG frames
"""

import time
import io
from PIL import Image
import tempfile
import os
import importlib

# Display model configurations
DISPLAY_MODELS = {
    "5.79g": {
        "module": "waveshare_epd.epd5in79g",
        "width": 792,
        "height": 272,
        "description": "5.79\" 4-color E-Paper HAT (G)"
    },
    "7.3e": {
        "module": "waveshare_epd.epd7in3e",
        "width": 800,
        "height": 480,
        "description": "7.3\" E-Paper HAT (E)"
    },
    "7.3f": {
        "module": "waveshare_epd.epd7in3f", 
        "width": 800,
        "height": 480,
        "description": "7.3\" E-Paper HAT (F)"
    },
    "7.3g": {
        "module": "waveshare_epd.epd7in3g",
        "width": 800,
        "height": 480, 
        "description": "7.3\" E-Paper HAT (G)"
    },
    "4.0e": {
        "module": "waveshare_epd.epd4in01e",
        "width": 640, 
        "height": 400,
        "description": "4\" E-Paper HAT Plus (E)"
    }
}

class DisplayService:
    def __init__(self, model="5.79g"):
        self.model = model
        self.epd = None
        self.epd_module = None
        self.width = 792
        self.height = 272
        self.initialized = False
        self.start_time = None
        self.hardware_available = False
        
        # Set display specs based on model
        if model in DISPLAY_MODELS:
            self.width = DISPLAY_MODELS[model]["width"]
            self.height = DISPLAY_MODELS[model]["height"]
            self.description = DISPLAY_MODELS[model]["description"]
        else:
            print(f"[DISPLAY] Warning: Unknown model '{model}', using default 5.79g")
            self.model = "5.79g"
            self.description = DISPLAY_MODELS["5.79g"]["description"]
        
        # Try to import the appropriate e-paper library
        try:
            module_name = DISPLAY_MODELS[self.model]["module"]
            self.epd_module = importlib.import_module(module_name)
            self.hardware_available = True
            print(f"[DISPLAY] {self.description} library imported successfully")
        except ImportError as e:
            self.hardware_available = False
            print(f"[DISPLAY] Warning: {self.description} library not available: {e}")
            print("[DISPLAY] Running in simulation mode")
        
    def initialize(self):
        """Initialize the e-paper display"""
        try:
            self.start_time = time.time()
            
            if self.hardware_available:
                print(f"[DISPLAY] Initializing {self.description}...")
                print(f"[DISPLAY] Step 1: Creating EPD object...")
                self.epd = self.epd_module.EPD()
                print(f"[DISPLAY] Step 2: Starting hardware initialization...")
                
                # Add timeout for hardware initialization
                import signal
                def timeout_handler(signum, frame):
                    raise TimeoutError(f'{self.description} initialization timed out after 30 seconds')
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)  # 30 second timeout
                
                try:
                    self.epd.init()
                    signal.alarm(0)  # Cancel timeout
                    print(f"[DISPLAY] Step 3: Hardware initialization successful")
                except TimeoutError as e:
                    signal.alarm(0)
                    print(f"[DISPLAY] ❌ {e}")
                    print(f"[DISPLAY] This usually indicates hardware connection issues")
                    print(f"[DISPLAY] Check ribbon cable and GPIO connections")
                    return False
                
                # Some displays may have different width/height properties
                if hasattr(self.epd, 'width') and hasattr(self.epd, 'height'):
                    self.width, self.height = self.epd.width, self.epd.height
                    
                print(f"[DISPLAY] ✅ E-paper display initialized: {self.width}x{self.height}")
            else:
                print(f"[DISPLAY] ⚠️ Running in simulation mode (no {self.description} hardware)")
                
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"[DISPLAY] ❌ Failed to initialize display: {e}")
            print(f"[DISPLAY] Hardware troubleshooting:")
            print(f"[DISPLAY] 1. Check ribbon cable connection")
            print(f"[DISPLAY] 2. Verify HAT is properly seated on GPIO pins")
            print(f"[DISPLAY] 3. Ensure SPI is enabled: ls /dev/spi*")
            print(f"[DISPLAY] 4. Try different display module variant")
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
            
            if self.hardware_available and self.epd:
                # Send to real e-paper display
                print(f"[DISPLAY] 📺 Displaying frame on {self.description} ({len(frame_data)} bytes)")
                self.epd.display(self.epd.getbuffer(image))
            else:
                # Simulation mode - save to file for testing
                timestamp = int(time.time())
                filename = f"/tmp/epaper_frame_{self.model}_{timestamp}.png"
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
            if self.hardware_available and self.epd:
                self.epd.Clear()
                print(f"[DISPLAY] 🧹 {self.description} cleared")
            else:
                print(f"[DISPLAY] 🧹 Simulation: {self.description} would be cleared")
        except Exception as e:
            print(f"[DISPLAY] ❌ Error clearing display: {e}")
            
    def shutdown(self):
        """Shutdown the display service"""
        try:
            if self.hardware_available and self.epd:
                print(f"[DISPLAY] 💤 Putting {self.description} to sleep...")
                self.epd.sleep()
                
            print("[DISPLAY] ✅ Display service shutdown complete")
            
        except Exception as e:
            print(f"[DISPLAY] ❌ Error during shutdown: {e}")
            
    def get_display_stats(self):
        """Get display statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "initialized": self.initialized,
            "hardware_available": self.hardware_available,
            "model": self.model,
            "description": self.description,
            "width": self.width,
            "height": self.height,
            "uptime_seconds": int(uptime)
        }
        
    @staticmethod
    def get_supported_models():
        """Get list of supported display models"""
        return {model: config["description"] for model, config in DISPLAY_MODELS.items()}