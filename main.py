"""
Agent setup.
"""
import yaml

HOST = None
BUCKET = None
ORG = None
TOKEN = None

if __name__ == "__main__":
    with open('config.yaml', 'r') as config:
        cfg = yaml.load(config, Loader=yaml.BaseLoader)

    print(cfg['hostUrl'])
