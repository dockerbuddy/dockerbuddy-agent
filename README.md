<div id="top" align="center">

![Contributors](https://img.shields.io/github/contributors/agh-docker-monitoring/dockiera-agent?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/agh-docker-monitoring/dockiera-agent?style=for-the-badge)
![Issues](https://img.shields.io/github/issues/agh-docker-monitoring/dockiera-agent?style=for-the-badge)

</div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/agent.png" alt="Logo" width="400" height="300">
  </a>

  <h3 align="center">Dockiera agent</h3>

  <p align="center">
    Agent for every buddy
    <br />
    <a href="#getting-started"><strong>Explore the docs »</strong></a>
    <br /><br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Content</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<br />

## About The Project

Agent was designed to collect metrics from host and docker containers.

Normally agent can be built and run in docker environment.

For demonstrational purposes it can be run as a mock agent as well.

## Getting Started

To get agent running follow these simple steps.

### Prerequisites

- Docker
    <ul>
        <li>
            <a href="https://docs.docker.com/desktop/windows/install/">
                Install Docker on Windows
            </a>
        </li>
        <li>
            <a href="https://docs.docker.com/engine/install/ubuntu/">
                Install Docker on Linux
            </a>
        </li>
        <li>
            <a href="https://docs.docker.com/desktop/mac/install/">
                Install Docker on Mac
            </a>
        </li>
    </ul>
- Poetry
    - Linux:
    ```curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -```
    - Mac: ```brew install poetry```
    - Windows:
        1. Enter Powershell
        1. Run: ```(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -```

### Installation

1. Clone the repo

   ```git clone https://github.com/agh-docker-monitoring/dockiera-agent.git```
2. Change directory to dockiera-agent

   ```cd dockiera-agent```
3. Install dependencies

    ```poetry install```


<!-- USAGE EXAMPLES -->
## Usage

### Run mock agent
```poetry run mock```

### Run normal agent in docker
```./run```

## License

Distributed under the MIT License.

<p align="right"><a href="#top">To the top</a></p>
