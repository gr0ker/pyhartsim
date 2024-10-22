# PyHartSim [![HART](https://github.com/gr0ker/pyhartsim/actions/workflows/hartsim.yml/badge.svg)](https://github.com/gr0ker/pyhartsim/actions/workflows/hartsim.yml)

Python [HART](https://en.wikipedia.org/wiki/Highway_Addressable_Remote_Transducer_Protocol) device simulator package.

## Setup

Install all dependencies:

```sh
make init
```

## Configure

Specify serial port number in `hartsim/config.py`:

```py
@dataclass
class Configuration:
    port: str = "COM3"
```

## Run

Run the simulator:

```sh
python -m hartsim.hartsim
```
