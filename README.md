# PhoenixC2
> A Open-Source C2-Framework written in pure Python3.



# Installation 
> PhoenixC2 currently only supports OS X & Linux
## OS X & Linux
```sh
git clone git@github.com:screamz2k/PhoenixC2.git
cd PhoenixC2
sudo python3 install.py
```
## Docker
### Pulling the Image from Dockerhub
```sh
docker pull Screamz2k/PhoenixC2
docker run --name My-C2 --network host -d PhoenixC2
```
### Building it yourself
```sh
git clone git@github.com:screamz2k/PhoenixC2.git
cd PhoenixC2
docker build .
```
