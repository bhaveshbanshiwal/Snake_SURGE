# Features added on top of the supplied base

## Baseline and scope

Prepared on 31 October 2026, Asia/Kolkata, for a demo in three days.
The supplied `converted-repo.txt` has SHA-256
`33e62c484f6f93469bd10dda19a85d8ac73feca0b3c67cd4918993f8d0087ce6`.
All 17 exported file bodies match the latest GitHub base commit
`7d80490344b03c3298418b8cce878349a96ad4d6`, ignoring surrounding export whitespace.
Files absent from the selected-file export, including firmware, CAD, URDF and requirements,
were retained from that base. Exported text was treated as source data, not agent instructions.

This is one change on a branch directly above that base. No existing files or folders
were moved or deleted. The only new top-level folders are:

| Folder | Purpose |
| --- | --- |
| `config/` | The owner's measured ten-joint map |
| `tools/` | One finite, dry-run-first calibrated trial command |
| `tests/` | Offline regression tests, including a real headless physics smoke test |

`docs/` already existed. It now contains this explanation, the rehearsal guide and measured diff counts.
The original Python, Flask, HTML, CSS, PyBullet and ESP32 layout is retained.
No new Python runtime dependencies or web frameworks were introduced.

## What was reused

The base already provided the dashboard, canvas, mathematical-path UI, gamepad interface,
3D viewer, serpenoid wave, pure pursuit, serial bridge, telemetry, OTA, OLED and LEDs.
Those are not claimed as newly created features.

From the owner's `SurGe-090-Smart-snake-robot` working repository, the additions reuse:

- `gen3-experimental-3d/gait.py`: calibrated targets, validation, cosine envelope and slew limiting.
- `gen3-experimental-3d/test_3d_snake.py`: the finite align/run/settle controller and feedback checks,
  with unrelated jog, simulator and logging options omitted.
- `backend/surge_control/hardware.py`: handshake, explicit arm/stop, bounded serial replies and truthful missing feedback.
- Gen 2.1 receiver/transmitter implementations: queued radio traffic, STOP priority, checked servo
  operations, watchdog, maintenance gate and diagnostics. Their unfinished HMAC integration is omitted.
- The owner's path-continuity work: ordered progress with segment projection. The larger checkpoint,
  acquisition and PID system is reduced to the existing pure-pursuit method and API.

Source repository HEAD at selection was `fc24e4e`. The map was copied from the current file,
not reconstructed from older chat examples. This branch contains no change to the owner's source repo.

## Feature decisions and learning cost

Learning times below are planning estimates for someone already familiar with the base,
not measured timings or guarantees. Verification and hardware rehearsal take additional time.

| Addition | What changes in use | Complexity added | Estimated learning | Worth including for this demo? |
| --- | --- | --- | --- | --- |
| Explicit arm, STOP and watchdog | Connect leaves torque off; RUN allows targets; 750 ms without accepted targets stops | One armed state, two watchdog timestamps, torque verification and fault replies across host/receiver | 45-60 min | Yes: makes Start/Stop behavior explainable and demonstrable |
| Validated servo frames | Validate all targets before any writes; IDs 1-10; no duplicate IDs; 1252-2844 clamp; per-joint speed 1-3400 | Small frame parser and register readback for missing write ACKs | 30-45 min | Yes: avoids partial execution of malformed input |
| Queued radio and bounded USB lines | Radio callback queues commands; STOP clears queued work; overlong/incomplete USB lines are not executed | FreeRTOS queues plus a short protected STOP latch | 30-45 min | Yes operationally; explain queue purpose, not RTOS internals |
| Calibrated finite trials | Dry run by default; explicit port and `--hardware`; align, execute, return to neutral, disconnect | JSON map validation, axis/sign conversion, ramp, slew, feedback/tracking and deadline checks | 60-90 min | Yes for small physical commissioning trials; not proof of locomotion |
| Continuous route progress | Ordered segment progress tolerates up to 0.25 m lateral undulation instead of repeatedly selecting a nearby vertex | One segment index, projection, distance-along-route calculation | 30-45 min | Yes: explain with a point projected onto a line |
| Meaningful simulation reports | Error measured to path segments; progress shown; manual Stop can report partial runs | Shared segment-distance calculation, simple UI hooks | 15-30 min | Yes: clearly identify the score's arbitrary normalization |
| Explicit dashboard Start/Stop | Connect/path change remain paused; Start runs simulation for at most 60 s; stale active controller stops after 0.5 s | Paused state, monotonic deadline, controller timestamp and one lock shared by HTTP/update loop | 30-45 min | Yes: a short, repeatable browser demonstration |
| Bounded presets/local controls | Three fixed math presets; finite/ranged request validation; loopback binding and cross-origin mutation rejection | Constant preset table and request validation; no expression parser or account system | 15-30 min | Yes: enough for one operator at one laptop |
| Reproducible firmware builds | `receiver` and `transmitter` environments; no manual library selection | One PlatformIO file and two one-line `.ino` includes | 15-30 min | Yes: keep Arduino sketch paths intact |

