"""
Agent setup.
"""
import threading
import time
from agent import Agent
from mock_agent import MockAgent

CHECK_AGENT_INTERVAL_TIME = 5


def run_agent(agent_constructor):
    agent = agent_constructor
    agent_thread = threading.Thread(target=agent.run, daemon=True)
    agent_thread.start()

    while True:
        time.sleep(CHECK_AGENT_INTERVAL_TIME)
        if not agent_thread.is_alive():
            agent = agent_constructor
            agent_thread = threading.Thread(target=agent.run, daemon=True)
            agent_thread.start()


if __name__ == "__main__":
    mode = input("Select mode [normal | mock]: ")

    if mode == "normal":
        run_agent(Agent())
    elif mode == "mock":
        run_agent(MockAgent())
    else:
        print("Invalid command")








