import asyncio

players = []
matches = []


def Player():

    def __init__(self, user, match):
        self.user = user
        self.id = self.user.id
        self.match = match


def Match():

    def __init__(self, host, channel):
        self.host = Player(host, self)
        self.channel = channel
        self.players = [self.host]
        self.stage = None

    async def on_message(self, message, parsed):

        if message.author is self.host.user:

            if self.stage == 'lobby':

                if parsed[0] == 'start':
                    self.stage = 'playing'
                    self.round = 0

    async def lobby(self):
        self.stage = lobby
