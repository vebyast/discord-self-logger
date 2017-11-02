import discord
import sys
import dateparser
import datetime
import pytz
import tzlocal
import vebyastdiscordlogger.logsaver as logsaver
import vebyastdiscordlogger.auth as discord_auth


client = discord.Client()

async def get_channel(channel_id):
    result = client.get_channel(channel_id)
    if not result:
        print("Could not find channel: {}".format(channel_id),
              file=sys.stderr)
        sys.exit(1)
    else:
        return result

def time_to_naive_utc(t_naive):
    localtz = tzlocal.get_localzone()
    t_local = localtz.localize(t_naive)
    t_utc_naive = t_local.astimezone(pytz.utc).replace(tzinfo=None)
    return t_utc_naive

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(client.user.discriminator)
    print('------')

    print('Collecting log dump information...')

    channel_id = discord_auth.get_channel_id()

    target_start_time = time_to_naive_utc(dateparser.parse(
        input('Date to get logs from (can be informal e.g. "June 9"): ')
    ))

    end_time_input = input('Date to get logs to (or blank for same day): ')
    if end_time_input:
        target_end_time = time_to_naive_utc(dateparser.parse(end_time_input))
    else:
        target_end_time = target_start_time + datetime.timedelta(1)

    print('Dumping logs...')

    channel = await get_channel(channel_id)

    log_filepath = logsaver.log_file_for_channel(channel)
    logsaver.ensure_file_exists(log_filepath)

    logsaver.write_log(
        filepath = log_filepath,
        text = "{block}\n{indent} Start of log dump {start_time}Z - {end_time}Z\n{block}\n".format(
            block = "=" * 80,
            indent = "=" * 4,
            start_time = target_start_time,
            end_time = target_end_time,
        ),
        suppress_ts = True,
    )

    num_logs = 0
    next_start_time = target_start_time
    done = False
    while not done:
        done = True
        async for log in client.logs_from(
                channel,
                limit=500,
                before=target_end_time,
                after=next_start_time,
                reverse=True):
            logsaver.write_log(
                filepath = log_filepath,
                text = logsaver.format_message_for_log(log) + "\n",
                suppress_ts = True,
            )
            done = False
            next_start_time = log.timestamp
            num_logs += 1

    print('Done!')
    print('Saved {n} to {path}'.format(
        path = log_filepath,
        n = num_logs,
    ))

    logsaver.write_log(
        filepath = log_filepath,
        text = "{block}\n{indent} End of log dump {start_time}Z - {end_time}Z\n{block}\n".format(
            block = "=" * 80,
            indent = "=" * 4,
            start_time = target_start_time,
            end_time = target_end_time,
        ),
        suppress_ts = True,
    )

    await client.logout()
    # sys.exit(0)

discord_auth_args = discord_auth.get_discord_auth_args()

client.run(*discord_auth_args, bot=False)
