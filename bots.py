from res import Strings as String
import random as rd
import datetime as dt
from collections import deque

class EasyBot:
    """
    EasyBot shoots randomly without any strategy.
    It does not remember previous shots, so it can repeat coordinates.
    """
    def say(self, value: str):
        return rd.randint(0, 9), rd.randint(0, 9)  # rd coordinates in a 10x10 grid


class MediumBot:
    """
    MediumBot avoids duplicate shots and has basic hit-follow-up logic.
    It shoots nearby cells if it gets a hit.
    """
    def __init__(self):
        self.previous_shots = set()
        self.to_follow_up = []  # Cells to target after a hit

    def say(self, value: str):
        if value == "hit" or value == "destroyed":
            self._add_adjacent_cells()

        # Follow-up logic: prioritize cells around a previous hit
        while self.to_follow_up:
            target = self.to_follow_up.pop(0)
            if target not in self.previous_shots:
                self.previous_shots.add(target)
                return target

        # rd guess if no cells to follow up
        while True:
            x, y = rd.randint(0, 9), rd.randint(0, 9)
            if (x, y) not in self.previous_shots:
                self.previous_shots.add((x, y))
                return x, y

    def _add_adjacent_cells(self):
        """
        Add adjacent cells (up, down, left, right) of the last shot to the follow-up list.
        """
        if self.previous_shots:
            last_x, last_y = max(self.previous_shots)
            possible_moves = [(last_x - 1, last_y), (last_x + 1, last_y),
                              (last_x, last_y - 1), (last_x, last_y + 1)]
            for move in possible_moves:
                if 0 <= move[0] < 10 and 0 <= move[1] < 10:  # Ensure within grid
                    self.to_follow_up.append(move)

class HardBot:
    """
    HardBot uses advanced AI strategies to efficiently search and sink all ships.
    Strategies:
      - Probability-Based Targeting
      - Pattern-Based Searching (Checkerboard Strategy)
      - Hunt and Target Mode
      - Bayesian Inference for Probability Updates
    """
    def __init__(self):
        self.grid_size = 10
        self.previous_shots = set()  # Tracks all previous shots
        self.to_follow_up = deque()  # Cells to target after a hit
        self.hunt_mode = True  # True = Hunt Mode; False = Target Mode
        self.hits = set()
        self.misses = set()
        self.probability_map = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self._initialize_probability_map()

    def say(self, value: str):
        """
        Determines the next move based on the result of the previous shot.
        :param value: "shoot", "hit", or "destroyed"
        :return: Coordinates (x, y) for the next shot
        """
        if value == "hit" or value == "destroyed":
            self.hunt_mode = False  # Switch to Target Mode
            self._add_adjacent_cells()

        # If Target Mode, prioritize adjacent cells
        if not self.hunt_mode and self.to_follow_up:
            while self.to_follow_up:
                target = self.to_follow_up.popleft()
                if self._is_valid_target(target):
                    self.previous_shots.add(target)
                    return target

        # Hunt Mode: Update probabilities and choose the best target
        self.hunt_mode = True
        self._update_probability_map()
        x, y = self._find_highest_probability_target()
        self.previous_shots.add((x, y))
        return x, y

    def _initialize_probability_map(self):
        """
        Initialize the probability map assuming ships can be placed anywhere.
        """
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.probability_map[i][j] = 1  # Uniform probabilities at the start

    def _is_valid_target(self, target):
        """
        Check if the target is valid: within bounds and not already shot.
        """
        x, y = target
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size and target not in self.previous_shots

    def _add_adjacent_cells(self):
        """
        Adds valid adjacent cells to the follow-up queue after a hit.
        """
        last_hit = max(self.previous_shots)  # Last hit coordinates
        x, y = last_hit
        possible_moves = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for nx, ny in possible_moves:
            if self._is_valid_target((nx, ny)):
                self.to_follow_up.append((nx, ny))

    def _update_probability_map(self):
        """
        Update the probability map dynamically based on hits and misses using Bayesian inference.
        """
        # Reset the map
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.probability_map[i][j] = 0

        # Update probabilities considering valid ship placements
        ship_lengths = [5, 4, 3, 3, 2]  # Example ship lengths
        for length in ship_lengths:
            # Horizontal placements
            for i in range(self.grid_size):
                for j in range(self.grid_size - length + 1):
                    if self._can_place_ship((i, j), length, horizontal=True):
                        for k in range(length):
                            self.probability_map[i][j + k] += 1

            # Vertical placements
            for i in range(self.grid_size - length + 1):
                for j in range(self.grid_size):
                    if self._can_place_ship((i, j), length, horizontal=False):
                        for k in range(length):
                            self.probability_map[i + k][j] += 1

    def _can_place_ship(self, start, length, horizontal):
        """
        Check if a ship of given length can be placed starting at (x, y).
        """
        x, y = start
        for i in range(length):
            nx, ny = (x, y + i) if horizontal else (x + i, y)
            if not (0 <= nx < self.grid_size and 0 <= ny < self.grid_size):
                return False
            if (nx, ny) in self.previous_shots:
                return False
        return True

    def _find_highest_probability_target(self):
        """
        Find the cell with the highest probability.
        """
        max_prob = -1
        best_target = None
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) not in self.previous_shots and self.probability_map[i][j] > max_prob:
                    max_prob = self.probability_map[i][j]
                    best_target = (i, j)
        return best_target if best_target else (rd.randint(0, 9), rd.randint(0, 9))


