from pathlib import Path

# SLEEP TIMES
FETCH_FREQ = 10

# DEV
HOME_PATH = Path("/")
MAX_WORKERS = 50

# MOCK AGENT
MOCK_CONTAINERS_FILE = Path("container_stats.csv")
VIRT_MEM_TOTAL = 34359738368
DISK_MEM_TOTAL = 250685575168
STARTING_PERCENT = float("50")
AVAILABLE_STATES = [
    "created",
    "restarting",
    "running",
    "removing",
    "paused",
    "exited",
    "dead",
]

# BACKEND
HOST_ID = "1"
BACKEND_ENDPOINT = "http://localhost:8080/api/v2/metrics"
