import logging
from typing import List

logger = logging.getLogger(__name__)


class MinHeap:
    def __init__(self, key=lambda x: x):
        self._hash_to_index: dict = {}
        self._heap_list: List = []
        self._index_to_key: dict = {}
        self._key = key
        self._size = 0

    def push(self, object):
        self._heap_list.append(object)
        self._size += 1
        index = self._size - 1
        self._update_index(index=index, object=object)
        self._sift_up(index=index)

    def peek(self) -> object:
        return self._heap_list[0]

    def pop(self) -> object:
        return self._delete(index=0)

    def contains(self, object) -> bool:
        return object.__hash__() in self._hash_to_index.keys()

    def is_empty(self):
        return self._size == 0

    def size(self):
        return self._size

    def update(self, object, key):
        """
        assumes key within object is aleady updated. this method is to update key within MinHeap
        """
        index = self._hash_to_index[object.__hash__()]
        old_key = self._index_to_key[index]
        if old_key > key:
            self._decrease_key(index=index, key=key)
        elif old_key < key:
            self._increase_key(index=index, key=key)
        else:
            logger.info(f'Old and new key are the same.')

    def _decrease_key(self, index, key):
        old_key = self._index_to_key[index]
        assert old_key > key, f'New key must be less than old key.'
        self._index_to_key[index] = key
        self._sift_up(index=index)

    def _increase_key(self, index, key):
        assert self._index_to_key[index] < key, f'New key must be greater than old key.'
        object = self._heap_list[index]
        # delete object
        self._delete(index=index)
        # add back object
        self.push(object)

    def _sift_down(self, index) -> int:
        current_index = index
        min_child_index = self._min_child_index(current_index)
        while min_child_index is not None:
            if self._key(self._heap_list[current_index]) > self._key(self._heap_list[min_child_index]):
                self._swap(current_index, min_child_index)
                current_index = min_child_index
                min_child_index = self._min_child_index(current_index)
            else:
                break

        return current_index

    def _sift_up(self, index) -> int:
        current_index: int = index
        parent_index: int = self._parent_index(current_index)

        # print(f'{self._size}, current_index: {current_index}, parent_index: {parent_index}')
        # print([f'{i}: {x.state.value}' for i, x in enumerate(self._heap_list)])
        # # print(f'current: {self._key(self._heap_list[current_index])}, parent: {self._key(self._heap_list[parent_index])}')

        while parent_index is not None and parent_index >= 0 and \
                self._key(self._heap_list[current_index]) < self._key(self._heap_list[parent_index]):
            self._swap(current_index, parent_index)
            current_index = parent_index
            parent_index = self._parent_index(current_index)

            # print(f'{self._size}, current_index: {current_index}, parent_index: {parent_index}')
            # # print(f'current: {self._key(self._heap_list[current_index])}, parent: {self._key(self._heap_list[parent_index])}')
            # print([f'{i}: {x.state.value}' for i, x in enumerate(self._heap_list)])
            # print([f'{i}: {x}' for i, x in enumerate(self._key(self._heap_list))])

        return current_index

    def _min_child_index(self, index) -> int:
        """
        :param index: index of parent
        :return: index of smallest child. None if no children
        """
        left_child_index = self._left_child_index(index)
        right_child_index = self._right_child_index(index)

        # no children
        if left_child_index is None and right_child_index is None:
            return None
        elif left_child_index is not None and right_child_index is None:
            return left_child_index
        elif left_child_index is None and right_child_index is not None:
            # this case shouldn't happen
            right_child_index

        # both children exist
        left_object = self._heap_list[left_child_index]
        right_object = self._heap_list[right_child_index]

        if self._key(left_object) < self._key(right_object):
            return left_child_index
        else:
            return right_child_index

    def _parent_index(self, index) -> int:
        """
        :param index: index of child
        :return: index of parent. returns None if no parent
        """
        if index == 0:
            return None
        return (index - 1) // 2

    def _left_child_index(self, index) -> int:
        """
        :param index: index of parent
        :return: index of left child. returns None if no left child
        """
        left_child_index = index * 2 + 1
        return left_child_index if left_child_index < self._size else None

    def _right_child_index(self, index) -> int:
        """
        :param index: index of parent
        :return: index of right child. returns None if no right child
        """
        right_child_index = index * 2 + 2
        return right_child_index if right_child_index < self._size else None

    def _row_size(self, index) -> int:
        n = 0
        two_to_the_n = 1
        while two_to_the_n <= index + 1:
            n += 1
            two_to_the_n *= 2
        return 2 ** (n - 1)

    def _delete(self, index) -> object:
        return_object = self._heap_list[index]

        # delete metadata associated with return_object
        self._hash_to_index.pop(return_object.__hash__())
        self._index_to_key.pop(index)

        # replace removed index with last item
        self._update_index(index=index, object=self._heap_list[self._size - 1])

        # shrink
        self._size -= 1
        self._heap_list = self._heap_list[:-1]

        # if deleted index was not last index
        if index != self._size - 1:
            self._sift_down(index=index)

        return return_object

    def _swap(self, index_one, index_two) -> None:
        tmp = self._heap_list[index_one]
        self._update_index(index_one, self._heap_list[index_two])
        self._update_index(index_two, tmp)

    def _update_index(self, index, object):
        self._heap_list[index] = object
        self._hash_to_index[object.__hash__()] = index
        self._index_to_key[index] = self._key(object)
