import os
import unicodedata
import re
import datetime


def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKC', value)
    value = re.sub(slugify.non_word_reg, '', value).strip().lower()
    value = re.sub(slugify.collapse_space_reg, '-', value)
    return value
slugify.non_word_reg = re.compile(r'[^\w\s-]')
slugify.collapse_space_reg = re.compile(r'[^\w\s-]')

def log_dir_for_server(server):
    return os.path.join(slugify(server.name))

def log_file_for_channel(channel):
    return os.path.join(log_dir_for_server(channel.server), slugify(channel.name))

def log_file_for_message(message):
    return log_file_for_channel(message.channel)

def ensure_file_exists(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

def format_message_for_log(message):
    return "{0} {1}: {2}".format(
        message.edited_timestamp or message.timestamp,
        user_nick_or_name(message.author),
        message.clean_content,
    )

def user_nick_or_name(user):
    if hasattr(user, 'nick'):
        return user.nick or user.name
    else:
        return user.name

def write_log(filepath, text, suppress_ts = False):
    with open(filepath, 'a', encoding='utf8') as log_file:
        log_file.write("{ts}{ts_space}{text}".format(
            ts = '' if suppress_ts else datetime.datetime.utcnow(),
            ts_space = '' if suppress_ts else ' ',
            text = text,
        ))
