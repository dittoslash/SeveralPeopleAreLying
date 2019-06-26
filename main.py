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

    game.matches = {} # channel id > match instance
    game.players = {} # dunno what this was supposed to be so i'm repurposing it. maps user id > player instance


@client.event
async def on_message(message):
    parsed = util.parse_message(message.content)
    if not parsed: return

    if type(message) is DMChannel:  # DMChannels will have different commands
        if game.player(message):
            pass # probably call something on the relevant match instance
        else:
            await message.chnanel.send("You are not in a match.")
    else:
        if game.match(message): 
            await game.match(message).on_message(message, parsed) # defer message parsing to the relevant match instance

        if parsed[0] == 'new':
            if game.player(message):
                await message.channel.send(f"You are already in a match (<#{game.players[message.author.id].channel.id}>)")
            elif not game.match(message):
                match = game.Match(message.author, message.channel) # start a new match
                game.matches[message.channel.id] = match
                await message.channel.send("Match created.")
            else:
                await message.channel.send("There is already a match in this channel.")

# main loop
client.run(tokens['token'])
