import sys
import math
import random
import turtle
import time
import copy
from enum import Enum


Color = str | tuple[float, float, float]
Point = tuple[float, float]
Line = tuple[float, float]


class Player(Enum):
    NIL = 0
    RED = 1
    BLU = 2

    def color(self) -> Color:
        if self == Player.RED:
            return 'red'
        if self == Player.BLU:
            return 'blue'
        return 'black'

    def __invert__(self):
        if self == Player.RED:
            return Player.BLU
        if self == Player.BLU:
            return Player.RED
        return Player.NIL


class Gui:
    def __init__(self, width: int, height: int, title: str = ''):
        turtle.setup(width, height)
        turtle.title(title)
        turtle.setworldcoordinates(-1.5, -1.5, 1.5, 1.5)
        turtle.tracer(0, 0)
        turtle.hideturtle()

    def draw_dot(self, dot: Point, color: Color):
        turtle.up()
        turtle.goto(dot)
        turtle.color(color)
        turtle.dot(15)

    def draw_line(self, p1: Point, p2: Point, color: Color, pensize: int):
        turtle.up()
        turtle.pensize(pensize)
        turtle.goto(p1)
        turtle.down()
        turtle.color(color)
        turtle.goto(p2)

    def update(self):
        turtle.update()

    def clear(self):
        turtle.clear()


