import threading
import time

from .agent import Agent
from .config import CHECK_IF_AGENT_ALIVE_TIME
from .mock_agent import MockAgent


def run_normal_agent():
    agent_thread = threading.Thread(target=Agent().run, daemon=True)
    agent_thread.start()

    while True:
        time.sleep(CHECK_IF_AGENT_ALIVE_TIME)
        if not agent_thread.is_alive():
            agent_thread = threading.Thread(target=Agent().run, daemon=True)
            agent_thread.start()


def run_mock_agent():
    agent = MockAgent()
    agent_thread = threading.Thread(target=agent.run, daemon=True)
    agent_thread.start()
