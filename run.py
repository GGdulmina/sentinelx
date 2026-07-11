"""SentinelX Management API and Background Daemon orchestrator.

Spawns the background authentication monitoring daemon thread and hosts
the management REST API / WebSocket real-time telemetry stream.
"""

import os
import sys
import threading
import time
import logging
from flask import Flask, jsonify
from flask_socketio import SocketIO

# Resolve path injection dependencies
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.watcher import follow
from core.parser import parse_line
from core.alerts import AlertEngine

# Setup structured console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("sentinelx.runtime")

# Initialize Web Engine Application Components
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sentinelx-core-secure-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Target system log trail configuration
TARGET_LOG_PATH = os.environ.get("SENTINELX_LOG_PATH", "core/tests/fixtures/auth_small.log")
STATE_FILE_PATH = os.environ.get("SENTINELX_STATE_PATH", "sentinelx_state.json")

# Core engine tracking structures
SYSTEM_STATS = {
    "status": "active",
    "lines_parsed": 0,
    "alerts_dispatched": 0,
    "target_file": TARGET_LOG_PATH
}

# Thread coordination flags
shutdown_event = threading.Event()


def background_daemon_worker(log_path: str, state_path: str) -> None:
    """Run real-time authentication monitoring inside an isolated background thread."""
    logger.info(f"Background daemon tracking target log vector: {log_path}")
    
    # Instantiate isolated alert threshold analyzer
    engine = AlertEngine(state_path=state_path)
    
    try:
        # Stream live log append transitions via follow generator
        for raw_line in follow(log_path):
            if shutdown_event.is_set():
                break
                
            SYSTEM_STATS["lines_parsed"] += 1
            
            # Pipe to regex structural tokenizer
            parsed_data = parse_line(raw_line)
            if not parsed_data:
                continue
                
            # Process malicious threat metrics
            alert_payload = engine.process_event(parsed_data)
            if alert_payload:
                SYSTEM_STATS["alerts_dispatched"] += 1
                logger.warning(f"SECURITY ESCALATION: [{alert_payload['severity']}] {alert_payload['message']}")
                
                # Emit non-blocking event stream packet out to all live dashboard sockets
                socketio.emit('security_alert', alert_payload)
                
    except Exception as e:
        logger.error(f"Uncaught exception inside background execution track: {e}")


# =========================================================================
# Management API Routing Layer
# =========================================================================

@app.route("/api/v1/health", methods=["GET"])
def get_health_status():
    """Retrieve runtime operational health indicators."""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "daemon_alive": any(t.name == "DaemonWorker" for t in threading.enumerate())
    }), 200


@app.route("/api/v1/stats", methods=["GET"])
def get_telemetry_metrics():
    """Expose total lines parsed and metric indicators."""
    return jsonify(SYSTEM_STATS), 200


if __name__ == "__main__":
    logger.info("Initializing SentinelX Operational System Fabric...")
    
    # Spawn background monitoring thread
    worker_thread = threading.Thread(
        target=background_daemon_worker,
        args=(TARGET_LOG_PATH, STATE_FILE_PATH),
        name="DaemonWorker",
        daemon=True
    )
    worker_thread.start()
    
    try:
        # Run Flask development application engine
        socketio.run(app, host="127.0.0.1", port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("Termination signal captured. Executing graceful system shutdown...")
    finally:
        shutdown_event.set()
        logger.info("SentinelX Daemon stopped cleanly.")
        sys.exit(0)