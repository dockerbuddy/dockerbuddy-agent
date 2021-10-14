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
To run normal agent just type in:
```./run```