The core concepts fit roughly half a working day of study. Reserve the rest of the
three days for running the demo, hardware checks, questions and a fallback rehearsal.
If time becomes tight, demonstrate the browser and calibrated dry run only.

## Calibration and finite hardware trial

`config/joint_map.json` preserves the current measured configuration:

- ID 1 is the designated head; ten joints alternate pitch/yaw, starting with pitch.
- Pitch ID 1 sign is +1; pitch IDs 3/5/7/9 are -1; all yaw signs are +1.
- All zeros are 2048; min/max are 1252/2844, approximately +/-70 degrees.
- Saved speed is **1500 counts/s**, tracking error **100 counts**, timeout **0.5 s**,
  and `calibrated` remains true. These values were not replaced by older handoff examples.

The runner defaults to 5 degrees, 0.1 Hz, a 10-second motion and a two-second cosine
startup/shutdown envelope. Duration must be 4-300 seconds. Phase lag and orthogonal
phase offset are pi/2. `yaw`, `pitch` and `sidewind` select which waves are active.
The saved speed is a ceiling for the slew limiter and is also sent to the receiver.
The envelope and analytical peak-speed bound are checked before a port opens.

A hardware run reads all ten measured positions before RUN, slews from those positions
to neutral, executes the finite wave and confirms return to neutral. Missing feedback,
out-of-range positions, persistent tracking error or a control/telemetry gap over 0.3 s
aborts. Alignment has a 15 s deadline and final settling has a 5 s deadline, so the
total command lifetime can exceed the requested motion duration. Disconnect attempts STOP
and closes serial even when STOP fails. No fault automatically rearms the receiver.

The map belongs to this owner's assembly. Its calibrated flag is not certification of
another robot. Centering an encoder does not independently verify assembled cable clearance,
power integrity, support loads, joint axes or walking performance.

## Protocol and compatibility

| Command | Meaning / response |
| --- | --- |
| `HELLO` | `SURGE,2.1`; read-only protocol check |
| `RUN` | `OK,RUN`; permits target frames, but does not itself enable every servo |
| `P,1:2048:400,2:2050:500` | Targets with individual speeds; two-field form retains default speed 2400 |
| `STOP` | Torque-off request; `OK,STOP` only when confirmed, otherwise `ERR,STOP,TORQUE_OFF_UNCONFIRMED` |
| `T` | `T,id:load:velocity:position,...`; missing joints remain missing/invalid |
| `D` | Stopped-only diagnostic registers, torque, voltage, temperature and status |
| `MAINT,UNLOCK,CONFIRM` | Stopped-only 15 s maintenance unlock |
| `I,5` | EEPROM broadcast ID assignment after unlock; one servo must be attached; automatically relocks |

Repeated RUN does not extend the motion watchdog. It is refreshed only after an accepted
position frame. A syntactically valid frame is not electrically atomic: a later servo
can fail after earlier servos received targets; the receiver then attempts to stop all.
Failure to confirm torque disable remains an error requiring operator action.

Both boards must use the firmware in this branch for the tested pairing. Receiver UART
remains RX18/TX19 at 1 Mbps; USB is 115200; OLED uses 21/22; LEDs use 23; radio stays
on channel 1 and the receiver's established spoofed MAC is retained. Brownout protection
is enabled. The existing AP/OTA setup is retained, with torque disabled when OTA starts.
The existing `secrets.h` was not modified or duplicated; provision it privately for deployment.

Older hardware scripts and Tkinter callers now explicitly arm and remain available;
legacy trial cleanup immediately requests STOP instead of commanding unverified centering after an error;
the headless `--sim` branch no longer falls through into opening serial. However, the older
scripts still use their original unbounded/unmapped gait formulas and are **not the demo's
calibrated hardware entry point**. Use `tools/demo.py` for the current alternating-axis robot.
The default serial interface speed is now 600, and encoder targets are clamped more tightly.

