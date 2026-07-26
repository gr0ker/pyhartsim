# CLAUDE.md

Guidance for working in PyHartSim — a Python HART (Highway Addressable Remote
Transducer Protocol) device simulator that talks over a serial port.

## Environment (read this first)

On this machine the dependencies live in the repo's `.venv`, **not** in the
system Python. Bare `python`, `pip`, `py.test`, and `ruff` resolve to the system
interpreter which does **not** have the deps installed. Use the venv explicitly:

```sh
.venv/Scripts/python.exe -m pytest tests -q          # run tests
.venv/Scripts/python.exe -m ruff check . --target-version=py312   # lint
.venv/Scripts/python.exe -m hartsim.hartsim          # run the simulator
```

The `Makefile` targets (`make init|test|ruff`) assume the venv tools are on
PATH; prefer the explicit commands above unless the venv is activated.

## Commands

```sh
# Run all tests (fast — ~0.25s, 121 tests at time of writing)
.venv/Scripts/python.exe -m pytest tests -q

# Run a single test file / single test
.venv/Scripts/python.exe -m pytest tests/test_payloads.py
.venv/Scripts/python.exe -m pytest tests/test_payloads.py::TestPayloads::test_u8_size_is_one

# Lint — ALWAYS run before committing; fix all findings
.venv/Scripts/python.exe -m ruff check . --target-version=py312

# Coverage report
.venv/Scripts/python.exe -m pytest tests --cov --cov-report=html:cov-report
```

## Running the simulator

`python -m hartsim.hartsim` opens a serial port (1200 baud, odd parity) and runs
the request/response loop. Port selection: `HARTSIM_PORT` env var, else the
`COM2` default in `hartsim/config.py`. Without a real or virtual serial port the
live loop can't be exercised — logic is verified via the unit tests, not by
running the loop.

Log-based replay: `python -m hartsim.logsim path/to/logfile.log [--port COMn]`
replays request/response pairs captured from real HART traffic instead of
simulating device logic. Both raw-hex and FDI structured log formats are
auto-detected; extended commands (>255) are rebuilt as command-31 wrapper frames.

## Architecture

HART frames arrive as serial bytes and flow through:

1. `framingutils.py` — `HartFrameBuilder.collect()` is a state machine that
   accumulates bytes into a complete `HartFrame` (type, address, command,
   payload). Handles parsing and serialization. Big-endian multi-byte values.
2. `hartsim.py` — entry point. Sets up serial, creates `HartDevice`s, routes
   each frame to a device by polling (short) or unique (long) address.
3. `commands.py` — `handle_request()` dispatches by command number to handlers.
   This is the largest module and the center of gravity for protocol behavior.
4. `devices.py` — `HartDevice` holds all device state (variables, tags, status,
   config). `DeviceVariable` = one process variable (units, value, limits).
5. `payloads.py` — binary serialization primitives: `U8/U16/U24/U32/F32`,
   `Ascii`, `PackedAscii`, and `PayloadSequence` to compose complex payloads.
6. `logparser.py` / `logsim.py` — log replay. `LogResponseProvider` returns
   matching responses in round-robin order when a request has several.

## Conventions

- HART is big-endian for multi-byte values.
- Command handlers follow the pattern `CmdNRequest` (input) + `CmdNReply` (output)
  with a static `create(device)` method that builds the reply from device state.
- Extended commands (number > 255) use the command-31 wrapper with a 2-byte
  extended command number.
- Payload types are iterable (serialize) and expose `deserialize()` (parse).
  Compose by subclassing `PayloadSequence`:

  ```python
  @dataclass
  class Cmd1Reply(PayloadSequence):
      status_0: U8 = U8()
      status_1: U8 = U8()
      pv_units: U8 = U8()
      pv_value: F32 = F32()
  ```

## Known gaps / TODO for future context

- No in-tree sample log fixture for `logsim` end-to-end validation.
- No linked HART spec reference for command numbers / status-byte bit meanings —
  verify protocol details against an external source when adding commands.
