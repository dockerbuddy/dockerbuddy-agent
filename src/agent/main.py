import threading

from .agent import Agent
from .mock_agent import MockAgent


def run_normal_agent():
    agent = Agent()
    agent_thread = threading.Thread(target=agent.run, daemon=True)
    agent_thread.start()


def run_mock_agent():
    agent = MockAgent()
    agent_thread = threading.Thread(target=agent.run, daemon=True)
    agent_thread.start()
