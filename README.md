<p align="center">
    <img align="center" src="pages/images/logo.png" width="100px" height="100px" alt="PhoenixC2" />
    <h1 align="center">PhoenixC2</h1>
    <p align="center"> An Open-Source C2-Framework written in pure Python3.</p>
</p>
<p align="center">
    <img align="center" src="https://github.com/screamz2k/PhoenixC2/actions/workflows/tests.yml/badge.svg"/>
    <img align="center" src="https://github.com/screamz2k/PhoenixC2/actions/workflows/docker.yml/badge.svg"/>
    <img align="center" src="https://github.com/screamz2k/PhoenixC2/actions/workflows/pypi-publish.yml/badge.svg"/>
</p>

## Disclaimer
This project is still in **development** and **not** ready for professional use.
The author and its affiliates do not endorse or condone any illegal or malicious activity conducted with this framework. Users of this framework are solely responsible for ensuring that their use of this framework is in compliance with all applicable laws and regulations.

## Features
- [x] Modern Web-Interface
- [x] Built for Teams and Organizations (Multi-User)
- [x] Customizable (Plugins, Modules, Kits)
- [x] Easy to use
- [x] Easy to extend
- [x] Supports different languages (Python, Go, ...)

### Planned Features
- [ ] Finished Web-Interface
- [ ] CLI-Interface
- [ ] Multi-Language Loaders
- [ ] More standard modules/kits/plugins
- [ ] Better documentation
- [ ] More tests

## Installation
Installation from source.
### Requirements
- Python3.11 =< 
- Go 1.15 =< 

### Command Line

```bash
git clone https://github.com/screamz2k/PhoenixC2.git
cd PhoenixC2
python3 -m pip install poetry
poetry install
```

## Usage

### Local

#### Start the server

```bash
poetry run phserver
```
The Web-Interface is available at [http://localhost:8080](http://localhost:8080) by default.

### Start the client
The client is **not** yet available.

## Docker

```bash
# server
docker run --network host screamz2k/phoenixc2 phserver
```


## Documentation
The documentation is available [here](https://screamz2k.gitbook.io/phoenixc2/)

## Contributing
Contributions are welcome! Please read the [contribution guidelines](https://github.com/screamz2k/PhoenixC2/.github/CONTRIBUTING.md) first.

Please vote in the [Discussion Tab](https://github.com/screamz2k/PhoenixC2/discussions/categories/polls) for development choices and new features.

## LICENSE
View license [here](https://github.com/screamz2k/PhoenixC2/LICENSE)

# Star History
[![Star History Chart](https://api.star-history.com/svg?repos=screamz2k/phoenixc2&type=Date)](https://star-history.com/#screamz2k/phoenixc2&Date)

- 08/04/23 Thank you all for over 50 stars in just two days :)
- 09/04/23 100 stars! I just 3 days. Thanks for the great support!
