import json
from json import JSONDecodeError


def save(show_func):
    def wrapper(*args, **kwargs):
        try:
            ind = show_func.__name__.split('_')[1]
            with open("trading/display/tmp_config.json", "r") as fp:
                config = json.load(fp)["config"]
            if args[0].state.currency not in config:
                config[args[0].state.currency] = [ind]
            elif ind not in config[args[0].state.currency]:
                config[args[0].state.currency].append(ind)
            else: 
                return
            with open("trading/display/tmp_config.json", "w") as fp:
                json.dump({"config": config}, fp)
            return show_func(*args[:1], **kwargs)
        except (IOError, JSONDecodeError):
            with open("trading/display/tmp_config.json", "w") as fp:
                config = {args[0].state.currency: [ind]}
                json.dump({"config": config}, fp)
                return show_func(*args[:1], **kwargs)
    return wrapper
