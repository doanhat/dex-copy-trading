import pathlib
from dotenv import dotenv_values


def get_config():
    conf_path = pathlib.Path(__file__).parent / ".env.dev"
    return dotenv_values(conf_path)


config = get_config()
