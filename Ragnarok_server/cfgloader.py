import json
import os
import os.path
def loadcfg():
    loader = open("config.json","r")
    return json.loads(loader.read())

if __name__ == "__main__":
    print (loadcfg())
