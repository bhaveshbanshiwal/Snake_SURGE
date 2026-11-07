"""Snake SURGE primary web application entry point. Launches the unified web dashboard."""
import sys
import argparse
import atexit
from pathlib import Path

# Setup paths for root, website, and kinematics
ROOT_DIR = Path(__file__).resolve().parent
for p in [str(ROOT_DIR), str(ROOT_DIR / "website"), str(ROOT_DIR / "kinematics")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from website.web_app import app, create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snake SURGE Web Dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    app.config['LAN_BOUND'] = args.host not in ('127.0.0.1', 'localhost', '::1')
    runtime = app.config["CONTROL"]
    runtime.start_worker()
    atexit.register(runtime.close)
    atexit.register(app.config['GEN3'].close)
    try:
        print(f"Starting Snake SURGE Web Dashboard on http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    finally:
        app.config['GEN3'].close()
        runtime.close()
