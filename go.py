import threading

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Stone:
    def __init__(self, board, point, color):
        self.board = board
        self.point = point
        self.color = color
        self.group = self.find_group()

    def remove(self):
        """Remove the stone from the board with mutual exclusion."""
        with self.board.lock:
            self.group.stones.remove(self)
        del self

    @property
    def neighbors(self):
        neighboring = [(self.point[0] - 1, self.point[1]),
                       (self.point[0] + 1, self.point[1]),
                       (self.point[0], self.point[1] - 1),
                       (self.point[0], self.point[1] + 1)]
        neighboring = [point for point in neighboring if 0 < point[0] < 20 and 0 < point[1] < 20]
        return neighboring

    @property
    def liberties(self):
        liberties = self.neighbors
        stones = self.board.search(points=self.neighbors)
        for stone in stones:
            liberties.remove(stone.point)
        return liberties

    def find_group(self):
        groups = []
        stones = self.board.search(points=self.neighbors)
        for stone in stones:
            if stone.color == self.color and stone.group not in groups:
                groups.append(stone.group)
        if not groups:
            group = Group(self.board, self)
            return group
        else:
            if len(groups) > 1:
                for group in groups[1:]:
                    groups[0].merge(group)
            groups[0].stones.append(self)
            return groups[0]

    def __str__(self):
        return 'ABCDEFGHJKLMNOPQRST'[self.point[0] - 1] + str(20 - self.point[1])

class Group:
    def __init__(self, board, stone):
        self.board = board
        self.board.groups.append(self)
        self.stones = [stone]
        self.liberties = None

    def merge(self, group):
        for stone in group.stones:
            stone.group = self
            self.stones.append(stone)
        self.board.groups.remove(group)
        del group

    def remove(self):
        while self.stones:
            self.stones[0].remove()
        self.board.groups.remove(self)
        del self

    def update_liberties(self):
        """Update the group's liberties with mutual exclusion."""
        with self.board.lock:
            liberties = []
            for stone in self.stones:
                for liberty in stone.liberties:
                    liberties.append(liberty)
            self.liberties = set(liberties)
            if len(self.liberties) == 0:
                self.remove()

    def __str__(self):
        return str([str(stone) for stone in self.stones])

class Board:
    def __init__(self):
        self.groups = []
        self.next = BLACK
        self.lock = threading.Lock()  # Create a lock for mutual exclusion

    def search(self, point=None, points=[]):
        stones = []
        for group in self.groups:
            for stone in group.stones:
                if stone.point == point and not points:
                    return stone
                if stone.point in points:
                    stones.append(stone)
        return stones

    def turn(self):
        if self.next == BLACK:
            self.next = WHITE
            return BLACK
        else:
            self.next = BLACK
            return WHITE

# Example usage:
if __name__ == "__main__":
    board = Board()
    stone1 = Stone(board, (3, 3), BLACK)
    stone2 = Stone(board, (3, 4), BLACK)

    print("Initial board:")
    print(board.groups)

    stone3 = Stone(board, (3, 5), WHITE)
    stone4 = Stone(board, (4, 5), WHITE)

    print("After adding more stones:")
    print(board.groups)