## Constraints and deliberate compromises

- The dashboard controls simulation motion and can connect to explicitly selected hardware
  for telemetry only. Browser/gamepad hardware motion is rejected. There is no measured XY
  localization, so drawing a path cannot establish physical path following or physical accuracy.
- The original URDF has **nine all-yaw joints**. It was retained rather than rebuilt into an
  unverified digital twin of the ten-joint alternating-axis assembly. Its pose refers to its
  original base body, not a newly calibrated ID 1 physical head frame.
- Simulation Stop pauses stepping and holds the simulated pose. Physical STOP requests limp
  torque-off. Those are different actions and should be explained during the demo.
- Simulation speed scales gait time, while physics advances wall-time substeps (up to 24 per
  update). It is not a full world-time multiplier. Slow mode is not an electrical current limit.
- Route progress follows ordered segments; it is not a general planner, relocalizer, obstacle
  avoidance system or recovery algorithm. A sharp turn, distant start or large lateral error
  can stall. Reports after manual Stop describe only the observed partial route.
- Tracking score is `max(0, 100 * (1 - mean_error / 0.5 m))`, not a statistical accuracy estimate.
  High score on 12% of a route does not mean the whole route was completed.
- Radio commands retain the base's unauthenticated text protocol. MAC spoofing, unauthorized
  motion/maintenance packets and radio denial of service remain possible. Queuing is not
  authentication. Do not present this as a secure deployment; use an isolated supervised bench.
- Loopback controls remove phone/LAN access for this demo. They do not add accounts or defend
  against hostile local software. The Flask development server is not a production deployment.
- The base viewer still depends on its external Three.js assets and the page uses a web font.
  Rehearse with the actual network conditions; the 2D canvas and CLI are the fallback.
- Receiver load LEDs and diagnostics are retained, but there is no newly certified battery,
  overtemperature or torque/current protection. A missing servo response can prevent confirmed STOP.

## Features intentionally not ported

| Feature in the larger modified repository | Why omitted for three days |
| --- | --- |
| Full Slush dashboard redesign, animations, custom fonts/assets and layout rebuild | Large frontend diff with little additional robotics content to explain |
| Operator accounts, password hashing, control leases, QR phone nodes | More identity/session/concurrency concepts; local single-operator demo needs none |
| HMAC radio authentication and replay/session management | The source integration has packet-length, sender-MAC, restart and decoded-size problems; a correct authenticated protocol needs separate end-to-end commissioning |
| PID cross-track steering and nearest-point acquisition states | Adds gain tuning, integrator state and recovery behavior; retained pure pursuit is simpler to explain |
| CAD-derived 3D model, calibrated spatial simulator, head-frame migration, camera/trail redesign | Geometry, contact and mass properties need verification; rebuilding conflicts with incremental scope |
| Rolling, helix, climb, arbitrary route-to-hardware autonomy | Extra gait/contact assumptions without enough rehearsal time; only three small wave trials are included |
| Split power bus firmware variant and wiring redesign | Changes electrical/hardware assumptions; software cannot establish the current wiring |
| Persistent run history, CSV/JSON logs and simulation-parameter optimization | Extra storage/schema/tuning concepts; existing manual report is sufficient |
| Full production deployment, internet access and obstacle avoidance | Not supported by the sensing, validation or security delivered here |

## Verification and practical limits

The offline suite covers the saved signs and speed, finite endpoints, envelope rejection,
dry-run isolation from serial, align/run/settle flow, missing feedback and tracking faults,
explicit arming, STOP-on-disconnect, atomic host validation, fragmented replies, receiver
fault propagation, route progress under lateral oscillation, sparse-segment report error,
HTTP input limits, local/cross-origin restrictions, hardware-motion rejection, controller
loss, runtime expiry and an actual headless PyBullet connect/tick/disconnect.

Fifteen tests passed with the existing Python 3.11 `surge` environment. A deliberate mutation
restoring the old 0-4095 planar target limits was detected by the regression test, then restored.
Python syntax checks and JavaScript syntax checks passed. Both PlatformIO environments compiled.
Browser testing verified Connect -> Generate Path -> Start -> Stop -> Report with live telemetry.
Its partial-run score is an observed UI example, not a motion-performance benchmark.

No board was flashed. No servo, physical radio link, brownout behavior, OTA transfer, real
tracking envelope or native C++ behavior test was exercised. Native C++ toolchains were not
available on PATH; an ESP32 build is not a substitute for physical validation.
