from abc import abstractmethod, ABC


class PipeSegment(ABC):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def finalize(self):
        pass


class UnarySegment(PipeSegment, ABC):

    def __init__(self, upstream):
        self.__upstream = upstream

    def get_upstream(self):
        return self.__upstream


class BinarySegment(PipeSegment, ABC):

    def __init__(self, left_upstream, right_upstream):

        self.__left = left_upstream
        self.__right = right_upstream

    def get_left_upstream(self):
        return self.__left

    def get_right_upstream(self):
        return self.__right
