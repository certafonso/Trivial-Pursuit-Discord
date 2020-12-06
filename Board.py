import json

class Board():
	def __init__(self, board_file, n_players):

		with open(board_file, "r") as json_file:
			board_config = json.load(json_file)

		self.Categories = board_config["Categories"]

		self.Questions = board_config["Questions"]

		self.Nodes = board_config["Nodes"]

		self.players = [{"Position": 0, "Cheeses": []} for i in range(n_players)]

		self.Validate()

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

	def MovePlayer(self, player_index, steps, direction, previous = -1):
		""" Moves a player a certain amount of steps in a direction of the board """

		if steps < 1: return

		try:
			curr_pos = self.players[player_index]["Position"]
		except IndexError:
			raise PlayerError(f"There is no player with index {player_index}")

		options = self.Nodes[self.players[player_index]["Position"]]["Adj"].copy()

		print(options)

		if previous != -1:
			options.remove(previous)

		if len(options) > 1 and direction == -1:	# decision needed
			raise DecisionNeeded(options, steps, "Choice needed")

		print(len(options))
		
		if len(options) == 1:
			self.players[player_index]["Position"] = options[0]
		elif direction not in options:
			raise DecisionNeeded(options, steps, f"Choice needed, {direction} was not an option")
		else:
			self.players[player_index]["Position"] = direction

		print(f"Was {curr_pos} moved to ", self.players[player_index]["Position"])

		self.MovePlayer(player_index, steps-1, -1, curr_pos)
		
class ConfigFileError(Exception):
	def __init__(self, message):
		super().__init__(message)

class PlayerError(Exception):
	def __init__(self, message):
		super().__init__(message)

class DecisionNeeded(Exception):
	def __init__(self, options, steps, message):
		super().__init__(message)
		self.options = options
		self.steps = steps

if __name__ == "__main__":
	a = Board("./Example_Board.json", 1)

	while True:
		try:
			a.MovePlayer(0, int(input("Steps: ")), -1, -1)
		except DecisionNeeded as decision:
			print(decision.options)
			a.MovePlayer(0, decision.steps, int(input("Choice: ")))