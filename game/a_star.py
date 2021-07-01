from typing import List

from game.board import Board
from game.min_heap import MinHeap
from game.node import Node, NodeState


class AStar:
    def __init__(self, board):
        self._board = board
        self._open_nodes: MinHeap = MinHeap(key=lambda x: x.total_distance)
        self._came_from: dict = {}
        self._path_found: bool = False

        assert self._board.source is not None, f'Board must have a source node'
        assert self._board.target is not None, f'Board must have a target node'

        self._open_nodes.push(self._board.source)

    def next(self) -> (Node, List[Node]):
        assert self._path_found is False, 'Path already found'

        # all possible nodes exhausted, board has no path from source to target
        if self._open_nodes.size() == 0:
            return (None, None)

        current_node: Node = self._open_nodes.pop()
        assert current_node.state != NodeState.VSTD, f'Node has already been visited'

        # target node has been reached
        if current_node == self._board.target:
            self._path_found = True

            # mark path nodes
            current_node = self._came_from[self._board.target]
            while current_node != self._board.source:
                current_node.state = NodeState.PATH
                current_node = self._came_from[current_node]

            return current_node, None

        # mark current node as visited
        if current_node != self._board.source:
            current_node.state = NodeState.VSTD

        # get neighbor nodes
        neighbor_nodes = self._get_neighbor_nodes(node=current_node)
        updated_neighbor_nodes: List[Node] = []

        for neighbor_node in neighbor_nodes:
            # if neighbor_node.state == NodeState.VSTD:
            #     continue

            # update distance_to_source and distance_to_target as needed
            candidate_distance_to_source = current_node.distance_to_source + current_node.distance_to(neighbor_node)
            if neighbor_node.distance_to_source is None \
                    or candidate_distance_to_source < neighbor_node.distance_to_source:
                self._came_from[neighbor_node] = current_node

                neighbor_node.distance_to_source = candidate_distance_to_source

                candidate_distance_to_target = neighbor_node.distance_to(self._board.target)
                neighbor_node.distance_to_target = candidate_distance_to_target \
                    if neighbor_node.distance_to_target is None \
                    else min(neighbor_node.distance_to_target, candidate_distance_to_target)

                updated_neighbor_nodes.append(neighbor_node)
                if self._open_nodes.contains(neighbor_node):
                    self._open_nodes.update(neighbor_node, neighbor_node.total_distance)
                else:
                    if neighbor_node != self._board.target:
                        neighbor_node.state = NodeState.NHBR
                    self._open_nodes.push(neighbor_node)

        return current_node, updated_neighbor_nodes

    def get_path(self) -> List[Node]:
        path = []

        current_node = self._came_from[self._board.target]

        while current_node != self._board.source:
            path = [current_node] + path
            current_node = self._came_from[current_node]

        return path

    def _get_neighbor_nodes(self, node: Node) -> List[Node]:
        """
        determines neighbors and sets their distance_to_source and distance_to_target
        :param node: node to find neighbors of
        :return: list of neighbors for given node
        """

        x_start = node.x - 1 if node.x > 0 else node.x
        x_stop = node.x + 2 if node.x < self._board.rows - 1 else node.x + 1
        y_start = node.y - 1 if node.y > 0 else node.y
        y_stop = node.y + 2 if node.y < self._board.columns - 1 else node.y + 1

        neighbor_nodes: List[Node] = []
        for i in range(x_start, x_stop):
            for j in range(y_start, y_stop):
                if i != node.x or j != node.y:
                    neighbor_node = self._board.get_node(row=i, column=j)
                    if neighbor_node.state in [NodeState.OPEN, NodeState.TRGT]:
                        neighbor_nodes.append(neighbor_node)

        return neighbor_nodes


if __name__ == '__main__':
    b = Board(rows=5, columns=5)
    b.set_source_node(row=0, column=0)
    b.set_target_node(row=4, column=4)
    b.set_blocked_node(row=3, column=3)
    a: AStar = AStar(board=b)
    while True:
        current_node, updated_neighbor_nodes = a.next()
        print(f'Current Node: {current_node}')
        if updated_neighbor_nodes is None:
            print(f'Path: {a.get_path()}')
            break
        else:
            for n in updated_neighbor_nodes:
                print(f'Neighbor Node: {n}')
