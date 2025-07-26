#!/usr/bin/env python3
"""
E-Paper Frame Display - Simplified Pi Implementation
Supports multiple Waveshare display models via --model argument
"""

import sys
import signal
import threading
import argparse
import os
from http_server import FrameHTTPServer
from display_service import DisplayService

class FrameDisplayApp:
    def __init__(self, model: str):
        self.display = DisplayService(display_model=model)
        self.http_server = None
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def start(self):
        """Start the frame display service"""
        print("=" * 50)
        print("E-Paper Frame Display v2.0")
        print("Multi-model Support")
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
        print("   POST /api/display/frame - Display frame")
        print("   GET  /api/status - Service status")
        print("   GET  /api/display/info - Display information")
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
    parser = argparse.ArgumentParser(description="E-Paper Frame Display")
    parser.add_argument("--model", default="5in79g", help="Display model (e.g. 5in79g, 7in3sce)")
    args = parser.parse_args()

    app = FrameDisplayApp(model=args.model)
    success = app.start()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
