import getpass
import os

def _get_discord_auth_from_file():
    if os.path.exists('discord_token.txt'):
        with open('discord_token.txt', 'r') as token_file:
            tok = token_file.read().strip()
            if tok:
                return [tok]

def _get_discord_auth_from_env():
    if 'DISCORD_TOKEN' in os.environ:
        tok = os.environ['DISCORD_TOKEN']
        if tok:
            return [tok]

def _get_discord_auth_from_user():
    return [
        input("Discord account email: "),
        getpass.getpass(),
    ]

def get_discord_auth_args():
    return _get_discord_auth_from_env() \
        or _get_discord_auth_from_file() \
        or _get_discord_auth_from_user()

def _get_channel_id_from_file():
    if os.path.exists('discord_logs_channel.txt'):
        with open('discord_logs_channel.txt', 'r') as token_file:
            return token_file.read().strip()

def _get_channel_id_from_env():
    if 'DISCORD_TOKEN' in os.environ:
        tok = os.environ['DISCORD_LOGS_CHANNEL']
        return tok

def _get_channel_id_from_user():
    return input("Channel ID (right-click on channel): ")

def get_channel_id():
    return _get_channel_id_from_env() \
        or _get_channel_id_from_file() \
        or _get_channel_id_from_user()