class Fati(object):

    def __init__(self):

        self.__x = 0
        self.__y = 0
        self.__last_ship = []
        self.__time = 0

        # Setting up an empty array
        self.__mp = []  # True if the field is hit else False
        for y in range(12):
            row = []
            for x in range (12):
                row.append(False)
            self.__mp.append(row)

    def say(self, sms: str):
        """
        :param sms: str - the command, what should do the bot
        :return: tuple of two int - (x, y) coordinates
        """
        result = None
        if sms == String.GameFrame.BOT_SHOOT:
            result = self.__shoot()

        elif sms == String.GameFrame.BOT_HIT:
            if self.__time != 0:
                self.__last_ship.append((self.__x, self.__y))
            result = self.__hit()

        elif sms == String.GameFrame.BOT_DESTROYED:
            self.__last_ship.append((self.__x, self.__y))
            result = self.__destroyed()

        self.__time += 1
        print(">>> Bot1: shoot #%d - (%d, %d)" % (self.__time, result[0], result[1]))
        return result

    def __shoot(self):
        """
        Calls when the bot receives "shoot" command
        :return: tuple of two ints - x and y, coordinate of the bot's chose
        """
        if not self.__last_ship:
            x = self.__rd(1, 10)
            y = self.__rd(1, 10)

            if not self.__mp[y][x]:
                self.__x = x
                self.__y = y

                self.__mp[y][x] = True
                self.__print_map()
                return x, y

            return self.__shoot()
        else:
            return self.__hit()

    def __hit(self):
        """
        Calls when the bot receives "hit" command
        :return: tuple of two ints - x and y, coordinate of the bot's chose
        """
        print("Bot's hit last ship: ", self.__last_ship)
        result = ()

        if len(self.__last_ship) == 1:
            result = self.__get_one_of_four()

        elif len(self.__last_ship) > 1:
            if self.__last_ship[0][0] != self.__last_ship[1][0]:  # is horizontal
                result = self.__get_right_or_left()
            else:
                result = self.__get_top_or_bottom()

        self.__x = result[0]
        self.__y = result[1]

        self.__mp[result[1]][result[0]] = True
        return result

    def __get_one_of_four(self):
        """
        :return: tuple of two ints - top, bottom, left or right of the hit point
        """
        where = self.__rd(1, 4)  # 1 - top, 2 - bottom, 3 - left, 4 - right

        result = None
        if where == 1 and self.__last_ship[0][1] > 1:
            result = self.__last_ship[0][0], self.__last_ship[0][1] - 1

        elif where == 2 and self.__last_ship[0][1] < 10:
            result = self.__last_ship[0][0], self.__last_ship[0][1] + 1

        elif where == 3 and self.__last_ship[0][0] > 1:
            result = self.__last_ship[0][0] - 1, self.__last_ship[0][1]

        elif where == 4 and self.__last_ship[0][0] < 10:
            result = self.__last_ship[0][0] + 1, self.__last_ship[0][1]

        if result is not None and not self.__mp[result[1]][result[0]]:
            self.__print_map()
            return result

        return self.__get_one_of_four()

    def __get_right_or_left(self):
        """
        :return: tuple of two ints - left or right of the hit point
        """
        which = self.__rd(1, 2)  # 1 - left, 2 - right
        result = None

        xes = list([ship[0] for ship in self.__last_ship])
        print("Bot1: xes: ", xes)
        right = max(xes)
        left = min(xes)

        if which == 1 and left > 1:
            result = left - 1, self.__last_ship[0][1]

        if which == 2 and right < 10:
            result = right + 1, self.__last_ship[0][1]

        if result is not None and not self.__mp[result[1]][result[0]]:
            return result

        return self.__get_right_or_left()

    def __get_top_or_bottom(self):
        """
        :return: tuple of two ints - top or bottom of the hit point
        """
        which = self.__rd(3, 4)  # 3 - top, 4 - bottom
        result = None

        yes = list([ship[1] for ship in self.__last_ship])
        print("Bot1: yes: ", yes)
        bottom = max(yes)
        top = min(yes)

        if which == 3 and top > 1:
            result = self.__last_ship[0][0], top - 1

        if which == 4 and bottom < 10:
            result = self.__last_ship[0][0], bottom + 1

        if result is not None and not self.__mp[result[1]][result[0]]:
            return result

        return self.__get_top_or_bottom()

    def __destroyed(self):
        """
        Calls when the bot receives "destroyed" command
        :return:
        """
        for x, y in self.__last_ship:
            print("Bot1: destroyed coors -", x, y)
            self.__mp[y + 1][x] = True
            self.__mp[y - 1][x] = True
            self.__mp[y][x + 1] = True
            self.__mp[y][x - 1] = True

            self.__mp[y + 1][x + 1] = True
            self.__mp[y - 1][x - 1] = True
            self.__mp[y - 1][x + 1] = True
            self.__mp[y + 1][x - 1] = True

        self.__last_ship = []

        return self.__shoot()

    @staticmethod
    def __rd(start: int, end: int):
        """
        :param start: int - start point
        :param end: int - end point
        :return: int - rd number
        """
        rd.seed(dt.datetime.now().microsecond)
        return rd.randint(start, end)

    def __print_map(self):
        print("\n Time:", self.__time)
        for i in range(1, 11):
            for j in range(1, 11):
                print(self.__mp[i][j], end=" ")
            print()