class Sim:
    def __init__(self, minimax_depth: int, prune: bool, vertices: int, gui: bool, frame_delay: float = 1):
        self.minimax_depth: int = minimax_depth
        self.prune: bool = prune
        self.vertices: int = vertices

        self.turn: Player = Player.RED
        self.reds: list[Line] = []
        self.blues: list[Line] = []
        self.available_moves: list[Line] = []

        self.gui = Gui(600, 600, 'Game of SIM - 810199484') if gui else None
        self.gui_dots: list[Point] = []
        self.frame_delay: float = frame_delay

    def generate_dots(self) -> list[Point]:
        dots: list[Point] = []
        for angle in range(0, 360, 360 // self.vertices):
            radians = math.radians(angle)
            dots.append((math.cos(radians), math.sin(radians)))
        return dots

    def draw_line(self, line: Line, color: Color, pensize: int = 3):
        angle = 360 // self.vertices
        radX, radY = (math.radians(line[0] * angle), math.radians(line[1] * angle))
        self.gui.draw_line((math.cos(radX), math.sin(radX)),
                           (math.cos(radY), math.sin(radY)),
                           color, pensize)

    def draw(self):
        if self.gui is None:
            return None

        for dot in self.gui_dots:
            self.gui.draw_dot(dot, 'dark gray')

        for red in self.reds:
            self.draw_line(red, 'red')
        for blue in self.blues:
            self.draw_line(blue, 'blue')

        self.gui.update()
        time.sleep(self.frame_delay)

    def initialize(self):
        self.available_moves.clear()
        self.reds.clear()
        self.blues.clear()

        for i in range(0, self.vertices):
            for j in range(i, self.vertices):
                if i != j:
                    self.available_moves.append((i, j))

        self.turn = random.choice((Player.RED, Player.BLU))

        self.gui_dots = self.generate_dots()
        if self.gui is not None:
            self.gui.clear()

        self.draw()

    def evaluate(self, turn: Player) -> int:
        score_multiplier = 1 if turn == Player.RED else -1
        turn_lines = self.reds if turn == Player.RED else self.blues
        other_lines = self.blues if turn == Player.RED else self.reds
        score = 0
        for x in self.available_moves:
            if self.check_triangle(turn_lines + [x]):
                score -= 10
            # elif self.check_triangle(other_lines + [x]):
            #     score += 10
            else:
                score += 1
        return score * score_multiplier

    def minimax(self, depth: int, turn: Player, alpha: float = -math.inf, beta: float = math.inf) -> tuple[Line, int, int]:
        if turn == Player.BLU:
            if self.check_triangle(self.reds):
                return None, -math.inf, depth
        if turn == Player.RED:
            if self.check_triangle(self.blues):
                return None, +math.inf, depth

        if depth <= 0:
            return None, self.evaluate(turn), depth

        optimal_move = None
        score_depth = -1

        if turn == Player.RED:
            score_max = -math.inf
            for move in copy.deepcopy(self.available_moves):
                self.reds.append(move)
                self.available_moves.remove(move)

                _, score, ret_depth = self.minimax(depth - 1, ~turn, alpha, beta)
                ret_depth = self.minimax_depth - ret_depth

                self.reds.remove(move)
                self.available_moves.append(move)

                if score == math.inf:
                    return move, score, ret_depth

                if score > score_max:
                    optimal_move = move
                    score_max = score
                    score_depth = ret_depth
                    alpha = max(alpha, score_max)
                    if self.prune and score_max >= beta:
                        break
                elif score == score_max:
                    if ret_depth > score_depth:
                        optimal_move = move
                        score_depth = ret_depth

            return optimal_move, score_max, score_depth

        if turn == Player.BLU:
            score_min = math.inf
            for move in copy.deepcopy(self.available_moves):
                self.blues.append(move)
                self.available_moves.remove(move)

                _, score, ret_depth = self.minimax(depth - 1, ~turn, alpha, beta)
                ret_depth = self.minimax_depth - ret_depth

                self.blues.remove(move)
                self.available_moves.append(move)

                if score == -math.inf:
                    return move, score, ret_depth

                if score < score_min:
                    optimal_move = move
                    score_min = score
                    score_depth = ret_depth
                    beta = min(beta, score_min)
                    if self.prune and score_min <= alpha:
                        break
                elif score == score_min:
                    if ret_depth > score_depth:
                        optimal_move = move
                        score_depth = ret_depth

            return optimal_move, score_min, score_depth

    def random_move(self) -> Line:
        return random.choice(self.available_moves)

    def swap_turn(self):
        self.turn = ~self.turn

    def play(self) -> Player:
        self.initialize()
        while self.available_moves:
            if self.turn == Player.RED:
                selection = self.minimax(self.minimax_depth, self.turn)[0]
                self.reds.append(selection)
            else:
                selection = self.random_move()
                self.blues.append(selection)

            self.available_moves.remove(selection)
            self.swap_turn()
            self.draw()

            winner = self.gameover()
            if winner != Player.NIL:
                return winner
        return Player.NIL

    def check_triangle(self, lines: list[Line]) -> tuple[Line, Line, Line] | None:
        for i in range(len(lines) - 2):
            for j in range(i + 1, len(lines) - 1):
                for k in range(j + 1, len(lines)):
                    unique_dots = {*lines[i], *lines[j], *lines[k]}
                    if len(unique_dots) == 3:
                        return (lines[i], lines[j], lines[k])
        return None

    def gameover(self) -> Player:
        def draw_lines(lines: list[Line], color: Color, pensize: int):
            if self.gui is None:
                return None
            for line in lines:
                self.draw_line(line, color, pensize)
            self.gui.update()
            time.sleep(self.frame_delay)

        def check_triangle_creator() -> tuple[Player, tuple[Line, Line, Line]]:
            if len(self.reds) < 3 and len(self.blues) < 3:
                return Player.NIL, None
            three_lines = self.check_triangle(self.reds)
            if three_lines:
                return Player.RED, three_lines
            three_lines = self.check_triangle(self.blues)
            if three_lines:
                return Player.BLU, three_lines
            return Player.NIL, None

        loser, lines = check_triangle_creator()
        if not lines:
            return Player.NIL
        draw_lines(lines, loser.color(), 7)
        return ~loser


def main(argv: list[str] = None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) < 3:
        raise SystemExit('usage: game.py <minimax_depth> <gui:1-0> <prune:1-0>')

    loops = 100
    depth = int(argv[0])
    has_gui = bool(int(argv[1]))
    prune = bool(int(argv[2]))

    game = Sim(depth, prune, 6, has_gui, 0.5)

    results = {Player.RED: 0, Player.BLU: 0, Player.NIL: 0}
    time_start = time.time()
    for _ in range(loops):
        winner = game.play()
        results[winner] += 1
    time_end = time.time()

    print(f'Time taken: {time_end - time_start:.3f} seconds')
    print(f'Average time per game: {(time_end - time_start) / loops:.3f} seconds')
    print(f'Total red wins: {results[Player.RED]}')
    print(f'Total blue wins: {results[Player.BLU]}')


if __name__ == '__main__':
    main()
