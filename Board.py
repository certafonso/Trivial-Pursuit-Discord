import json
from random import shuffle, randint

class Board():
	def __init__(self, board_file, n_players):

		with open(board_file, "r") as json_file:
			board_config = json.load(json_file)

		self.Categories = board_config["Categories"]

		self.Questions = board_config["Questions"]

		self.Nodes = board_config["Nodes"]

		self.players = [{"Position": 0, "Cheeses": [], "Hue": randint(0, 360)} for i in range(n_players)]

		self.Validate()

		self.SelectedQuestions = {}

		for category in self.Categories:
			self.RenewQuestions(category)

			print(self.Questions[category])

		self.Graphics = board_config["Graphics"]

		self.HTML = None

	def Validate(self):
		""" Tests if everything was imported properly """

		for category in self.Categories:	# check if every category has questions
			try:
				if len(self.Questions[category]) <= 1:
					raise KeyError
			except KeyError:
				raise ConfigFileError(f"The category {category} doesn't have any questions")

		for i in range(len(self.Nodes)):
			category = self.Nodes[i]["Category"]
			if category not in self.Categories:
				raise ConfigFileError(f"Node {i} has the category {category}, that doesn't exist")

			for connection in self.Nodes[i]["Adj"]:
				if connection > len(self.Nodes):
					raise ConfigFileError(f"Node {i} is adjacent to node {connection}, that doesn't exist")

	def MovePlayer(self, player_index, steps, direction, previous = -1):
		""" Moves a player a certain amount of steps in a direction of the board """

		if steps < 1: return

		curr_pos = self.players[player_index]["Position"]

		options = self.Nodes[self.players[player_index]["Position"]]["Adj"].copy()

		if previous != -1:
			options.remove(previous)

		if len(options) > 1 and direction == -1:	# decision needed
			raise DecisionNeeded(options, steps, "Choice needed")

		if len(options) == 1:
			self.players[player_index]["Position"] = options[0]
		elif direction not in options:
			raise DecisionNeeded(options, steps, f"Choice needed, {direction} was not an option")
		else:
			self.players[player_index]["Position"] = direction

		print(f"Was {curr_pos} moved to ", self.players[player_index]["Position"])

		self.UpdateGraphics()

		self.MovePlayer(player_index, steps-1, -1, curr_pos)
	
	def GetQuestion(self, category):
		""" Returns a question from a category """

		if self.SelectedQuestions[category] >= len(self.Questions[category]):
			raise QuestionError(f"All questions from {category} where used", category)

		question = self.Questions[category][self.SelectedQuestions[category]]

		self.SelectedQuestions[category] += 1

		return question

	def GetQuestionForPlayer(self, player_index):
		""" Returns a question from the category of the node the player is in """

		category = self.Nodes[self.players[player_index]["Position"]]["Category"]

		return self.GetQuestion(category)

	def RenewQuestions(self, category):
		""" Puts every question of a category back in game """

		self.SelectedQuestions[category] = 0
			
		shuffle(self.Questions[category])

	def GiveCheese(self, player_index, category = None):
		""" Gives a cheese from a certain category to a player """

		if category == None:	# category not specified
			if self.Nodes[self.players[player_index]["Position"]]["CategoryHub"]:
				category = self.Nodes[self.players[player_index]["Position"]]["Category"]
			
			else: return False	# not in category hub

		if category not in self.players[player_index]["Cheeses"]:	# check if player already has the cheese
			self.players[player_index]["Cheeses"].append(category)
			self.UpdateGraphics()
			return True
		else: return False

	def CheckWin(self, player_index):
		""" Checks if a player has won """

		if len(self.players[player_index]["Cheeses"]) == len(self.Categories):
			return True

		return False

	def StartGraphics(self):
		""" Loads the HTML template needed for the graphic component """

		# check if graphics weren't already started
		if self.HTML == None:

			# load Board template
			with open("./Graphics/Board_Template.html", "r") as f:
				self.HTML = f.read()

			# add board to the html
			self.HTML = self.HTML.format(Board=self.Graphics["Board"], Players="{Players}")

			self.UpdateGraphics()

	def UpdateGraphics(self):
		""" Updates the graphics of the game """

		# check if there are graphics started
		if self.HTML != None:
			Players = ""

			for player in self.players:
				# get position of player
				print((self.Nodes[player["Position"]]["Square"][0][0], self.Nodes[player["Position"]]["Square"][0][1]))
				print((self.Nodes[player["Position"]]["Square"][1][0], self.Nodes[player["Position"]]["Square"][1][1]))
				posx = randint(self.Nodes[player["Position"]]["Square"][0][0], self.Nodes[player["Position"]]["Square"][0][1]-50)
				posy = randint(self.Nodes[player["Position"]]["Square"][1][0], self.Nodes[player["Position"]]["Square"][1][1]-50)

				# add player image
				Players += self.Graphics["Player"].format(x=posx, y=posy, Hue=player["Hue"])

				# add cheeses
				for cheese in player["Cheeses"]:
					Players += self.Graphics[cheese].format(x=posx, y=posy)

			out = self.HTML.format(Players=Players)

			# write to the html file
			with open("./Trivial.html", "w") as f:
				f.write(out)

class ConfigFileError(Exception):
	def __init__(self, message):
		super().__init__(message)

class QuestionError(Exception):
	def __init__(self, message, category):
		super().__init__(message)
		self.category = category

class DecisionNeeded(Exception):
	def __init__(self, options, steps, message):
		super().__init__(message)
		self.options = options
		self.steps = steps

if __name__ == "__main__":
	a = Board("./4 Categories Board.json", 1)

	a.StartGraphics()

	while True:
		try:
			# a.MovePlayer(0, int(input("Steps: ")), -1, -1)
			a.MovePlayer(0, 1, -1, -1)
		except DecisionNeeded as decision:
			print(decision.options)
			a.MovePlayer(0, decision.steps, int(input("Choice: ")))

		try:
			print("Question: ", a.GetQuestionForPlayer(0))
		except QuestionError as e:
			a.RenewQuestions(e.category)

		print(a.GiveCheese(0))

		# 	if a.CheckWin(0):
		# 		break