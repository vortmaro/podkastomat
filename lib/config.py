import json

def load():
    try:
        configFile = open('config.json', 'r', encoding='utf-8')
        config = json.load(configFile)
        configFile.close()
    except:
        config = {
            'translate': [],
            'podcasts': [],
        }
    return config

def save(configData):
    configFile = open('config.json', 'w', encoding='utf-8')
    json.dump(configData, configFile, indent=4)
    configFile.write('\n')
    configFile.close()
