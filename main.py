"""
Agent setup.
"""
import threading
import time
from agent import Agent

CHECK_AGENT_INTERVAL_TIME = 5

if __name__ == "__main__":
    agent = Agent()
    agent_thread = threading.Thread(target=agent.run, daemon=True)
    agent_thread.start()

    while True:
        time.sleep(CHECK_AGENT_INTERVAL_TIME)
        if not agent_thread.is_alive():
            agent = Agent()
            agent_thread = threading.Thread(target=agent.run, daemon=True)
            agent_thread.start()




