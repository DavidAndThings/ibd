from pipeline import PipeSegment, UnarySegment, BinarySegment


class AddressStore(PipeSegment):

    def __init__(self, address):
        self.__addr = address

    def finalize(self):
        pass

    def run(self):
        return self.__addr


class SampleToFam(UnarySegment):

    def __init__(self, upstream):
        super().__init__(upstream)

    def finalize(self):
        pass

    def run(self):
        pass


class MapToMap(UnarySegment):

    def __init__(self, upstream):
        super().__init__(upstream)

    def finalize(self):
        pass

    def run(self):
        pass


class HapsToPed(BinarySegment):

    def __init__(self, left_upstream, right_upstream):
        super().__init__(left_upstream, right_upstream)

    def finalize(self):
        pass

    def run(self):
        pass