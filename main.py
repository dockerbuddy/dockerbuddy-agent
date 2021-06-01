"""
Agent setup.
"""
import threading
from agent import Agent

if __name__ == "__main__":
    agent = Agent()
    threading.Thread(target=agent.run, daemon=True).start()
    while True:
        pass




