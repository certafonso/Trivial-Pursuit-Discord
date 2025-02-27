# external libraries
import discord
import asyncio
from dotenv import load_dotenv
import os
import time
import random

# project modules
import Player
import Trivial

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.running_games = {}

        # self.bg_task = self.loop.create_task(self.check_clock())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_guild_join(self, guild):
        print("Entered")
        print(guild.name)
        
        # channel = guild.system_channel
        
        # await channel.send("To start The Wikipedia Game someone must type `-wikigames` in the channel where you want the game to take place.")

    async def on_message(self, message):
        """Handles messages"""

        if message.author == client.user:
            return

        if type(message.channel) == discord.DMChannel:  # received a dm
            channel, message.author = self.user_ingame(message.author)
            if channel != None:
                await self.running_games[channel]["Game"].on_message(message)

        else:
            if message.content == "-wikigames":             # command to start a game
                await self.start_game(message.channel, message.author)           
            elif str(message.channel.id) in self.running_games:  # there's a game running in the channel
                # Commands that will always work 
                if message.content == "-join":          
                    await self.join_player(message.channel, message.author)
                elif message.content == "-leave":
                    await self.leave_player(message.channel, message.author)
                elif message.content == "-list":      
                    await self.display_players(message.channel)
                elif message.content == "-quit":
                    await self.end_game(message.channel)
                elif message.content == "-help":
                    await self.help(message.channel)
                
                else:
                    if self.running_games[str(message.channel.id)]["WaitingPlayers"]:   # Will only work if the game didn't start
                        if message.content.split(" ")[0] == "-play":
                            if self.running_games[str(message.channel.id)]["GameMaster"] == message.author:
                                # only the gamemaster can start the game
                                await self.play_game(message.channel)
                            else:
                                await message.channel.send("You're not the GameMaster")
                    else:   # message will be handled by the game
                        await self.running_games[str(message.channel.id)]["Game"].on_message(message)

    def user_ingame(self, user):
        """Checks if a user is participating in any game"""

        for channel in self.running_games.keys():
            for player in self.running_games[channel]["Players"]:
                if user.id == player.id:
                    return channel, player
        return None, None

    async def start_game(self, channel, GameMaster):
        """Starts a game in a channel"""

        if str(channel.id) in self.running_games:    #there's already a game running
            await channel.send("There is already a game running in this channel.")
        else:
            GameMaster = Player.Player(GameMaster)
            
            self.running_games.update(
                {str(channel.id): {
                    "GameMaster" : GameMaster,
                    "WaitingPlayers" : True,
                    "Players" : [GameMaster],
                    "Game" : None
                }
            })
            await channel.send("Welcome to the Trivial Discord. To join the game type `-join`.")

    async def join_player(self, channel, player):
        """Adds a player to a game"""

        for i in range(0, len(self.running_games[str(channel.id)]["Players"])):
            if self.running_games[str(channel.id)]["Players"][i] == player:    # player already in the game
                await channel.send(f"You're already in the game.")
                return

        if self.running_games[str(channel.id)]["WaitingPlayers"]:   # the game didn't start, add to the player list
            await channel.send(f"Welcome to the Trivial Discord {player.mention}.")
            self.running_games[str(channel.id)]["Players"].append(Player.Player(player))
            await self.display_players(channel)
        else:
            await channel.send("There is a game running, you have to wait for it to end.")

    async def leave_player(self, channel, player):
        """Removes a player from a game"""

        if self.running_games[str(channel.id)]["GameMaster"] == player: # the player is the gamemaster so the game ends
            await channel.send(f"The game will now end because the GameMaster hates fun.")
            self.running_games.pop(str(channel.id))

        else:
            if player in self.running_games[str(channel.id)]["Players"]:
                self.running_games[str(channel.id)]["Players"].remove(player)
            await channel.send(f"Bye {player.mention}")

    async def display_players(self, channel):
        """Displays a list of all players"""

        message = ""

        if len(self.running_games[str(channel.id)]["Players"]) != 0:
            message += "Player list:\n"
            for player in self.running_games[str(channel.id)]["Players"]:
                message += f"{player.mention} ({player.points} points)\n"
            
            message += "Type `-join` to join the game or `-leave` to leave the game."

        else:
            message += "No one is playing :("

        await channel.send(message)

    async def play_game(self, channel):
        """ Enters the game """

        self.running_games[str(channel.id)]["WaitingPlayers"] = False
        self.running_games[str(channel.id)]["Game"] = Trivial.Game(channel, self.running_games[str(channel.id)]["Players"])

        return
        
    async def end_game(self, channel):
        """Ends a game"""

        self.running_games[str(channel.id)]["Game"] = None
        self.running_games[str(channel.id)]["WaitingPlayers"] = True

        await channel.send("GoodBye")

    async def help(self, channel):
        """Displays a help menu"""

        if str(channel.id) not in self.running_games:               # not in game
            await channel.send("To start a game you have to type `-wikigames` in the channel you want to use, the person who does this will be the gamemaster and will control various aspects of the game, then everyone who wants to play has to type `-join`.")
        
        elif self.running_games[str(channel.id)]["WaitingPlayers"]: # waiting players
            await channel.send("Everyone that wants to play has to type `-join`.\nThere are two games available: nPeopleAreLying (minimum of 3 players) and WikiAgainstHumanity (minimum of 3 players). To play a game, the gamemaster needs to type `-play [game name]` in chat.")
        
        else:                                                       # in game
            await self.running_games[str(channel.id)]["Game"].help()

if __name__ == "__main__":

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    client = Client()
    client.run(TOKEN)