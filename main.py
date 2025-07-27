#!/usr/bin/env python3
"""
E-Paper Frame Display - Simplified Pi Implementation
Receives pre-rendered frames from backend and displays them
"""

import sys
import signal
import threading
import argparse
from http_server import FrameHTTPServer
from display_service import DisplayService

class FrameDisplayApp:
    def __init__(self, display_model="5.79g"):
        self.display = DisplayService(display_model)
        self.http_server = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def start(self):
        """Start the frame display service"""
        print("=" * 60)
        print("E-Paper Frame Display v2.0")
        print("Simplified Pi Implementation")
        print("=" * 60)
        
        # Show display model info
        stats = self.display.get_display_stats()
        print(f"📱 Display Model: {stats['model']} - {stats['description']}")
        print(f"📏 Resolution: {stats['width']}x{stats['height']}")
        print(f"🔧 Hardware: {'Available' if stats['hardware_available'] else 'Simulation Mode'}")
        print("")
        
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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='E-Paper Frame Display Service',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Supported Display Models:
  5.79g    5.79" 4-color E-Paper HAT (G) - 792x272 (default)
  7.3e     7.3" E-Paper HAT (E) - 800x480  
  4.0e     4" E-Paper HAT Plus (E) - 640x400

Examples:
  python3 main.py                    # Use default 5.79g display
  python3 main.py --model 7.3e       # Use 7.3" E-Paper HAT
  python3 main.py -m 4.0e            # Use 4" E-Paper HAT Plus
  python3 main.py --list-models      # Show supported models
        '''
    )
    
    parser.add_argument(
        '-m', '--model',
        default='5.79g',
        help='E-paper display model (default: 5.79g)'
    )
    
    parser.add_argument(
        '--list-models',
        action='store_true',
        help='List supported display models and exit'
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Handle --list-models
    if args.list_models:
        print("Supported E-Paper Display Models:")
        print("=" * 40)
        supported = DisplayService.get_supported_models()
        for model, description in supported.items():
            print(f"  {model:<8} {description}")
        print("")
        print("Usage: python3 main.py --model <model>")
        return 0
    
    # Validate model
    supported_models = DisplayService.get_supported_models()
    if args.model not in supported_models:
        print(f"Error: Unknown display model '{args.model}'")
        print(f"Supported models: {', '.join(supported_models.keys())}")
        print("Use --list-models to see full descriptions")
        return 1
    
    # Start the application
    app = FrameDisplayApp(args.model)
    success = app.start()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())