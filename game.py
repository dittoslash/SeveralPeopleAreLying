import asyncio
import util

players = {}
matches = {}

# check if user is in a match
def find_player_match(message):
    if message.author.id in players.keys():
        return players[message.author.id]
    else:
        return False

# check if there is a match in that channel
def find_match(message):
    if message.channel.id in matches.keys():
        return matches[message.channel.id]
    else:
        return False

# get the player instance representing a player
def find_player(message):
    if message.author.id in players.keys():
        for p in players[message.author.id].players:
            if p.id == message.author.id:
                return p
    return False

class Player:
    def __init__(self, user, match):
        self.user = user
        self.id = self.user.id
        self.match = match
        self.points = 0

class Match:
    def __init__(self, host, channel):
        self.host = Player(host, self)
        self.channel = channel
        self.players = []
        self.stage = "lobby"
        self.responses = []
        # self.settings = {
        #    "rounds": 0
        #}

        self.add_player(host)

    async def on_message(self, message, parsed):
        if parsed[0] == 'join' and self.stage == 'lobby':
            if find_player_match(message):
                await message.channel.send(f"You are already in a match (<#{players[message.author.id].channel.id}>)")
            else:
                self.add_player(message.author)
                await util.respond(message, True)
        if parsed[0] == 'leave' and self.stage == 'lobby':
            if find_player_match(message):
                self.remove_player(message.author)
                await util.respond(message, True)
            else:
                await message.channel.send("You are not in this match.")
        if message.author is self.host.user:
            if parsed[0] == 'start' and self.stage == 'lobby':
                self.stage = 'submit'
                self.round = 0
                await util.respond(message, True)

    async def on_dm(self, message, parsed):
        if self.stage == "submit":
            self.responses[self.players.index(player(message))] = message.content
            await util.respond(message, True)
        else:
            await message.channel.send("The match is not currently accepting submissions.")

    async def lobby(self):
        self.stage = "lobby"

    def add_player(self, user):  # Use these instead of fucking with the players dict yourself.
        self.players.append(Player(user, self))
        self.responses.append('')
        players[user.id] = self

    def remove_player(self, user):  # Might not actually work. Probably will.
        self.players.remove(Player(user, self))
        del players[user.id]
