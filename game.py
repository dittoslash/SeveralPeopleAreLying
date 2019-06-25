import asyncio

players = {}
matches = {}

# check if user is in a match


def player(message):
    if message.author.id in players.keys():
        return players[message.author.id]
    else:
        return False
# check if there is a match in that channel


def match(message):
    if message.channel.id in matches.keys():
        return matches[message.channel.id]
    else:
        return False


class Player:

    def __init__(self, user, match):
        self.user = user
        self.id = self.user.id
        self.match = match


class Match:

    def __init__(self, host, channel):
        self.host = Player(host, self)
        self.channel = channel
        self.players = []
        self.addPlayer(host)
        self.stage = "lobby"
        # self.settings = {
        #    "rounds": 0
        #}

    async def on_message(self, message, parsed):
        if parsed[0] == 'join' and self.stage == 'lobby':
            if player(message):
                await message.channel.send(f"You are already in a match (<#{players[message.author.id].channel.id}>)")
            elif match(message):
                matches[message.channel.id].addPlayer(message)
                await message.channel.send("Joined successfully.")
            else:
                await message.channel.send("There is already a match in this channel.")
        if message.author is self.host.user:
            if parsed[0] == 'start' and self.stage == 'lobby':
                self.stage = 'playing'
                self.round = 0

    async def lobby(self):
        self.stage = lobby

    def add_player(self, user):  # Use these instead of fucking with the players dict yourself.
        self.players.append(Player(user, self))
        players[user.id] = self

    def remove_player(self, user):  # Might not actually work. Probably will.
        self.players.remove(Player(user, self))
        del players[user.id]
