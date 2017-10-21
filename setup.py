#!python

from distutils.core import setup

setup(
    name='discord-self-logger',
    version='0.1',
    description='Discord self-bot that logs events',
    author='Vebyast',
    author_email='vebyast@gmail.com',
    url='',
    packages=[],
    requires=['discord.py'],
    scripts=['discord-logger-bot.py'],
)
