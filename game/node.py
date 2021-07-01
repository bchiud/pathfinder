import math
from enum import Enum


class Node:
    def __init__(self, x: int, y: int, node_state, distance_to_source=None, distance_to_target=None):
        self._x = x
        self._y = y
        self._state: NodeState = node_state
        self._distance_to_source: float = distance_to_source
        self._distance_to_target: float = distance_to_target

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value) -> None:
        self._state: NodeState = value

    @property
    def distance_to_source(self) -> float:
        """
        :return: distance from current node to source node
        """
        return self._distance_to_source

    @distance_to_source.setter
    def distance_to_source(self, value: float) -> None:
        self._distance_to_source = value

    @property
    def distance_to_target(self) -> float:
        """
        :return: distance from current node to target node
        """
        return self._distance_to_target

    @distance_to_target.setter
    def distance_to_target(self, value) -> None:
        self._distance_to_target = value

    @property
    def total_distance(self) -> float:
        return self._distance_to_source + self._distance_to_target \
            if self._distance_to_source is not None and self._distance_to_target is not None \
            else None

    def distance_to(self, other):
        """
        calculates the euclidean distance between self node and other node
        :param node: other node to calculate distance between
        :return: distance between two nodes
        """
        x = self._x - other.x
        y = self._y - other.y
        return math.sqrt(x ** 2 + y ** 2)

    def _get_distance_strings(self):
        distance_to_source_str = f'{self._distance_to_source:.2f}' if self._distance_to_source else None
        distance_to_target_str = f'{self._distance_to_target:.2f}' if self._distance_to_target else None
        total_distance_str = f'{self.total_distance:.2f}' if self.total_distance else None
        return distance_to_source_str, distance_to_target_str, total_distance_str

    def __hash__(self):
        return hash((self._x, self._y))

    def __str__(self):
        distance_to_source_str, distance_to_target_str, total_distance_str = self._get_distance_strings()
        return f'({self._x}, {self._y}, {str(self._state.value)}, {distance_to_source_str}, ' \
               f'{distance_to_target_str}, {total_distance_str})'

    def __repr__(self):
        distance_to_source_str, distance_to_target_str, total_distance_str = self._get_distance_strings()
        return f'(x: {self._x}, y: {self._y}, state: {str(self._state.value)}, ' \
               f'distance_to_source: {distance_to_source_str}, distance_to_target: {distance_to_target_str}), ' \
               f'total_distance: {total_distance_str}'


class NodeState(Enum):
    OPEN = 'white'
    WALL = 'saddle brown'
    SRCE = 'orange'
    TRGT = 'SpringGreen2'
    VSTD = 'dodger blue'
    NHBR = 'deep sky blue'
    PATH = 'yellow'
