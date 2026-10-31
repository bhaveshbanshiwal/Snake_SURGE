# Three-day preparation and demo script

## Recommendation

Use the browser simulation and the calibrated dry run as the dependable presentation.
Add a small physical pitch trial only after independently identifying both boards,
checking the current assembly/map and rehearsing Stop. Do not make successful physical
walking, autonomous path following or a CAD-accurate 3D simulation the success criterion.

## Setup

Run commands from the root of this checkout, not the owner's larger three-generation repo.
Use an existing environment that can import Flask, pyserial, psutil and PyBullet.
On the prepared laptop the existing Python executable is:

```powershell
Set-Location 'C:\Users\gannu\Downloads\Snake_SURGE-demo'
& 'C:\Users\gannu\miniconda3\envs\surge\python.exe' -m unittest discover -s tests -v
& 'C:\Users\gannu\miniconda3\envs\surge\python.exe' tools/demo.py --gait pitch
& 'C:\Users\gannu\miniconda3\envs\surge\python.exe' web_app.py
```

On another computer, install the existing `requirements.txt` in a suitable environment
and use `python` in place of that absolute executable. PyBullet requires a compatible
Python wheel/package; do not spend the demo deadline repeatedly compiling it from source.
If simulation cannot start, use the dry run and explain the computed targets.

## Day 1: understand and prove the software

1. Run the tests and all three dry-run presets:

   ```powershell
   python tools/demo.py --gait yaw
   python tools/demo.py --gait pitch
   python tools/demo.py --gait sidewind
   ```

2. Explain one line of the map: ID, physical axis, sign, zero and permitted encoder interval.
   Explain why pitch ID 1 differs from pitch IDs 3/5/7/9. Keep the actual saved values unchanged.
3. Explain the wave in plain language: sine gives motion, spatial phase creates a travelling
   wave, pitch/yaw waves are a quarter-cycle apart, and the cosine envelope starts/ends at zero.
4. Open <http://127.0.0.1:5000>. Leave Simulation selected and Run Headless checked.
   Connect, generate Gentle sine, Start, Stop, and explain the report as a partial simulation run.
5. Study only `src/calibrated_gait.py`, `tools/demo.py`, the protocol table and the short path
   projection method. Do not try to learn the full larger modified repository.

## Day 2: rehearse the physical boundary, if hardware is included

Build without uploading first:

```powershell
python -m platformio run -e receiver -e transmitter
```

Identify which board is plugged in before each upload. Support the robot and disconnect
motor power while flashing; select the actual port. The examples are commands for the
operator to run, not a record of uploads performed during development:

```powershell
python -m platformio run -e receiver -t upload --upload-port COM6
# Swap to the transmitter, reconfirm its port, then:
python -m platformio run -e transmitter -t upload --upload-port COM6
```

COM6 is the owner's previous observed port, not a guarantee of device identity. The receiver
keeps destination MAC `28:05:a5:4e:01:38`; its upload-reported factory MAC can differ.

If using dashboard hardware telemetry, disconnect that engine before starting the CLI so
the serial port is released. Verify all ten feedback rows and safe initial positions before a trial. The runner refuses
to RUN with missing/out-of-range positions. Check cable travel and support the assembly.
Then, after the dry run and with the intended transmitter attached:

```powershell
python tools/demo.py --hardware --port COM6 --gait pitch --amplitude 5 --duration 10
```

The requested 10 s excludes alignment and final settling. Ctrl+C exits through disconnect,
which requests STOP. If software cannot confirm torque-off, stop interacting with the robot
and use the physical power cutoff; do not assume a missing acknowledgment proves it is limp.
The receiver's independent 750 ms watchdog is a fallback, not an electrical emergency stop.

Do not use the older `test_3d_snake.py`/`test_spiral.py` motion formulas for the current
assembly. They are retained base tools, not the calibrated demonstration.

If anything is unreliable, keep Day 3 software-only. Do not add gains, amplitudes, new axes
or new firmware features to recover a presentation at the last minute.

## Day 3: freeze the scope and rehearse

- Run the same tests, dry run and browser sequence once more.
- Choose a short, gentle route near the simulated origin; a manual Stop report is acceptable.
- Save a local screen recording or screenshots if needed; do not rely on a live network for the 3D viewer.
- Keep the hardware disconnected for the opening software explanation.
- Rehearse the fallback: dry-run output plus the architecture/feature document.

## Suggested five-minute presentation

| Time | Show | Explain |
| --- | --- | --- |
| 0:00-0:45 | Original folder layout and README | This is an incremental change above the supplied base, not a rebuild |
| 0:45-1:45 | Generate gentle sine, Connect and Start simulation | Pure pursuit aims ahead; segment projection records ordered progress |
| 1:45-2:30 | Stop and report | Deviation is distance to the path; partial-route score does not prove completion |
| 2:30-3:30 | Map and pitch dry run | Measured signs/limits are preserved; inactive yaw joints remain at neutral |
| 3:30-4:15 | Protocol table or rehearsed small physical trial | Connect is limp, RUN arms, P moves, STOP/watchdog disable torque |
| 4:15-5:00 | Feature/compromise table | No measured hardware XY, no authenticated radio deployment, no verified digital twin |

## Questions to be ready for

- **Why three new folders?** Configuration, one executable demo tool and tests each have a clear purpose;
  the existing architecture remains understandable.
- **Does sidewind mean it walks?** No. It computes two orthogonal waves. Ground contact, friction,
  assembly and load still determine whether there is net movement.
- **Why not the full redesign?** The deadline favors features with a short explanation and testable behavior.
- **Is the 3D view the hardware twin?** No. It visualizes the retained planar model, with nine joints.
- **What does Stop mean?** Simulation pauses; hardware requests torque-off and reports whether it was confirmed.
- **Is the radio secure?** No. This preserves the base's text protocol; the unfinished HMAC changes were not ported.
- **What is worth learning after the demo?** Session-safe authenticated radio, verified physical localization,
  accurate spatial geometry/contact models, then controller tuning and deployment controls.
