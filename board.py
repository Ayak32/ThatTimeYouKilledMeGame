
class Board():
    def __init__():
        eras = Era()

    def makeMove(move):
        pass

    def undoMove(move):
        pass

    def getValidMoves(Player):
        pass

    def isGameOver():
        pass

class Era():
    def __init__(self):
        self.grid = [[Space(x, y, self) for x in range(4)]
                    for y in range(4)]
        self._setupAdjacency()

    def getPieces():
        pass

    def movePiece(self, from_position, to_position):
        pass


class Space:
    def __init__(self, x: int, y: int, era: Era):
        self.position = Position(x, y, era)
        self.adjacent_spaces = []

    def getAdjacent(self) -> List[Space]:
        return self.adjacent_spaces

    def isOccupied():
        pass

class Position():
     def __init__(self, x: int, y: int, era: Era):
        _x = x
        _y = y
        _era = era

