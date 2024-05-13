from discordwebhook import Discord

from src.conf.config import config


def send_discord_message(msg) -> None:
    discord = Discord(url=config["DISCORD_WEBHOOK"])
    discord.post(content=msg)
