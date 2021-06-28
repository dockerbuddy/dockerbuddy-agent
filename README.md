# dockiera-agent

You can use agent in two modes:
- normal agent - monitor actual data from host and docker containers
- mock agent - put sample data into influxdb. The data can be configured by user.

Docker container status - 
Instead of saving docker container status as string we made Enum Status and save it as integer.

The Status Enum:
- created = 0
- restarting = 1
- running = 2
- removing = 3
- paused = 4
- exited = 5
- dead = 6  
