import discord
from discord import DMChannel

import util
import game


# settings constants
tokens = util.load_config()
pre = tokens['prefix']  # fast access of the prefix
client = discord.Client()


@client.event
async def on_ready():
    print('----------------')
    print(f'Logged in as {client.user.name}')
    print('----------------')

    matches = []
    game.matches = []  # so we can also have access to the matches there

    players = []
    game.players = []


@client.event
async def on_message(message):
    parsed = [util.parse_message(message.content)]

    # check if user is in a match
    def player(message): return m

    if type(message.channel) is DMChannel:  # DMChannels will have different commands
        pass
    else:
        if parsed[0] == 'new':
            match = 'something'  # start a new match
            matches.append(match)

# main loop
client.run(tokens['token'])
