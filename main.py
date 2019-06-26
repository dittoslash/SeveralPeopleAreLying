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

    game.matches = {}  # channel id > match instance
    game.players = {}  # dunno what this was supposed to be so i'm repurposing it. maps user id > player instance


@client.event
async def on_message(message):
    parsed = util.parse_message(message.content)

    if message.author.bot:  # we don't want it to respond to itself or other bots
        return

    if type(message.channel) is DMChannel:  # DMChannels will have different commands
        if game.find_player_match(message):
            await game.find_player_match(message).on_dm(message, parsed)  # defer message parsing to the relevant match instance
        else:
            await message.channel.send("You are not in a match.")
    else:  # we are in a TextChannel here
        if not parsed:  # we aren't interested in messages without the prefix here
            return

        if game.find_match(message):
            await game.find_match(message).on_message(message, parsed)  # defer message parsing to the relevant match instance

        if parsed[0] == 'new':
            if game.find_player_match(message):
                await message.channel.send(f"You are already in a match (<#{game.players[message.author.id].channel.id}>)")
            elif not game.find_match(message):
                match = game.Match(message.author, message.channel)  # start a new match
                game.matches[message.channel.id] = match
                start_message = await message.channel.send(f"{message.author.mention} has created a match! \nType {pre}join to join!")
            else:
                await message.channel.send("There is already a match in this channel.")

# main loop
client.run(tokens['token'])
