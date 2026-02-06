# Copilot Instructions for PyHartSim

## Build & Test Commands

```sh
# Install dependencies
make init

# Run all tests with coverage
make test

# Run a single test file
py.test tests/test_payloads.py

# Run a single test
py.test tests/test_payloads.py::TestPayloads::test_u8_size_is_one

# Lint
make ruff
```

## Running the Simulator

```sh
python -m hartsim.hartsim
```

Configure serial port in `hartsim/config.py` before running.

## Architecture

PyHartSim is a HART (Highway Addressable Remote Transducer Protocol) device simulator that communicates over serial port at 1200 baud with odd parity.

### Core Components

- **hartsim.py** - Main entry point. Sets up serial port, creates simulated devices, and runs the request/response loop. Routes incoming HART frames to appropriate devices based on polling or unique address.

- **framingutils.py** - HART frame parsing and serialization. `HartFrameBuilder` is a state machine that accumulates bytes into complete frames. `HartFrame` represents a parsed frame with type, address, command, and payload.

- **commands.py** - Command handlers. `handle_request()` dispatches to command-specific handlers (Cmd0, Cmd1, etc.). Each command has Request/Reply dataclasses for payload serialization.

- **devices.py** - `HartDevice` dataclass holds all device state: variables, tags, status, configuration. `DeviceVariable` represents a single process variable with units, value, and limits.

- **payloads.py** - Binary payload serialization primitives. `U8`, `U16`, `U24`, `U32`, `F32` for numeric types. `Ascii`, `PackedAscii` for strings. `PayloadSequence` for composing complex payloads.

- **logparser.py** - Log file parser for log-based simulation. Extracts request/response pairs from HART communication logs. `LogResponseProvider` provides round-robin response selection.

- **logsim.py** - Log-based simulator entry point. Replays logged responses instead of simulating device logic. Matches requests exactly after stripping preambles.

### Data Flow

1. Serial bytes arrive → `HartFrameBuilder.collect()` accumulates until frame complete
2. Frame routed to device by polling address (short) or unique address (long)
3. `handle_request()` dispatches to command handler based on command number
4. Handler builds reply using device state and payload types
5. Reply frame serialized and sent back over serial

### Payload System

Payload types are iterable (serialize) and have `deserialize()` (parse). Use `PayloadSequence` as a base class to compose complex payloads from primitives:

```python
@dataclass
class Cmd1Reply(PayloadSequence):
    status_0: U8 = U8()
    status_1: U8 = U8()
    pv_units: U8 = U8()
    pv_value: F32 = F32()
```

## Key Conventions

- HART protocol uses big-endian byte order for multi-byte values
- Command handlers follow pattern: `CmdNRequest` for input, `CmdNReply` with static `create(device)` method for output
- Extended commands (number > 255) use command 31 wrapper with 2-byte extended command number
