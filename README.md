# PhoenixC2
> An Open-Source C2-Framework written in pure Python3.

## Features
- [x] Modern Web-Interface
- [x] CLI-Interface
- [x] Built for Teams and Organizations (Multi-User)
- [x] Customizable (Plugins, Modules, Kits)
- [x] Easy to use
- [x] Easy to extend
- [x] Supports different languages (Python, Go, ...)


## Installation

### Requirements
- =< Python3.10
- Go

### Install

```bash
git clone https://github.com/screamz2k/PhoenixC2.git
cd PhoenixC2
python3 -m pip install .
```

## Usage

### Start the server

#### Host

```bash
# via entrypoint
phserver
# via module
python3 -m phoenixc2.server
# or
python3 -m phoenixc2 server
```

The Web-Interface is available at `http://localhost:8080` by default.

### Start the client
```bash
# via entrypoint
phclient
# via module
python3 -m phoenixc2.client
# or
python3 -m phoenixc2 client
```

#### Docker
```bash
# server
docker run --network host screamz2k/phoenixc2 server
# client
docker run --network host screamz2k/phoenixc2 client
```

## LICENSE
View license [here](LICENSE)
