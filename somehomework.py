from itertools import product
import random

SHIP_ALIVE = 0x2588  # закрашенный квадрат █ - живой блок корабля
SHIP_HIT = 0x2591  # полупрозрачный квадрат ░ - подбитый блок корабля
SPACE = 0x0020  # пробел " " - пустая клетка
MISS = 0x002E  # точка . - промах


class Dot:
    """класс описание точки"""

    # граници значений
    leters = [char for char in "ABCDEF"]
    digits = list(range(1, 7))

    def __init__(self, pos) -> None:
        """инициализация экземепляра класса с позицией в виде строки A1, C6 ...
        либо кортежа с абсолютными координатами (отсчет с нуля)

        Raises:
            ValueError: если входные данные не соответсвуют требуемому формату
        """
        if isinstance(pos, str):
            self.__set_pos_from_str(pos)
        elif isinstance(pos, tuple):
            self.__set_pos_from_tuple(pos)
        else:
            raise ValueError("Unknown pos type, should be tuple or string.")
        self.char = chr(SPACE)

    def __str__(self) -> str:
        # возвращаем точку в виде строки вида A1, B4 ...
        return Dot.leters[self.x] + str(self.y + 1)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, __o: object) -> bool:
        # точки равны если их координаты равны
        return self.x == __o.x and self.y == __o.y

    def __hash__(self):
        return hash(self.__str__())

    def __set_pos_from_str(self, pos: str) -> None:
        """задает координаты из строки А1, В4 ...

        Args:
            pos (str): строка с координатами

        Raises:
            ValueError: будет исключение если буквы/цифры выходят за пределы
        """
        if len(pos) != 2:
            raise ValueError("Position (pos) should be a string of 2 characters: A5, C7 etc.")

        if pos[0].upper() not in Dot.leters:
            raise ValueError("First coordinate should be a letter from A to F: [A...F].")
        else:
            self.x = Dot.leters.index(pos[0].upper())

        if not pos[1].isdigit() or int(pos[1]) not in Dot.digits:
            raise ValueError("Second coordinate should be a digit from 1 to 6: [1...6].")
        else:
            self.y = int(pos[1]) - 1

    def __set_pos_from_tuple(self, pos: str) -> None:
        """задает координаты из кортежа

        Args:
            pos (str): кортеж с координатами

        Raises:
            ValueError: будет исключение если цифры выходят за пределы
        """
        if len(pos) != 2:
            raise ValueError("Position (pos) should be a tuple with 2 int: (0, 3) or (4, 1) etc.")

        if not isinstance(pos[0], int) or pos[0] + 1 not in Dot.digits:
            raise ValueError("First coordinate should be a digit from 0 to 5: [0...5].")
        else:
            self.x = pos[0]

        if not isinstance(pos[1], int) or pos[1] + 1 not in Dot.digits:
            raise ValueError("Second coordinate should be a digit from 0 to 5: [0...5].")
        else:
            self.y = pos[1]

    @staticmethod
    def get_all_dots() -> list:
        """возвращает список со всеми возможными точками на основе допустимых границ

        Returns:
            list: список всех возможных точек
        """
        dots = product(Dot.leters, Dot.digits)
        return list(map(lambda dot: Dot(dot[0] + str(dot[1])), dots))


