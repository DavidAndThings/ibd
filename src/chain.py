from abc import ABC, abstractmethod
from helpers import sample_to_fam, haps_to_ped, run_ilash, build_map_file, TempFileManager
from qc import get_high_quality_regions, plot_hits
from graph import FileSampleGraph, build_graph_from_file
from os import listdir
from os.path import isfile, join
from cluster import run_infomap
import json
from shapeit import ShapeIt


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

            output_match = request.output + ".match"
            output_figure = request.output + ".png"

            get_high_quality_regions(
                request.map, request.match, request.chromosome, 
                output_match, request.identified
            )

            plot_hits(
                request.map, request.match, request.chromosome, 
                output_match, output_figure
            )

        elif self.has_next():
            self.get_next().handle(request)


class GraphHandler(CommandHandler):

    def handle(self, request):
        
        if request.tool == "graph":
            
            onlyfiles = [join(request.match_dir, f) for f in listdir(request.match_dir) if isfile(join(request.match_dir, f)) and f.endswith(".match")]
            sample_graph = FileSampleGraph(31, 97)
            sample_graph.build_storage()

            for f in onlyfiles:
                build_graph_from_file(f, sample_graph)
            
            sample_graph.flush_adjacency_list(request.output)
            sample_graph.purge()

        elif self.has_next():
            self.get_next().handle(request)


class InfoMapHandler(CommandHandler):

    def handle(self, request):
        
        if request.tool == "infomap":

            run_infomap(request.graph, request.output_prefix)

        elif self.has_next():
            self.get_next().handle(request)


class ShapeItHandler(CommandHandler):

    def handle(self, request):

        if request.tool == "shapeit":

            with open(request.config) as config_file:

                config_data = json.load(config_file)
                shapeit_workflow = ShapeIt(config_data)
                shapeit_workflow.run()
        
        elif self.has_next():
            
            self.get_next().handle(request)
