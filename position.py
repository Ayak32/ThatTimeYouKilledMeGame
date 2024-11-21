class Position:
    def __init__(self, x: int, y: int, era):
        self._x = x
        self._y = y
        self._era = era

    def with_era(self, new_era):
        """Create a new position with updated era"""
        return Position(self._x, self._y, new_era)

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return (self._x == other._x and 
                self._y == other._y and 
                self._era == other._era)