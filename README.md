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

## Disclaimer
This project is still in **development** and **not** ready for actual use.

## Installation

### Requirements
- =< Python3.11
- Go

### Installation

```bash
git clone https://github.com/screamz2k/PhoenixC2.git
cd PhoenixC2
python3 -m pip install poetry
poetry install
```

## Usage

### Start the server

#### Host

```bash
poetry run phserver
```

The Web-Interface is available at `http://localhost:8080` by default.

### Start the client
```bash
poetry run phclient
```

#### Docker
```bash
# server
docker run --network host screamz2k/phoenixc2 phserver
# client
docker run --network host screamz2k/phoenixc2 phclient
```

## LICENSE
View license [here](LICENSE)
