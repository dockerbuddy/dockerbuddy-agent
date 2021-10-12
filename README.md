# dockiera-agent

## Installation

### Clone repository
```
$ git clone https://github.com/agh-docker-monitoring/dockiera-agent.git
```

### Poetry installation
- Linux: ```curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -```
- Mac: ```brew install poetry```
- Windows:
    1. Enter Powershell
    1. Run: ```(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -```

Then install project dependencies with poetry:
* ```$ cd dockiera-agent```
* ```$ poetry install```

## Usage

# Deprecated
Run Agent/MockAgent by:

```$ poetry run start```

You can use agent in two modes:
- normal agent - monitor actual data from host and docker containers
- mock agent - put sample data into influxdb. The data can be configured by user.

# Active
Run Agent in Docker environment:

1. Build an image:
```docker build -t dockiera-agent-image .

```

2. Run container:
```docker run --name dockiera-agent-container --network=dockiera-app_default  -v /var/run/docker.sock:/var/run/docker.sock dockiera-agent-image

```