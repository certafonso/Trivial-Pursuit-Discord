import discord
import asyncio
import wikipedia
import random

import Board

class Game():
	"""Implements the game nPeopleAreLying"""
	def __init__(self, channel, players):

		self.Channel = channel
		self.Players = players
		self.PlayerTurn = 1
		self.GameStage = 0
		self.Board = Board.Board("./4 Categories Board.json", len(players)-1)
		# Game Stages:
		# 0 - Roll dice
		# 1 - Choose Direction
		# 2 - Choose category
		# 3 - answer question

		self.Board.StartGraphics()
		print("Game Started")

	async def on_message(self, message):
		"""Will handle messages for the game nPeopleAreLying"""

		command = message.content.split(" ")

		if self.GameStage == 0:     # Stage 0 - Roll dice
			if command[0] == "-roll" and self.Players[self.PlayerTurn] == message.author:
				self.steps = random.randint(1, 6)

				await self.Channel.send(f"You rolled a {self.steps}!")

				await self.move(self.steps)
					
		elif self.GameStage == 1:   # Stage 1 - Choose Direction
			if command[0] == "-go" and self.Players[self.PlayerTurn] == message.author:
				await self.move(self.steps, command[1])

		elif self.GameStage == 3:   # Stage 3 - answer question
			if command[0] == "-accept" and self.Players[0] == message.author:
				if self.Board.GiveCheese(self.PlayerTurn):	# won cheese
					await self.Channel.send(f"Great! You won a cheese.")

				self.GameStage = 0
				mention = self.Players[self.PlayerTurn].mention
				await self.Channel.send(f"Great! {mention} you get to go again. \nRoll by typing ``-roll`` in chat.")

			elif command[0] == "-reject" and self.Players[0] == message.author:
				self.GameStage = 0
				self.PlayerTurn += 1
				if self.PlayerTurn >= len(self.Players):
					self.PlayerTurn = 1

				mention = self.Players[self.PlayerTurn].mention
				await self.Channel.send(f"Too bad! {mention} it's your turn. \nRoll by typing ``-roll`` in chat.")

	async def move(self, steps, direction = -1):
		""" Moves the player """

		try:
			self.Board.MovePlayer(self.PlayerTurn, steps, int(direction))
			await self.get_question()

		except Board.DecisionNeeded as decision:
			position = self.Board.players[self.PlayerTurn]["Position"]
			self.GameStage = 1
			self.steps = decision.steps
			await self.Channel.send(f"You are in {position} choose one of the following directions: {decision.options}. \nChoose by typing ``-go [option]`` in chat.")
		
		except ValueError:
			await self.Channel.send(f"{direction} is not a number. Try again.")

	async def get_question(self):
		""" Gets a question for the player """

		try:
			await self.Channel.send(f"Your question: {self.Board.GetQuestionForPlayer(self.PlayerTurn)}")
			self.GameStage = 3
		except Board.QuestionError as e:
			self.Board.RenewQuestions(e.category)
			await self.Channel.send(f"All questions from {e.category} were used, will now be repeated.")
			await self.get_question()




