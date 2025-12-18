########################################################################################
#                                                                                      #
#                            DINO GAME FOR NON GRAPHICAL UI                            #
#                                                                                      #
########################################################################################
# Coordinate system:
# Top-left: (0, 0)
# Top-right: (0, width-1)
# Bottom-left: (height-1, 0)
# Bottom-right: (height-1, width-1)
#

import random
import shutil
from typing import NewType
import time
import keyboard
import sys

char = NewType('Char', str)





class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Symbol:
    dino = "\033[32m█\033[0m" # "\033[32m█\033[0m"
    cactus = "\033[38;5;94m█\033[0m"
    bird = "\033[34m▭\033[0m"
    empty = " "
    floor = "\033[37m■\033[0m"
    cloud = "☁"



class Clock:
    def tick(self, fps: float):
        time.sleep(1/fps)


class GameObject:
    def __init__(self, symbol: char, x:int=None, y:int=None, xy:tuple[int, int]=None):
        """
        Symbols:
        Dino: ■
        :param symbol:
        """
        self.symbol = symbol
        if xy:
            self.x, self.y = xy
        else:
            self.x = x if x is not None else 0
            self.y = y if y is not None else 0

    def __str__(self):
        """
        __str__ is the function, if you call it like Gameobj = GameObject()
        print(Gameobj), then prints symbol
        :return:
        """
        return self.symbol


class Dino(GameObject):
    def __init__(self, symbol: char, x:int=None, y:int=None, xy:tuple[int, int]=None):
        super().__init__(symbol, x, y)
        self.velocity = 0
        self.fall_velocity = 0

    def jump(self):
        if self.y == game.height - 2:
            self.y -= 10
            if self.y < 0:
                self.y = 0
            self.fall_velocity = 0

    def update(self):
        self.fall_velocity = 1
        self.y += self.fall_velocity

        if self.y >= game.height - 2:
            self.y = game.height - 2
            self.fall_velocity = 0


    def __str__(self):
        return "Dino"

    def get_cells(self):
        return [(self.x, self.y)]


class Cactus(GameObject):
    def __init__(self, symbol: char, gme, x:int=None, y:int=None):
        super().__init__(symbol, x, y)
        self.height = random.randint(1, 2)
        self.width = random.randint(1, 3)
        self.prev_x = x
        self.prev_y = y
        self.game = gme

    def update(self):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x -= 1

    def draw(self):
        for row_offset in range(self.height):
            for col_offset in range(self.width):
                y_pos = self.prev_y - row_offset
                x_pos = self.prev_x + col_offset
                if 0 <= y_pos < self.game.height and 0 <= x_pos < self.game.width:
                    self.game.gameboard[y_pos][x_pos] = GameObject(Symbol.empty, x_pos, y_pos)

        for row_offset in range(self.height):
            for col_offset in range(self.width):
                y_pos = self.y - row_offset
                x_pos = self.x + col_offset
                if 0 <= y_pos < self.game.height and 0 <= x_pos < self.game.width:
                    self.game.gameboard[y_pos][x_pos] = self



class Game:
    def __init__(self):
        size = shutil.get_terminal_size()
        self.width = size.columns
        self.height = size.lines-1
        self.gameboard = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if y == self.height - 1:
                    row.append(GameObject(Symbol.floor, x, y))
                elif y == 0 and x % 4 == 0:
                    row.append(GameObject(Symbol.cloud, x, y))
                else:
                    row.append(GameObject(Symbol.empty, x, y))
            self.gameboard.append(row)

    def draw(self):
        sys.stdout.write("\033[H")
        for row in self.gameboard:
            sys.stdout.write("".join(obj.symbol for obj in row) + "\n")
        sys.stdout.flush()


    def update(self):
        index = self.gameboard.index(Symbol.Dino)

    def set_symbol(self, gmeObj: GameObject):
        if isinstance(gmeObj, Dino):
            for row in self.gameboard:
                for i, obj in enumerate(row):
                    if obj is gmeObj:
                        row[i] = GameObject(Symbol.empty, i, gmeObj.y)

            self.gameboard[gmeObj.y][gmeObj.x] = gmeObj

    def __str__(self):
        return "1"


    def quit(self):
        input("")
        sys.exit()

    def collision(self, obj1, obj2):
        cells1 = getattr(obj1, "get_cells", lambda: [(obj1.x, obj1.y)])()
        cells2 = getattr(obj2, "get_cells", lambda: [(obj2.x, obj2.y)])()
        for c1 in cells1:
            for c2 in cells2:
                if c1 == c2:
                    return True
        return False


game = Game()
sys.stdout.write("\033[2J")     # Clear screen
sys.stdout.write("\033[?25l")   # hide cursor
sys.stdout.flush()
game.draw()
dino = Dino(Symbol.dino, x = 5, y = game.height - 2)
clock = Clock()
print(game.gameboard)
keyboard.add_hotkey("space", dino.jump)
cacti = [Cactus(Symbol.cactus, x=100, y=game.height - 2, gme=game), Cactus(Symbol.cactus, x=120, y=game.height - 2, gme=game)]
while True:
    dino.update()
    game.set_symbol(dino)

    for cactus in reversed(cacti):
        cactus.update()
        if cactus.x + cactus.width <= 0:
            for row_offset in range(cactus.height):
                for col_offset in range(cactus.width):
                    y_pos = cactus.prev_y - row_offset
                    x_pos = cactus.prev_x + col_offset
                    if 0 <= y_pos < cactus.game.height and 0 <= x_pos < cactus.game.width:
                        cactus.game.gameboard[y_pos][x_pos] = GameObject(Symbol.empty, x_pos, y_pos)
            cacti.remove(cactus)
            continue
        cactus.draw()

    for cactus in cacti:
        if game.collision(dino, cactus):
            game.quit()

    if len(cacti) < 5 and random.randint(1, 10) == 5:
        if not cacti or all(cactus.x < game.width - 20 for cactus in cacti):
            cacti.append(Cactus(Symbol.cactus, gme=game, x=game.width - 1, y=game.height - 2))

    game.draw()
    clock.tick(15) #Pygmae like for fps


