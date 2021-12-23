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
    <a href="#running-agent-on-host"><strong>Explore the docs »</strong></a>
    <br /><br />
  </p>
</div>
<br />

## About The Project

Agent was designed to collect metrics from host and docker containers.

## Running agent on host

1. Get the distribution for your platform:
<a href="https://github.com/agh-docker-monitoring/dockiera-agent/releases/tag/v1.2.0-beta">Latest Release</a>
2. Change agent environments in bash script ```./run```
<br> See [Environment variables](#environment-variables).
3. Run the bash script ```./run```

## Environment variables
- `AGENT_HOST_ID` - Host ID - Available after adding a host.
- `AGENT_BACKEND_ENDPOINT` - Metrics endpoint. Should have suffix `api/v2/metrics`
- `AGENT_FETCH_FREQ` - Frequency with which agent sends data

## Dev Environment
Agent and can also be run locally using Poetry. <br>
There is mock version of the agent sending fake data.

### Prerequisites
- Docker
- Poetry

### Steps
1. Clone the repository
2. Create `.env` file with [Environment variables](#environment-variables)
3. Run `poetry install` to install dependencies

### Run normal agent
```poetry run normal```

### Run mock agent
```poetry run mock```

## License

Distributed under the MIT License.

<p align="right"><a href="#top">To the top</a></p>
