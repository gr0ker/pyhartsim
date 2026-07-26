# PyHartSim [![HART](https://github.com/gr0ker/pyhartsim/actions/workflows/hartsim.yml/badge.svg)](https://github.com/gr0ker/pyhartsim/actions/workflows/hartsim.yml)

Python [HART](https://en.wikipedia.org/wiki/Highway_Addressable_Remote_Transducer_Protocol) device simulator package.

## Setup

Install all dependencies:

```sh
make init
```

## Configure

The serial port defaults to `COM2`. Override it with the `HARTSIM_PORT`
environment variable (both simulators), or edit the default in `hartsim/config.py`:

```py
@dataclass
class Configuration:
    port: str = field(default_factory=_default_port)  # HARTSIM_PORT or COM2
```

## Run

Run the device simulator:

```sh
python -m hartsim.hartsim
```

## Log-Based Simulation

Replay responses from a captured HART communication log file:

```sh
python -m hartsim.logsim path/to/logfile.log [--port COM2]
```

The log simulator parses request/response pairs from log files (raw hex and FDI
structured text formats are auto-detected, including extended commands >255 which
are replayed as command-31 wrapper frames) and matches incoming requests exactly
(after stripping preambles). If multiple responses exist for the same request,
they are returned in round-robin order. Requests not present in the log first fall
back to a match by command number, otherwise get no reply at all.
