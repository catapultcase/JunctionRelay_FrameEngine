#!/usr/bin/env python3
"""
E-Paper Frame Display - Simplified Pi Implementation
Receives pre-rendered frames from backend and displays them
"""

import sys
import signal
import threading
from http_server import FrameHTTPServer
from display_service import DisplayService

class FrameDisplayApp:
    def __init__(self):
        self.display = DisplayService()
        self.http_server = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def start(self):
        """Start the frame display service"""
        print("=" * 50)
        print("E-Paper Frame Display v2.0")
        print("Simplified Pi Implementation")
        print("=" * 50)
        
        # Initialize display
        if not self.display.initialize():
            print("[ERROR] Failed to initialize e-paper display")
            return False
            
        # Show startup screen
        self.display.show_startup_screen()
        
        # Start HTTP server
        self.http_server = FrameHTTPServer(self.display)
        server_thread = threading.Thread(target=self.http_server.start, daemon=True)
        server_thread.start()
        
        self.running = True
        
        print("🚀 Frame Display Service Started")
        print("📡 HTTP server running on port 80")
        print("📋 Endpoints:")
        print("   POST /api/data - Main data ingestion (Junction Relay protocol)")
        print("   POST /api/display/frame - Direct frame display (legacy)")
        print("   GET  /api/status - Service status")
        print("   GET  /api/display/info - Display information")
        print("   GET  /api/test - Test endpoint")
        print("")
        print("🖼️  Frame Mode: Ready to receive prefixed frame data")
        print("📡 Compatible with Junction Relay frame streaming")
        print("Press Ctrl+C to stop")
        
        # Main loop
        try:
            while self.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
        self.shutdown()
        return True
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[SHUTDOWN] Received signal {signum}")
        self.running = False
        
    def shutdown(self):
        """Graceful shutdown"""
        print("[SHUTDOWN] Stopping services...")
        
        if self.http_server:
            self.http_server.stop()
            
        if self.display:
            self.display.shutdown()
            
        print("✅ Shutdown complete")

def main():
    app = FrameDisplayApp()
    success = app.start()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())