class Ship:
    """класс представления корабля"""

    # ориентация: вертикальная или горизонтальная
    directions = ["v", "h"]

    def __init__(self, start_dot: Dot, direction: str, length: int) -> None:
        """создание экземляра корабля

        Args:
            start_dot (Dot): начальная точка
            direction (str): направление (v или h)
            length (int): длина корабля

        Raises:
            ValueError: если корабль слишком длинный, неизвестное направление
                        или выходит за пределы поля, то будет исключение
        """
        self.start_dot = start_dot

        # проверка направления
        if direction not in Ship.directions:
            raise ValueError(f"Available direction is: {' or '.join(Ship.directions)}.")
        else:
            self.direction = direction

        # проверка длины
        if length < 1 or length > 3:
            raise ValueError("Ship's length should be from 1 to 3.")
        else:
            # число жизний (попадание), в начале равно длине корабля
            self.lives = length
            self.length = length

        # проверяем, влезет ли в поле корабль вертикально
        if direction == Ship.directions[0]:
            try:
                _ = Dot((self.start_dot.x, self.start_dot.y + length - 1))
            except:
                raise ValueError("Ship does not fit to the board, it is too long.")
        # влезет ли в поле корабли горизонтально
        elif direction == Ship.directions[1]:
            try:
                _ = Dot((self.start_dot.x + length - 1, self.start_dot.y))
            except:
                raise ValueError("Ship does not fit to the board, it is too long.")

    def get_dots(self, with_border: bool = False) -> list:
        """возвращает все точки корабля, либо корабля + граница в виде 1 клетки вокруг него

        Args:
            with_border (bool, optional): включать ли границу. Defaults to False.

        Returns:
            list: список точек
        """
        if self.direction == Ship.directions[0] and not with_border:
            return [Dot((self.start_dot.x, self.start_dot.y + i)) for i in range(self.length)]
        elif self.direction == Ship.directions[1] and not with_border:
            return [Dot((self.start_dot.x + i, self.start_dot.y)) for i in range(self.length)]

        # если нужно вернуть корабль + границу, то сначала получаем токи корабля, рекурсивным вызовом
        ship_dots = self.get_dots()
        dots_and_border = set(ship_dots.copy())
        # затем для каждой точки корабля берем квадрат 3х3 вокруг него
        for ship_dot in ship_dots:
            for dot in product(range(ship_dot.x - 1, ship_dot.x + 2), range(ship_dot.y - 1, ship_dot.y + 2)):
                # валидация точки происходит при ее создании, все невозможные точки просто пропускаем
                try:
                    dots_and_border.add(Dot(dot))
                except:
                    pass
        return list(dots_and_border)


