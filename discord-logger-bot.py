import discord
import vebyastdiscordlogger.logsaver as logsaver
import vebyastdiscordlogger.auth as discord_auth


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
    filepath = logsaver.log_file_for_message(message)
    logsaver.ensure_file_exists(filepath)
    logsaver.write_log(filepath, logsaver.format_message_for_log(message) + "\n", suppress_ts = True)

@client.event
async def on_message_edit(message_before, message):
    # ignore private messages
    if not message.server:
        return

    # log everything else to the appropriate directory
    filepath = logsaver.log_file_for_message(message)
    logsaver.ensure_file_exists(filepath)

    logsaver.write_log(filepath, "Message edited:\n    {m_before}\n    {m_after}\n".format(
        m_before = logsaver.format_message_for_log(message_before),
        m_after = logsaver.format_message_for_log(message),
    ))

@client.event
async def on_message_delete(message):
    # ignore private messages
    if not message.server:
        return

    # log everything else to the appropriate directory
    filepath = logsaver.log_file_for_message(message)
    logsaver.ensure_file_exists(filepath)

    logsaver.write_log(filepath, "Message deleted:\n    {m}\n".format(
        m = logsaver.format_message_for_log(message)
    ))

@client.event
async def on_reaction_add(reaction, user):
    # ignore private messages
    if not reaction.message.server:
        return

    # log everything else to the appropriate directory
    filepath = logsaver.log_file_for_message(reaction.message)
    logsaver.ensure_file_exists(filepath)
    logsaver.write_log(filepath, "{u} added reaction: {r}\n    {m}\n".format(
        r = str(reaction.emoji),
        u = logsaver.user_nick_or_name(user),
        m = logsaver.format_message_for_log(reaction.message),
    ))

@client.event
async def on_reaction_remove(reaction, user):
    # ignore private messages
    if not reaction.message.server:
        return

    # log everything else to the appropriate directory
    filepath = logsaver.log_file_for_message(reaction.message)
    logsaver.ensure_file_exists(filepath)
    logsaver.write_log(filepath, "{u} removed reaction: {r}\n    {m}\n".format(
        r = str(reaction.emoji),
        u = logsaver.user_nick_or_name(user),
        m = logsaver.format_message_for_log(reaction.message),
    ))


@client.event
async def on_member_update(member_before, member):
    # ignore private messages
    if not member.server:
        return

    def log_on_all_channels(text):
        # log everything else to the appropriate directory
        for channel in member.server.channels:
            filepath = logsaver.log_file_for_channel(channel)
            logsaver.ensure_file_exists(filepath)
            logsaver.write_log(filepath, text)

    if member.nick and not member_before.nick:
        log_on_all_channels("{u} got a nick: '{after}'\n".format(
            u = member.name,
            after = member.nick,
        ))
    elif member_before.nick and not member.nick:
        log_on_all_channels("{u} cleared their nick (was '{before}')\n".format(
            u = member.name,
            before = member_before.nick,
        ))
    elif member.nick != member_before.nick:
        log_on_all_channels("{u} changed nick from '{before}' to '{after}'\n".format(
            u = member.name,
            before = member_before.nick,
            after = member.nick
        ))

    new_roles = set(member.roles) - set(member_before.roles)
    old_roles = set(member_before.roles) - set(member.roles)
    if new_roles:
        log_on_all_channels("{u} was given roles: {r}\n".format(
            u = logsaver.user_nick_or_name(member),
            r = ', '.join(str(r) for r in new_roles),
        ))

    if old_roles:
        log_on_all_channels("{u} lost roles: {r}\n".format(
            u = logsaver.user_nick_or_name(member),
            r = ', '.join(str(r) for r in old_roles),
        ))

    # if member.status != member_before.status:
    #     log_on_all_channels("{u} changed status from '{before}' to '{after}'\n".format(
    #         u = member.name,
    #         before = member_before.status,
    #         after = member.status,
    #     ))


discord_auth_args = discord_auth.get_discord_auth_args()

client.run(*discord_auth_args, bot=False)
