# Measured complexity of this single change

Counts are from `git diff --cached --numstat` against base `7d80490`, measured on
31 October 2026. A line means a physical text line, including comments and blank lines.
It is a review-size measure, not a runtime-cost or learning-time measurement. Git can count
an edited line as both one deletion and one insertion. Counts exclude this count document.

| Group | Lines added | Lines removed | Net lines |
| --- | ---: | ---: | ---: |
| Receiver/transmitter and bounded serial parser | 421 | 104 | +317 |
| Calibrated targets, saved map and finite runner | 318 | 0 | +318 |
| Host transport and legacy caller compatibility | 171 | 108 | +63 |
| Existing path/simulator/dashboard integration | 278 | 217 | +61 |
| Build and ignore configuration | 23 | 0 | +23 |
| Offline tests | 241 | 0 | +241 |
| Guides and README (before this count document) | 328 | 0 | +328 |

Implementation/build/config total: **1211 additions, 429 deletions, +782 net lines**.
This includes the 88-line measured map, firmware checks and compatibility edits.
It does not mean 1211 lines of new algorithms were invented: the map, calibrated controller,
receiver and host transport reuse the owner's working implementations.

## Why this is not just a few added lines

- Arming without host changes would break existing callers. Watchdog without bounded input
  and clean shutdown would create misleading Stop behavior. Those form one connected feature.
- Shortening the receiver by dropping whole-frame validation, torque readback or the
  maintenance lock would reduce line count by removing behavior needed by hardware.
- The finite runner reuses one wave generator and one align/run/settle loop for all three
  presets, rather than duplicating three physical demo scripts.
- The existing dashboard remains the UI. Existing pure pursuit remains the steering law;
  only ordered progress/projection and its callers are added, rather than the larger PID system.
- There is no new web framework, runtime package, database, daemon, account store, GUI
  application, authentication protocol or model asset pipeline.
- The two one-line PlatformIO entry files include the original `.ino` files because
  PlatformIO does not discover these nested sketches as standalone sources. The wrapper
  prevents moving the original Arduino folders or duplicating their implementations.
- Tests deliberately exercise failures as well as happy paths. Documentation is longer
  because the requested comparison, learning plan and limits must be reviewable.

## Operational complexity to remember

The operator needs two ESP32 firmware targets, one matching text protocol, one map,
one Python environment and one CLI trial command. The browser adds one local server and
one paused/running state. Hardware trials and browser simulation are separate demonstrations.
The retained legacy scripts are not an additional supported gait workflow for the measured assembly.

The highest remaining costs are physical commissioning and the unauthenticated radio boundary,
not the number of Python lines. See `DEMO_FEATURES.md` for the feature-by-feature value judgment.
