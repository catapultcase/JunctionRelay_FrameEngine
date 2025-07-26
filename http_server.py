"""
HTTP Server - Receives frame data and routes to display
Supports multi-model display info
"""

from flask import Flask, request, jsonify
import time
import uuid

class FrameHTTPServer:
    def __init__(self, display_service):
        self.display = display_service
        self.app = Flask(__name__)
        self.running = False
        self.frame_count = 0
        self.last_frame_time = None

        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/api/display/frame', methods=['POST'])
        def display_frame():
            try:
                frame_data = request.get_data()
                if not frame_data:
                    return jsonify({"error": "No frame data received"}), 400

                if len(frame_data) < 100:
                    return jsonify({"error": "Frame data too small"}), 400

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
            uptime = time.time() - self.display.start_time if self.display.start_time else 0
            return jsonify({
                "status": "running",
                "service": "epaper_frame_display",
                "uptime_seconds": int(uptime),
                "frames_displayed": self.frame_count,
                "last_frame": self.last_frame_time,
                "display_initialized": self.display.initialized,
                "mac_address": self._get_mac_address(),
                "model": self.display.model,
                "resolution": {
                    "width": self.display.width,
                    "height": self.display.height
                }
            })

        @self.app.route('/api/display/info', methods=['GET'])
        def get_display_info():
            model = self.display.model
            resolution = {
                "5in79g": (792, 272),
                "7in3sce": (800, 480)
            }.get(model, (self.display.width, self.display.height))

            colors = ["black", "white", "red", "yellow"]
            if model == "7in3sce":
                colors += ["green", "blue"]

            return jsonify({
                "display_type": f"epaper_frame_display_{model}",
                "width": resolution[0],
                "height": resolution[1],
                "colors": colors,
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
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                            for ele in range(0, 8*6, 8)][::-1])
            return mac
        except:
            return "00:00:00:00:00:00"

    def start(self, host="0.0.0.0", port=80):
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
        self.running = False
        print("[HTTP] Server stopped")
