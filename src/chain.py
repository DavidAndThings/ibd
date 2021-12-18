from abc import ABC, abstractmethod
from helpers import sample_to_fam, haps_to_ped, run_ilash, build_map_file, TempFileManager
from qc import remove_segments, get_exclusions, get_hits, get_threshold
import matplotlib.pyplot as plt
from graph import FileSampleGraph, build_graph_from_file
from os import listdir
from os.path import isfile, join


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
            sample_to_fam(request.sample, request.output)

        elif self.has_next():
            self.get_next().handle(request)


class HapsConvertHandler(CommandHandler):

    def handle(self, request):

        if request.tool == "convert" and request.type == "haps":
            haps_to_ped(request.haps, request.fam, request.output)

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
            output_match = request.output + ".match"
            figure = request.output + ".png"

            if request.identified is None:

                exclusions = manager.get_new_file()
                get_exclusions(request.chromosome, request.map, request.match, exclusions)
                remove_segments(request.chromosome, request.match, exclusions, output_match)

            else:
                exclusions_one, exclusions_two = request.identified, manager.get_new_file()
                get_exclusions(request.chromosome, request.map, request.match, exclusions_two)

                results_temp = manager.get_new_file()
                remove_segments(request.chromosome, request.match, exclusions_one, results_temp)
                remove_segments(request.chromosome, results_temp, exclusions_two, output_match)

            manager.purge()

            hits_before, position_before = get_hits(request.map, request.match)
            thr = get_threshold(hits_before)
            hits_after, position_after = get_hits(request.map, output_match)
            self.__plot_hits(request.chromosome, hits_before, position_before, hits_after, position_after, thr, figure)

        elif self.has_next():
            self.get_next().handle(request)

    @staticmethod
    def __plot_hits(chrom, hits_before, position_before, hits_after, position_after, thr, output_addr):

        line_before, = plt.plot(position_before, hits_before)
        line_before.set_label("Before QC")

        line_after, = plt.plot(position_after, hits_after)
        line_after.set_label("After QC")

        plt.axhline(y=thr, color='r', linestyle="-")
        plt.xlabel("position")
        plt.ylabel("hits")
        plt.title("Chromosome {} quality control".format(chrom))
        plt.legend()
        plt.savefig(output_addr)


class GraphHandler(CommandHandler):

    def handle(self, request):
        
        if request.tool == "graph":
            
            onlyfiles = [join(request.match_dir, f) for f in listdir(request.match_dir) if isfile(join(request.match_dir, f)) and f.endswith(".match")]
            sample_graph = FileSampleGraph(31, 97, request.output)
            sample_graph.build_storage()

            for f in onlyfiles:
                build_graph_from_file(f, sample_graph)
            
            sample_graph.get_adjacency_list()

        elif self.has_next():
            self.get_next().handle(request)
