"""
HTTP Server - Receives frame data and routes to display
Ultra-simplified compared to previous implementation
"""

from flask import Flask, request, jsonify
import time
import uuid
import os

class FrameHTTPServer:
    def __init__(self, display_service):
        self.display = display_service
        self.app = Flask(__name__)
        self.running = False
        self.frame_count = 0
        self.last_frame_time = None
        
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup HTTP endpoints"""
        
        @self.app.route('/api/display/frame', methods=['POST'])
        def display_frame():
            """Main endpoint - receives PNG frame and displays it"""
            try:
                # Get raw binary data (PNG)
                frame_data = request.get_data()
                
                if not frame_data:
                    return jsonify({"error": "No frame data received"}), 400
                
                if len(frame_data) < 100:  # Basic sanity check
                    return jsonify({"error": "Frame data too small"}), 400
                    
                # Display the frame
                success = self.display.display_frame(frame_data)
                
                if success:
                    self.frame_count += 1
                    self.last_frame_time = time.time()
                    
                    return jsonify({
                        "status": "success",
                        "frame_size": len(frame_data),
                        "frame_count": self.frame_count,
                        "timestamp": self.last_frame_time
                    }), 200
                else:
                    return jsonify({"error": "Failed to display frame"}), 500
                    
            except Exception as e:
                print(f"[HTTP] ERROR in /api/display/frame: {e}")
                return jsonify({"error": str(e)}), 500
                
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Service status endpoint"""
            uptime = time.time() - self.display.start_time if self.display.start_time else 0
            
            return jsonify({
                "status": "running",
                "service": "epaper_frame_display",
                "uptime_seconds": int(uptime),
                "frames_displayed": self.frame_count,
                "last_frame": self.last_frame_time,
                "display_initialized": self.display.initialized,
                "mac_address": self._get_mac_address()
            })
            
        @self.app.route('/api/display/info', methods=['GET'])
        def get_display_info():
            """Display capabilities endpoint"""
            return jsonify({
                "display_type": "epaper_frame_display",
                "width": 792,
                "height": 272,
                "colors": ["black", "white", "red", "yellow"],
                "capabilities": [
                    "frame_display",
                    "png_support",
                    "color_epaper"
                ],
                "version": "2.0",
                "mac_address": self._get_mac_address()
            })
            
        @self.app.route('/api/test', methods=['GET'])
        def test_endpoint():
            """Simple test endpoint"""
            return jsonify({
                "message": "Frame display service is running",
                "timestamp": time.time(),
                "service": "epaper_frame_display"
            })
            
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Endpoint not found"}), 404
            
        @self.app.errorhandler(500)  
        def internal_error(error):
            return jsonify({"error": "Internal server error"}), 500
            
    def _get_mac_address(self):
        """Get MAC address"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                           for ele in range(0,8*6,8)][::-1])
            return mac
        except:
            return "00:00:00:00:00:00"
            
    def start(self, host="0.0.0.0", port=80):
        """Start the HTTP server"""
        if self.running:
            return
            
        self.running = True
        print(f"[HTTP] Starting server on {host}:{port}")
        
        try:
            self.app.run(host=host, port=port, debug=False, threaded=True)
        except Exception as e:
            print(f"[HTTP] Server error: {e}")
        finally:
            self.running = False
            
    def stop(self):
        """Stop the HTTP server"""
        self.running = False
        print("[HTTP] Server stopped")