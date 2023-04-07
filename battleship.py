from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'your move is out from board'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'your move has been marked yet'


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot ({self.x},{self.y})'


class Ship:
    def __init__(self, indicator, length, orientation):
        self.ind = indicator
        self.len = length
        self.ori = orientation
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.len):
            cur_x = self.ind.x
            cur_y = self.ind.y
            if self.ori == 0:
                cur_x += i
            elif self.ori == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def there_is_a_hit(self, dot):
        return dot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.field = [['O'] * size for _ in range(size)]
        self.busy = []
        self.ships = []
        self.count = 0

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

        if self.hid:
            res = res.replace('■', 'O')
        return res

    def out_of_board(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, border=False):
        area = [
            (-1, -1), (-1, 0), (1, -1),
            (0, -1), (0, 0), (0, 1),
            (-1, 1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for x, y in area:
                cur = Dot(dot.x + x, dot.y + y)
                if not (self.out_of_board(cur)) and cur not in self.busy:
                    if border:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out_of_board(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        if self.out_of_board(dot):
            raise BoardOutException()
        if dot in self.busy:
            raise BoardUsedException()
        self.busy.append(dot)
        for ship in self.ships:
            if ship.there_is_a_hit(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, border=True)
                    print('ship is destroyed')
                    return False
                else:
                    print('ship is damaged')
                    return True
        self.field[dot.x][dot.y] = '.'
        print('miss!')
        return False

    def clean(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f'enemy is shooting: {dot.x + 1} {dot.y + 1}')
        return dot


class User(Player):
    def ask(self):
        while True:
            cords = input('your move: ').split()
            if len(cords) != 2:
                print('enter 2 coordinates')
                continue
            x, y = cords
            if not (x.isdigit() and y.isdigit()):
                print('enter a numbers')
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        self.formation = [3, 2, 2, 1, 1, 1, 1]
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True
        self.ai = AI(computer, player)
        self.user = User(player, computer)

    def gen_board(self):
        board = Board(size=self.size)
        attempts = 0
        for f in self.formation:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), f, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.clean()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.gen_board()
        return board

    @staticmethod
    def greet():
        print('-------------------------')
        print('welcome to the battleship')
        print('-------------------------')
        print('-------------------------')
        print('    input format: x, y   ')
        print('   x - number of string  ')
        print('   y - number of column  ')
        print('-------------------------')
        print()

    def printing(self):
        print('-' * 25)
        print('user board:')
        print(self.user.board)
        print('-' * 25)
        print('ai board:')
        print(self.ai.board)
        print('-' * 25)

    def emulation(self):
        num = 0
        while True:
            self.printing()
            if num % 2 == 0:
                print('user move')
                repeat = self.user.move()
            else:
                print('ai move')
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == len(self.ai.board.ships):
                self.printing()
                print('-' * 25)
                print('user win')
                break
            if self.user.board.count == len(self.user.board.ships):
                self.printing()
                print('-' * 25)
                print('ai win')
                break
            num += 1

    def start(self):
        self.greet()
        self.emulation()


game = Game()
game.start()
