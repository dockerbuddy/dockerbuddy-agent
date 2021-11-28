import threading
import time

from .agent import Agent
from .config import CHECK_IF_AGENT_ALIVE_TIME


def run_normal_agent():
    agent_thread = threading.Thread(target=Agent().run, daemon=True)
    agent_thread.start()

    while True:
        time.sleep(CHECK_IF_AGENT_ALIVE_TIME)
        if not agent_thread.is_alive():
            agent_thread = threading.Thread(target=Agent().run, daemon=True)
            agent_thread.start()
