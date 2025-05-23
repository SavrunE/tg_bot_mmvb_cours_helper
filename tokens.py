import json

def load_token(bot_name: str) -> str:
    with open("tokens.json", 'r') as f:
        config = json.load(f)
    return config.get(bot_name)
