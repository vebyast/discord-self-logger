#!python

from distutils.core import setup

setup(
    name='discord-self-logger',
    version='0.1',
    description='Discord self-bot for logging, either in realtime or dumping history',
    author='Vebyast',
    author_email='vebyast@gmail.com',
    url='',
    packages=['vebyastdiscordlogger'],
    requires=['discord.py'],
    scripts=['discord-logger-bot.py', 'discord-log-dumper.py'],
)
