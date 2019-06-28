import asyncio
import util
import random

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

# find player from the id instead of the message
def find_player_from_id(identifier):
    if identifier in players.keys():
        for p in players[identifier].players:
            if p.id == identifier:
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
        self.responses = {}
        self.already_done_questions = []
        self.settings = {
            "rounds": 5,
            "response_time": 120,
            "voting_time": 30
        }

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
                self.round = 0
                await util.respond(message, True)
                await self.submit()
            if parsed[0] == 'set' and self.stage == 'lobby':
                try:
                    if len(parsed) >= 2:
                        if parsed[1] in self.settings.keys():
                            if len(parsed) >= 3:
                                self.settings[parsed[1]] = int(parsed[2])
                                await util.respond(message, True)
                            else: await message.channel.send("Need a value.")
                        else: await message.channel.send("Unknown setting.")
                    else: await message.channel.send("Valid settings are `rounds`, `response_time`, and `voting_time`.")
                except ValueError: await message.channel.send("Not a number.")

    async def on_dm(self, message, parsed):
        if self.stage == "submit":
            self.responses[find_player(message).user.id] = message.content
            await util.respond(message, True)
        else:
            await message.channel.send("The match is not currently accepting submissions.")

    async def submit(self):
        self.stage = 'submit'
        self.round += 1
        self.responses = {}
        questions = util.load_questions()
        question = {'prompt':None}
        while question['prompt'] in self.already_done_questions or question['prompt'] is None:
            question = random.choice(questions)
            
        self.already_done_questions.append(question['prompt'])
        self.term = question['prompt']
        self.definition = question['answer']

        await self.channel.send(f'**Round {self.round}** has started! Check your DMs!')

        for player in self.players:
            await player.user.send(f'Write a fake definition for: \n\n**{self.term}** \n\nYou have {self.settings["response_time"]} seconds.')

        await asyncio.sleep(self.settings["response_time"])

        await self.voting()

    async def voting(self):
        self.stage = 'voting'
        await self.channel.send(f'**Round {self.round} Voting** has started! React to the correct definition for **{self.term}**!')
        # Raine stuff

        responses = list(self.responses.items())
        responses.append((None,self.definition))
        responses = random.sample(responses, len(responses))
        voting_messages = {}
            
        for player_id, definition in responses:
            msg = await self.channel.send(f'```{definition}```')
            await msg.add_reaction("✅")
            voting_messages[player_id] = msg
            await asyncio.sleep(1.5)
            
        await asyncio.sleep(self.settings["voting_time"])
        
        points_message = []
        
        correct_definition = [response for response in responses if response[0] is None][0][1]
        points_message.append(f'**Round {self.round} Voting** has finished! This was the correct definition: ```{correct_definition}``` ')
        
        for player_id, message in voting_messages.items():
            message = await self.channel.fetch_message(message.id)
            reaction = [r for r in message.reactions if r.emoji == "✅" ][0]
            voters = []
            async for user in reaction.users():
                if user.bot or user.id == player_id or not find_player_from_id(user.id):
                    continue
                voters.append(find_player_from_id(user.id))
            
            if len(voters) < 1:
                continue
            
            if player_id is None: # if the player is None then we have the correct message
                points_message.append('')
                for voter in voters[:-1]:   
                    points_message[-1] += f'{voter.user.mention}, ' # nice formatting
                    voter.points += 2
                points_message[-1] += f'{voters[-1].user.mention} ' # the last user mentioned doesn't need a comma
                voters[-1].points += 2
                points_message[-1] += ' received 2 points for choosing the correct definition'
            else:
                points_message.append(f'{find_player_from_id(player_id).user.mention} got {len(voters)} points by fooling ')
                find_player_from_id(player_id).points += len(voters)
                for voter in voters[:-1]:   
                    points_message[-1] += f'{voter.user.mention}, ' # nice formatting
                points_message[-1] += f'{voters[-1].user.mention} into thinking their definition was the correct one' # the last user mentioned doesn't need a comma
        
        points_message.append('\n Current Ranking:')
            
        sorted_players = sorted(self.players, key=lambda player: player.points, reverse=True)
        
        for i, player in enumerate(sorted_players, 1):
            points_message.append(f'#{i} - {player.user.mention} - {player.points} points')
            
        points_message = '\n'.join(points_message)
        await self.channel.send(points_message)
        
        await asyncio.sleep(10)
                
        if self.round >= self.settings["rounds"]:
            top = self.players[0]
            for p in self.players:
                if p.points > top.points:
                    top = p
            await self.channel.send(f'{top.user.mention} wins, with {top.points} points!')

            for p in self.players:
                self.remove_player(p.user)
                del matches[self.channel.id]
                print(matches, players)
        else:
            await self.submit()

    def add_player(self, user):  # Use these instead of fucking with the players dict yourself.
        self.players.append(Player(user, self))
        players[user.id] = self

    def remove_player(self, user):  # Might not actually work. Probably will.
        self.players.remove(find_player_from_id(user.id))
        del players[user.id]