class Field:
    """класс представления поля"""

    def __init__(self, hidden: bool = False) -> None:
        """создание экземпляра поля

        Args:
            hidden (bool, optional): для компьютера скрываем поле от игрока. Defaults to False.
        """
        # делаем 2d массив точек
        self.board = [[Dot((x, y)) for x in range(len(Dot.digits))] for y in range(len(Dot.leters))]
        self.ship_list = []
        self.hidden = hidden
        # использованные точки
        self.hitted_dots = set()
        # точки кораблей
        self.ships_dots = set()

    def add_ship(self, ship: Ship) -> None:
        """добавляем корабль на поле

        Args:
            ship (Ship): корабль
        """
        self.ship_list.append(ship)
        # меняем все точки отрисовки корабля на закрашенный квадрат
        for dot in ship.get_dots():
            if not self.hidden:
                self.board[dot.x][dot.y].char = chr(SHIP_ALIVE)
            self.ships_dots.add(dot)

    def __generate(self, ships_count: list) -> None:
        """генерация поля

        Args:
            ships_count (list): лист с длинами кораблей вида [3 2 2 1 1]

        Raises:
            RuntimeError: генерацию пробуем пока все корабли не влезут в поле, но если
                            слишком много неуспешных попыток, будет исключение
        """
        all_dots_set = set(Dot.get_all_dots())
        for ship_length in ships_count:
            counter = 0
            # для каждого корабля пробуем создать в цикле
            while True:
                counter += 1
                try:
                    # берем рандомную точку как начало корабля, рандомное напрвление
                    # и пробуем создать корабль
                    start_dot = random.choice(tuple(all_dots_set))
                    direction = random.choice(Ship.directions)
                    ship = Ship(
                        start_dot=start_dot,
                        direction=direction,
                        length=ship_length,
                    )
                except:
                    # если создать не получилось, повторяем процесс
                    pass
                else:
                    # если создать получилось, проверяем, что нет пересечения
                    # с остальными кораблями, если все ок - выходим из цикла
                    if len(set(ship.get_dots(with_border=True)) - all_dots_set) == 0:
                        break
                if counter >= 2000:
                    raise RuntimeError("can not generate board")
            self.add_ship(ship)
            all_dots_set = all_dots_set - set(ship.get_dots())

    def generate(self, ships_count: list = [3, 2, 2, 1, 1, 1, 1]) -> None:
        """генерация поля

        Args:
            ships_count (list, optional): лист с длинами кораблей вида. Defaults to [3, 2, 2, 1, 1, 1, 1].
        """
        # пробуем создать поле пока не получится
        while True:
            try:
                self.__generate(ships_count)
            except:
                # если сюда попали, значит попыток создания было очень много, поэтому реинициализируем поле
                self.__init__(self.hidden)
            else:
                break

    def __mass_mark(self, dot_list: list, marker) -> None:
        """замена символа отображения точки

        Args:
            dot_list (list): лист точек для замены
            marker (_type_): новый символ
        """
        for dot in dot_list:
            self.board[dot.x][dot.y].char = marker
        pass

    def shot(self, dot: Dot) -> bool:
        """выстрел по полю

        Args:
            dot (Dot): куда стреляем

        Raises:
            ValueError: если в точку уже стреляли или она из границы потопленного
                        корабля - бросаем исключение

        Returns:
            bool: попали (True) или нет (False)
        """
        # можно ли стрелять в точку или нет
        if dot in self.hitted_dots:
            raise ValueError("This dot was used before. Select another one.")
        else:
            self.hitted_dots.add(dot)

        # если не попали помечаем точку промахом и выходим из функции
        if dot not in self.ships_dots:
            self.board[dot.x][dot.y].char = chr(MISS)
            return False

        # если попали
        self.board[dot.x][dot.y].char = chr(SHIP_HIT)
        for indx, ship in enumerate(self.ship_list):
            if dot in ship.get_dots():
                # уменьшаем жизнь корабля на 1
                ship.lives -= 1
                # если корабль потоплен
                if ship.lives == 0:
                    # получаем границу вокруг корабля
                    border = set(ship.get_dots(with_border=True)) - set(ship.get_dots())
                    # и маркируем границу как промахи, что бы туда нельзя было стрелять
                    self.__mass_mark(list(border), chr(MISS))
                    self.hitted_dots = self.hitted_dots.union(border)
                    self.ship_list.pop(indx)
                    break
        return True


