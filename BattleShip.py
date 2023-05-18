from random import randint


class Shot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class FieldException(Exception):
    pass


class FieldOutException(FieldException):
    def __str__(self):
        return "Вы стреляете за пределы поля!"


class FieldUsedException(FieldException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class FieldSetFailException(FieldException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self. o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            put_x = self.bow.x
            put_y = self.bow.y

            if self.o == 0: # по вертикали
                put_x += i

            if self.o == 1: # по горизонтали
                put_y += i

            ship_dots.append(Shot(put_x, put_y))

        return ship_dots

    def shoot(self, shot):
        return shot in self.dots


class Field:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.count = 0 # количество пораженных кораблей

        self.field = [["▢"] * size for _ in range(size)]

        self.busy = [] # список точек, либо занятых кораблями, либо точек, в которые уже стреляли
        self.ships = [] # список корбалей на доске

    def __str__(self):
        b = ""
        b += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, j in enumerate(self.field):
            b += f"\n{i + 1} | " + " | ".join(j) + " |"

        if self.hid:
            b = b.replace("■", "▢")
        return b

    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Shot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "▪"
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise FieldSetFailException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise FieldOutException()

        if d in self.busy:
            raise FieldUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shoot(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "✖"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "0"
        print("Мимо!")
        return False

    def begin(self):
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
            except FieldException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Shot(randint(0, 5), randint(0, 5))
        print(f"Ход машина: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Shot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Field(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Shot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except FieldSetFailException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("-------------------")
        print("  Добро пожаловать ")
        print("         в         ")
        print("    Морской  Бой   ")
        print("-------------------")
        print("   Формат ввода:   ")
        print("       X пробел Y  ")
        print(" X - номер строки  ")
        print(" Y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Доска игрока:")
        print(self.us.board)
        print("-" * 20)
        print("Доска машины:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.print_boards()

            if num % 2 == 0:
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Игрок победил!")
                break

            if self.us.board.count == len(self.us.board.ships):
                print("-" * 20)
                print("Машина победила!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()