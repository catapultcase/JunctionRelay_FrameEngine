import threading
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
        
        @self.app.route('/api/data', methods=['POST'])
        def handle_stream_data():
            """Main endpoint - handles Junction Relay stream data with prefixes"""
            try:
                # Get raw binary data
                data = request.get_data()
                
                if not data:
                    return jsonify({"error": "No data received"}), 400
                
                # Process the stream data synchronously
                success = self._process_stream_data(data)
                
                if success:
                    return jsonify({"status": "OK"}), 200
                else:
                    return jsonify({"error": "Failed to process stream data"}), 500
                    
            except Exception as e:
                print(f"[HTTP] ERROR in /api/data: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/display/frame', methods=['POST'])
        def display_frame():
            """Legacy endpoint - receives PNG frame and displays it"""
            try:
                # Get raw binary data (PNG)
                frame_data = request.get_data()
                
                if not frame_data:
                    return jsonify({"error": "No frame data received"}), 400
                
                if len(frame_data) < 100:  # Basic sanity check
                    return jsonify({"error": "Frame data too small"}), 400
                    
                # Dispatch actual rendering to a background thread
                def _render():
                    try:
                        success = self.display.display_frame(frame_data)
                        if success:
                            self.frame_count += 1
                            self.last_frame_time = time.time()
                            print(f"[HTTP] ✅ Frame displayed: {len(frame_data)} bytes")
                        else:
                            print(f"[HTTP] ❌ Failed to display frame")
                    except Exception as e:
                        print(f"[HTTP] ERROR in rendering thread: {e}")

                threading.Thread(target=_render, daemon=True).start()
                
                # Immediately return success on data receipt
                return jsonify({
                    "status": "success",
                    "frame_size": len(frame_data),
                    "frame_count": self.frame_count,
                    "timestamp": self.last_frame_time
                }), 200
                    
            except Exception as e:
                print(f"[HTTP] ERROR in /api/display/frame: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Service status endpoint"""
            uptime = time.time() - self.display.start_time if self.display.start_time else 0
            display_stats = self.display.get_display_stats()
            
            return jsonify({
                "status": "running",
                "service": "epaper_frame_display",
                "uptime_seconds": int(uptime),
                "frames_displayed": self.frame_count,
                "last_frame": self.last_frame_time,
                "display_initialized": self.display.initialized,
                "display_model": display_stats["model"],
                "display_description": display_stats["description"],
                "hardware_available": display_stats["hardware_available"],
                "mac_address": self._get_mac_address()
            })
            
        @self.app.route('/api/display/info', methods=['GET'])
        def get_display_info():
            """Display capabilities endpoint"""
            display_stats = self.display.get_display_stats()
            
            return jsonify({
                "display_type": "epaper_frame_display",
                "model": display_stats["model"],
                "description": display_stats["description"],
                "width": display_stats["width"],
                "height": display_stats["height"],
                "colors": ["black", "white", "red", "yellow"],
                "capabilities": [
                    "frame_display",
                    "png_support",
                    "color_epaper",
                    "stream_protocol"
                ],
                "hardware_available": display_stats["hardware_available"],
                "version": "2.0",
                "mac_address": self._get_mac_address()
            })
            
        @self.app.route('/api/display/models', methods=['GET'])
        def get_supported_models():
            """Get supported display models"""
            from display_service import DisplayService
            return jsonify({
                "supported_models": DisplayService.get_supported_models(),
                "current_model": self.display.model
            })
            
        @self.app.route('/api/test', methods=['GET'])
        def test_endpoint():
            """Simple test endpoint"""
            display_stats = self.display.get_display_stats()
            return jsonify({
                "message": "Frame display service is running",
                "timestamp": time.time(),
                "service": "epaper_frame_display",
                "model": display_stats["model"],
                "resolution": f"{display_stats['width']}x{display_stats['height']}"
            })
            
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Endpoint not found"}), 404
            
        @self.app.errorhandler(500)  
        def internal_error(error):
            return jsonify({"error": "Internal server error"}), 500
    
    def _process_stream_data(self, data):
        """Process Junction Relay stream data with LLLLTTRR prefix"""
        try:
            if len(data) < 8:
                print(f"[HTTP] Data too short for prefix: {len(data)} bytes")
                return False
            
            # Check if data starts with 8-digit prefix
            prefix_bytes = data[:8]
            try:
                prefix_str = prefix_bytes.decode('ascii')
                if not prefix_str.isdigit():
                    # Not prefixed data, might be raw PNG
                    print("[HTTP] No valid prefix found, trying as raw PNG")
                    return self._handle_raw_png(data)
            except UnicodeDecodeError:
                # Binary data, might be raw PNG
                print("[HTTP] Binary data without ASCII prefix, trying as raw PNG")
                return self._handle_raw_png(data)
            
            # Parse LLLLTTRR prefix
            length_hint = int(prefix_str[0:4])
            type_field   = int(prefix_str[4:6])
            route_field  = int(prefix_str[6:8])
            
            print(f"[HTTP] Prefix: Length={length_hint}, Type={type_field:02d}, Route={route_field:02d}")
            
            # Extract payload after prefix
            payload = data[8:]
            
            if   type_field == 2:  # Frame data
                print(f"[HTTP] Processing frame data: {len(payload)} bytes")
                return self._handle_frame_data(payload)
            elif type_field == 0:  # JSON data
                print(f"[HTTP] Processing JSON data: {len(payload)} bytes")
                return self._handle_json_data(payload)
            elif type_field == 1:  # Gzip data
                print(f"[HTTP] Processing Gzip data: {len(payload)} bytes")
                return self._handle_gzip_data(payload)
            else:
                print(f"[HTTP] Unknown type field: {type_field:02d}")
                return False
                
        except Exception as e:
            print(f"[HTTP] Error processing stream data: {e}")
            return False
    
    def _handle_frame_data(self, frame_data):
        """Handle frame data (Type 02)"""
        try:
            # Frame data should be PNG bytes
            if len(frame_data) < 100:
                print(f"[HTTP] Frame data too small: {len(frame_data)} bytes")
                return False
            
            # Check for PNG signature
            if frame_data[:8] != b'\x89PNG\r\n\x1a\n':
                print("[HTTP] Warning: Frame data doesn't have PNG signature")
            
            # Dispatch rendering to background
            def _render():
                try:
                    success = self.display.display_frame(frame_data)
                    if success:
                        self.frame_count += 1
                        self.last_frame_time = time.time()
                        print(f"[HTTP] ✅ Frame displayed: {len(frame_data)} bytes")
                    else:
                        print(f"[HTTP] ❌ Failed to display frame")
                except Exception as e:
                    print(f"[HTTP] ERROR in rendering thread: {e}")
            
            threading.Thread(target=_render, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"[HTTP] Error handling frame data: {e}")
            return False
    
    def _handle_json_data(self, json_data):
        """Handle JSON data (Type 00) - for compatibility"""
        try:
            json_str = json_data.decode('utf-8')
            print(f"[HTTP] Received JSON data: {json_str[:100]}...")
            return True
        except Exception as e:
            print(f"[HTTP] Error handling JSON data: {e}")
            return False
    
    def _handle_gzip_data(self, gzip_data):
        """Handle Gzip data (Type 01) - for compatibility"""
        try:
            import gzip
            decompressed = gzip.decompress(gzip_data)
            json_str     = decompressed.decode('utf-8')
            print(f"[HTTP] Received Gzip JSON data: {json_str[:100]}...")
            return True
        except Exception as e:
            print(f"[HTTP] Error handling Gzip data: {e}")
            return False
    
    def _handle_raw_png(self, png_data):
        """Handle raw PNG data (no prefix)"""
        try:
            # Check for PNG signature
            if png_data[:8] == b'\x89PNG\r\n\x1a\n':
                print(f"[HTTP] Processing raw PNG: {len(png_data)} bytes")

                def _render():
                    try:
                        success = self.display.display_frame(png_data)
                        if success:
                            self.frame_count += 1
                            self.last_frame_time = time.time()
                            print(f"[HTTP] ✅ Raw PNG displayed: {len(png_data)} bytes")
                        else:
                            print(f"[HTTP] ❌ Failed to display raw PNG")
                    except Exception as e:
                        print(f"[HTTP] ERROR in rendering thread: {e}")

                threading.Thread(target=_render, daemon=True).start()
                return True
            else:
                print("[HTTP] Data is not valid PNG")
                return False
        except Exception as e:
            print(f"[HTTP] Error handling raw PNG: {e}")
            return False
    
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