class Board:
    """игровая доска"""

    def __init__(self, player, enemy) -> None:
        """доска состоит из двух полей:

        Args:
            player (_type_): поле игрока
            enemy (_type_): поле противника
        """
        self.player = player
        self.enemy = enemy
        # список точек куда можно стрелять компьютеру, с самого начала это все точки поля
        self.enemy_next_dots = Dot.get_all_dots()
        # список точек куда стрелять в первую очередь. при попадании компьютер будет
        # заносить сюда соседние точки, что бы в первую очередь по ним стрелять
        self.enemy_next_turn = []

    def __str__(self) -> str:
        """отрисовка игровой доски в виде

            PLAYER             ENEMY

           1 2 3 4 5 6        1 2 3 4 5 6
          +-+-+-+-+-+-+      +-+-+-+-+-+-+
        A | |█| |█|█|█|    A |.|.| | | | |
          +-+-+-+-+-+-+      +-+-+-+-+-+-+
        B |.|.|.|.| | |    B | | | | | | |
          +-+-+-+-+-+-+      +-+-+-+-+-+-+
        C |.|░|░|.| |█|    C | | | | | | |
          +-+-+-+-+-+-+      +-+-+-+-+-+-+
        D |.|.|.|.| | |    D | | | | | | |
          +-+-+-+-+-+-+      +-+-+-+-+-+-+
        E |█| |█| |█|█|    E | | | | | | |
          +-+-+-+-+-+-+      +-+-+-+-+-+-+
        F | | | | | | |    F | | | | | | |
          +-+-+-+-+-+-+      +-+-+-+-+-+-+
        """
        result = "\n" + " " * 11 + "PLAYER" + " " * 13 + "ENEMY" + "\n\n"
        result += ("        " + " ".join(map(str, Dot.digits))) * 2 + "\n"
        result += " " + ("      " + "+-" * len(Dot.digits) + "+") * 2 + "\n"
        for indx, (row1, row2) in enumerate(zip(self.player.board, self.enemy.board)):
            result += f"     {Dot.leters[indx]} |"
            for cell in row1:
                result += str(cell.char) + "|"
            result += f"    {Dot.leters[indx]} |"
            for cell in row2:
                result += str(cell.char) + "|"
            result += "\n " + ("      " + "+-" * len(Dot.digits) + "+") * 2 + "\n"
        return result

    def __player_turn(self) -> bool:
        """ход игрока]

        Returns:
            bool: удалось пойти или нет (точки нет или какая-то другая ошибка)
        """
        # вводим точку с клавиатуры
        point = input("Players turn, type dot coordinates (A1, B4, D5 etc): ")
        # пробуем создать точку, при этом проверяются условия, если какая-то ошибка, выводим ее
        # и пользователь повторяет ввод дргой точкой
        try:
            dot = Dot(point)
        except Exception as e:
            print(self)
            print(e)
            return False
        # стреляем по полю, если ошибка - выводим ее и пользователь повторяет ввод дргой точкой
        try:
            self.enemy.shot(dot)
        except Exception as e:
            print(self)
            print(e)
            return False
        print(self)
        return True

    def __enemy_turn(self) -> Dot:
        """ход компьюьтера

        Returns:
            Dot: возвращаем точку, что бы написать ее для информации
        """
        # если до этого подбили корабль и есть точки, куда стрелять в первую
        # очередь, берем точку
        if len(self.enemy_next_turn) != 0:
            dot = self.enemy_next_turn.pop()
            self.enemy_next_dots.remove(dot)
        # или выбираем из всех возможных
        else:
            random.shuffle(self.enemy_next_dots)
            dot = self.enemy_next_dots.pop()
        # пробуем стрелять, если ошибка, например в точку уже стреляли или
        # еще что-то, то повторяем ход компьютера
        try:
            shot = self.player.shot(dot)
        except:
            return self.__enemy_turn()
        # если попали
        if shot:
            # заполняем лист с точками для стрельбы в первую очередь
            next_coord = [
                (dot.x + 1, dot.y),
                (dot.x - 1, dot.y),
                (dot.x, dot.y + 1),
                (dot.x, dot.y - 1),
            ]
            for coord in next_coord:
                try:
                    next_dot = Dot(coord)
                except:
                    pass
                else:
                    if next_dot not in self.player.hitted_dots:
                        self.enemy_next_turn.append(next_dot)
        return dot

    def __check_for_winner(self) -> bool:
        """проверка победителя

        Returns:
            bool: есть победитель или нет
        """
        # если у игрока не осталось кораблей, рисуем доску и выходим
        if len(self.player.ship_list) == 0:
            print(self)
            print(" " * 10 + "===> ENEMY WIN <===")
            return True
        # если у компьютера не осталось кораблей, рисуем доску и выходим
        elif len(self.enemy.ship_list) == 0:
            print(self)
            print(" " * 10 + "===> PLAYER WIN <===")
            return True
        print(self)
        return False

    def run_game(self) -> None:
        """обработка цикла ходоа"""
        # флаг кто ходит
        player_turn = True
        while True:
            if player_turn:
                turn = self.__player_turn()
                if not turn:
                    continue
                player_turn = not player_turn
            else:
                dot = self.__enemy_turn()
                player_turn = not player_turn
                print("=" * 50)
                print(f"Сhoice of enemy: {dot}")
            win = self.__check_for_winner()
            if win:
                break


if __name__ == "__main__":
    # создаем два поля: игроку и компьютеры
    player = Field()
    player.generate()
    enemy = Field(hidden=True)
    enemy.generate()
    # создаем доску с этими двуми полями
    board = Board(player, enemy)
    print(board)
    # запускаем игру
    board.run_game()