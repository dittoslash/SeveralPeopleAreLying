import discord
import util


# settings constants
tokens = util.load_tokens()
client = discord.Client()


@client.event
async def on_ready():
    print('----------------')
    print(f'Logged in as {client.user.name}')
    print('----------------')


@client.event
async def on_message(message):
    pass  # main interaction here

# main loop
client.run(tokens['token'])
