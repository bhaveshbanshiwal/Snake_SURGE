# Snake SURGE: three-day demo additions

Incremental additions to `bhaveshbanshiwal/Snake_SURGE` commit `7d80490`.
The existing folders, dashboard, serial protocol, CAD and planar URDF remain in place.
New top-level folders: `config/`, `tools/`, `tests/`.

Start with [the three-day demo guide](docs/THREE_DAY_DEMO.md).
Read [features, learning cost and compromises](docs/DEMO_FEATURES.md) before a physical trial.
[Measured code changes](docs/DEMO_COMPLEXITY.md) separate implementation, tests and documentation.

From this repository's root, with the existing Python dependencies installed:

```powershell
python tools/demo.py --gait pitch
python -m unittest discover -s tests -v
python web_app.py
```

Open <http://127.0.0.1:5000>. Connect Simulation, generate a path, then press Start.
Connecting and drawing do not start motion. Stop opens the simulation report.
Hardware motion uses the explicitly enabled finite CLI trial; dashboard hardware is telemetry only.

Build firmware without flashing:

```powershell
python -m platformio run -e receiver -e transmitter
```
