from abc import ABC, abstractmethod
from helpers import sample_to_fam, haps_to_ped, run_ilash, build_map_file, TempFileManager
from qc import remove_segments, get_exclusions


class CommandHandler(ABC):

    def __init__(self):
        self.__next = None

    @abstractmethod
    def handle(self, request):
        pass

    def has_next(self):
        return self.__next is not None

    def set_next(self, next_handler):
        self.__next = next_handler

    def get_next(self):
        return self.__next


class SampleConvertHandler(CommandHandler):

    def handle(self, request):

        if request.tool == "convert" and request.type == "sample":
            sample_to_fam(request.sample, request.fam)

        elif self.has_next():
            self.get_next().handle(request)


class HapsConvertHandler(CommandHandler):

    def handle(self, request):

        if request.tool == "convert" and request.type == "haps":
            haps_to_ped(request.haps, request.fam, request.ped)

        elif self.has_next():
            self.get_next().handle(request)


class DistConvertHandler(CommandHandler):

    def handle(self, request):

        if request.tool == "convert" and request.type == "dist":
            build_map_file(request.haps, request.dist, request.chr, request.output)

        elif self.has_next():
            self.get_next().handle(request)


class ILASHHandler(CommandHandler):

    def handle(self, request):

        if request.tool == "ilash":
            run_ilash(request.ped, request.map, request.output)

        elif self.has_next():
            self.get_next().handle(request)


class QcHandler(CommandHandler):

    def handle(self, request):

        if request.tool == "qc":

            manager = TempFileManager()
            exclusions = manager.get_new_file()
            get_exclusions(request.chromosome, request.map, request.match, exclusions.name)
            remove_segments(request.chromosome, request.match, exclusions.name, request.output)
            manager.purge()

        elif self.has_next():
            self.get_next().handle(request)

