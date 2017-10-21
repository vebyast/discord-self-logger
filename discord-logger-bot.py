import discord
import os
import datetime
import sys
import unicodedata
import re
import getpass

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

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(client.user.discriminator)
    print('------')

@client.event
async def on_message(message):
    # ignore private messages
    if not message.server:
        return

    # log everything else to the appropriate directory
    filepath = log_file_for_message(message)
    ensure_file_exists(filepath)

    with open(filepath, 'a') as log_file:
        log_file.write(format_message_for_log(message) + "\n")

@client.event
async def on_message_edit(message_before, message):
    # ignore private messages
    if not message.server:
        return

    # log everything else to the appropriate directory
    filepath = log_file_for_message(message)
    ensure_file_exists(filepath)

    with open(filepath, 'a') as log_file:
        log_file.write("{0} Message edited:\n    {m_before}\n    {m_after}\n".format(
            datetime.datetime.utcnow(),
            m_before = format_message_for_log(message_before),
            m_after = format_message_for_log(message),
        ))

@client.event
async def on_message_delete(message):
    # ignore private messages
    if not message.server:
        return

    # log everything else to the appropriate directory
    filepath = log_file_for_message(message)
    ensure_file_exists(filepath)

    with open(filepath, 'a') as log_file:
        log_file.write("{0} Message deleted:\n    {m}\n".format(
            datetime.datetime.utcnow(),
            m = format_message_for_log(message)
        ))

@client.event
async def on_reaction_add(reaction, user):
    # ignore private messages
    if not reaction.message.server:
        return

    # log everything else to the appropriate directory
    filepath = log_file_for_message(reaction.message)
    ensure_file_exists(filepath)
    with open(filepath, 'a') as log_file:
        log_file.write("{ts} {u} added reaction: {r}\n    {m}\n".format(
            ts = datetime.datetime.utcnow(),
            r = str(reaction.emoji),
            u = user_nick_or_name(user),
            m = format_message_for_log(reaction.message),
        ))

@client.event
async def on_reaction_remove(reaction, user):
    # ignore private messages
    if not reaction.message.server:
        return

    # log everything else to the appropriate directory
    filepath = log_file_for_message(reaction.message)
    ensure_file_exists(filepath)
    with open(filepath, 'a') as log_file:
        log_file.write("{ts} {u} removed reaction: {r}\n    {m}\n".format(
            ts = datetime.datetime.utcnow(),
            r = str(reaction.emoji),
            u = user_nick_or_name(user),
            m = format_message_for_log(reaction.message),
        ))


@client.event
async def on_member_update(member_before, member):
    # ignore private messages
    if not member.server:
        return

    def log_on_all_channels(text):
        # log everything else to the appropriate directory
        for channel in member.server.channels:
            filepath = log_file_for_channel(channel)
            ensure_file_exists(filepath)
            with open(filepath, 'a') as log_file:
                log_file.write(text)

    if member.nick and not member_before.nick:
        log_on_all_channels("{ts} {u} got a nick: '{after}'\n".format(
            ts = datetime.datetime.utcnow(),
            u = member.name,
            after = member.nick,
        ))
    elif member_before.nick and not member.nick:
        log_on_all_channels("{ts} {u} cleared their nick (was '{before}')\n".format(
            ts = datetime.datetime.utcnow(),
            u = member.name,
            before = member_before.nick,
        ))
    elif member.nick != member_before.nick:
        log_on_all_channels("{ts} {u} changed nick from '{before}' to '{after}'\n".format(
            ts = datetime.datetime.utcnow(),
            u = member.name,
            before = member_before.nick,
            after = member.nick
        ))

    new_roles = set(member.roles) - set(member_before.roles)
    old_roles = set(member_before.roles) - set(member.roles)
    if new_roles:
        log_on_all_channels("{ts} {u} was given roles: {r}\n".format(
            ts = datetime.datetime.utcnow(),
            u = member.nick or member.name,
            r = ', '.join(str(r) for r in new_roles),
        ))

    if old_roles:
        log_on_all_channels("{ts} {u} lost roles: {r}\n".format(
            ts = datetime.datetime.utcnow(),
            u = member.nick or member.name,
            r = ', '.join(str(r) for r in old_roles),
        ))

    # if member.status != member_before.status:
    #     log_on_all_channels("{ts} {u} changed status from '{before}' to '{after}'\n".format(
    #         ts = datetime.datetime.utcnow(),
    #         u = member.name,
    #         before = member_before.status,
    #         after = member.status,
    #     ))


discord_token = None
discord_uname = None
discord_pass = None

if 'DISCORD_TOKEN' in os.environ:
    discord_token = os.environ['DISCORD_TOKEN']

if os.path.exists('discord_token.txt'):
    with open('discord_token.txt', 'r') as token_file:
        discord_token = token_file.read().strip()

if not discord_token:
    discord_uname = input("Discord account email: ")
    discord_pass = getpass.getpass()

if not discord_token and not (discord_uname and discord_pass):
    print('Need to set the discord token. This can be done with the DISCORD_TOKEN environment variable, by creating a file "discord_token.txt", or by typing in your username and password when prompted.', file=sys.stderr)
    sys.exit(-1)

if discord_token:
    client.run(discord_token, bot=False)
else:
    client.run(discord_uname, discord_pass, bot=False)
