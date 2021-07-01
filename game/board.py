from typing import List

from game.node import Node, NodeState


class Board:
    def __init__(self, rows: int, columns: int):
        self._rows: int = rows
        self._columns: int = columns
        self._source: Node = None
        self._target: Node = None

        # create board
        self._board: List[List[Node]] = [
            [Node(node_state=NodeState.OPEN, x=row, y=column) for column in range(self._columns)]
            for row in range(self._rows)]

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def board(self) -> List[List[Node]]:
        return self._board

    @property
    def source(self) -> Node:
        return self._source

    @property
    def target(self) -> Node:
        return self._target

    def set_blocked_node(self, row: int, column: int) -> None:
        self._set_node_state(row=row, column=column, node_state=NodeState.WALL)

    def set_source_node(self, row: int, column: int):
        # assert source node does not exist yet
        assert self._source is None

        # set source node
        self._set_node_state(row=row, column=column, node_state=NodeState.SRCE)

        # set source node reference
        self._source = self.get_node(row=row, column=column)

        # calculate source node distances if target node exists
        if self._target is not None:
            self._update_source_node_distances()

    def set_target_node(self, row: int, column: int):
        # assert target node does not exist yet
        assert self._target is None

        # set target node
        self._set_node_state(row=row, column=column, node_state=NodeState.TRGT)

        # set target node reference
        self._target = self.get_node(row=row, column=column)

        # calculate source node distances if source node exists
        if self._source is not None:
            self._update_source_node_distances()

    def set_unblocked_node(self, row: int, column: int) -> None:
        self._set_node_state(row=row, column=column, node_state=NodeState.OPEN)

    def set_visited_node(self, row: int, column: int) -> None:
        self._set_node_state(row=row, column=column, node_state=NodeState.VSTD)

    def _set_node_state(self, row: int, column: int, node_state: NodeState):
        assert row < self._rows, f'Row index is out of bounds.'
        assert column < self._rows, f'Column index is out of bounds.'

        self._board[row][column].state = node_state

    def get_node(self, row: int, column: int) -> Node:
        return self._board[row][column]

    def _update_source_node_distances(self):
        assert self._source is not None, f'Source node must be defined.'
        assert self._target is not None, f'Target node must be defined.'

        self._source.distance_to_source: float = self._source.distance_to(self._source)
        self._source.distance_to_target: float = self._source.distance_to(self._target)

    def __str__(self):
        s = ''
        for row in self._board:
            s += f'{row.__repr__()}\n'
        return s
