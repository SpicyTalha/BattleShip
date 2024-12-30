from res import Strings as String
import random as rd
import datetime as dt
from collections import deque
import numpy as np

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

class HardBot(object):

    def __init__(self):
        self.__x = 0
        self.__y = 0
        self.__last_ship = []
        self.__time = 0
        self.__prob_map = [[0 for _ in range(12)] for _ in range(12)]
        self.__total_shots = 0
        self.__hunt_mode = True

        # Initialize hit map
        self.__mp = [[False for _ in range(12)] for _ in range(12)]

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
                self.__hunt_mode = False
            result = self.__hit()

        elif sms == String.GameFrame.BOT_DESTROYED:
            self.__last_ship.append((self.__x, self.__y))
            result = self.__destroyed()

        self.__time += 1
        self.__total_shots += 1
        print(">>> Bot1: shoot #%d - (%d, %d)" % (self.__time, result[0], result[1]))
        return result

    def __shoot(self):
        """
        Calls when the bot receives "shoot" command
        :return: tuple of two ints - x and y, coordinate of the bot's choice
        """
        if self.__hunt_mode:
            return self.__hunt()
        else:
            return self.__hit()

    def __hunt(self):
        """
        Hunt mode: select cells in a checkerboard pattern for efficiency.
        """
        candidates = [(x, y) for x in range(1, 11) for y in range(1, 11) if not self.__mp[y][x] and (x + y) % 2 == 0]
        if candidates:
            self.__x, self.__y = rd.choice(candidates)
        else:
            self.__x, self.__y = self.__random_shoot()

        self.__mp[self.__y][self.__x] = True
        self.__update_probability_map()
        self.__print_map()
        return self.__x, self.__y

    def __random_shoot(self):
        while True:
            x = self.__rd(1, 10)
            y = self.__rd(1, 10)
            if not self.__mp[y][x]:
                return x, y

    def __hit(self):
        """
        Calls when the bot receives "hit" command
        :return: tuple of two ints - x and y, coordinate of the bot's choice
        """
        result = ()

        if len(self.__last_ship) == 1:
            result = self.__get_one_of_four()

        elif len(self.__last_ship) > 1:
            if self.__last_ship[0][0] != self.__last_ship[1][0]:  # Horizontal
                result = self.__get_right_or_left()
            else:  # Vertical
                result = self.__get_top_or_bottom()

        self.__x, self.__y = result
        self.__mp[self.__y][self.__x] = True
        self.__update_probability_map()
        return result

    def __get_one_of_four(self):
        """
        :return: tuple of two ints - top, bottom, left, or right of the hit point
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        rd.shuffle(directions)
        for dx, dy in directions:
            nx, ny = self.__last_ship[0][0] + dx, self.__last_ship[0][1] + dy
            if 1 <= nx <= 10 and 1 <= ny <= 10 and not self.__mp[ny][nx]:
                return nx, ny
        return self.__random_shoot()

    def __get_right_or_left(self):
        """
        :return: tuple of two ints - left or right of the hit point
        """
        xes = sorted([ship[0] for ship in self.__last_ship])
        for nx in [xes[0] - 1, xes[-1] + 1]:
            if 1 <= nx <= 10 and not self.__mp[self.__last_ship[0][1]][nx]:
                return nx, self.__last_ship[0][1]
        return self.__random_shoot()

    def __get_top_or_bottom(self):
        """
        :return: tuple of two ints - top or bottom of the hit point
        """
        yes = sorted([ship[1] for ship in self.__last_ship])
        for ny in [yes[0] - 1, yes[-1] + 1]:
            if 1 <= ny <= 10 and not self.__mp[ny][self.__last_ship[0][0]]:
                return self.__last_ship[0][0], ny
        return self.__random_shoot()

    def __destroyed(self):
        """
        Calls when the bot receives "destroyed" command
        :return:
        """
        for x, y in self.__last_ship:
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                nx, ny = x + dx, y + dy
                if 1 <= nx <= 10 and 1 <= ny <= 10:
                    self.__mp[ny][nx] = True

        self.__last_ship = []
        self.__hunt_mode = True
        self.__update_probability_map()
        return self.__shoot()

    def __update_probability_map(self):
        """
        Updates the probability map based on current hits and misses.
        """
        for y in range(1, 11):
            for x in range(1, 11):
                if self.__mp[y][x]:
                    self.__prob_map[y][x] = 0
                else:
                    self.__prob_map[y][x] = self.__calculate_probability(x, y)

    def __calculate_probability(self, x, y):
        """
        Calculates the probability of a ship being at a given coordinate.
        """
        probability = 0
        ship_lengths = [2, 3, 3, 4, 5]
        for ship_len in ship_lengths:
            for dx, dy in [(1, 0), (0, 1)]:
                fits = True
                for i in range(ship_len):
                    nx, ny = x + i * dx, y + i * dy
                    if not (1 <= nx <= 10 and 1 <= ny <= 10) or self.__mp[ny][nx]:
                        fits = False
                        break
                if fits:
                    probability += 1
        return probability

    def __reinforcement_update(self, x, y, outcome):
        """
        Reinforcement learning update for probability map based on shot outcome.
        :param x: int - x coordinate
        :param y: int - y coordinate
        :param outcome: bool - True if hit, False if miss
        """
        adjustment = 3 if outcome else -2
        ship_lengths = [2, 3, 3, 4, 5]
        for ship_len in ship_lengths:
            for dx, dy in [(1, 0), (0, 1)]:
                for i in range(ship_len):
                    nx, ny = x - i * dx, y - i * dy
                    if 1 <= nx <= 10 and 1 <= ny <= 10 and not self.__mp[ny][nx]:
                        self.__prob_map[ny][nx] = max(0, self.__prob_map[ny][nx] + adjustment)

    @staticmethod
    def __rd(start: int, end: int):
        rd.seed(dt.datetime.now().microsecond)
        return rd.randint(start, end)

    def __print_map(self):
        print("\nTime:", self.__time)
        for i in range(1, 11):
            for j in range(1, 11):
                print(self.__mp[i][j], end=" ")
            print()

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
