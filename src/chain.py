from helpers import sample_to_fam, haps_to_ped, run_ilash, build_map_file
from qc import get_high_quality_regions, plot_hits
from graph import FileSampleGraph, build_graph_from_file, filter_sample_graph
from os import listdir
from os.path import isfile, join
from cluster import run_infomap
import json
from shapeit import ShapeIt
from to_ilash import deploy_to_ilash, SingleChromToIlash
from phased_toilash import deploy_phased_toilash
from to_infomap import ToInfomap


def to_infomap_function(handler):

    def to_infomap_handler(request):
        
        if request.tool == "to_infomap":

            with open(request.config) as config_file:

                config_data = json.load(config_file)
                job = ToInfomap(config_data["to_infomap"])
                job.run()
        
        else:
            handler(request)

    return to_infomap_handler


def phased_toilash_function(handler):

    def phased_toilash_handler(request):
        
        if request.tool == "phased_toilash":

            with open(request.config) as config_file:
                
                config_data = json.load(config_file)
                deploy_phased_toilash(config_data["phased_toilash"])
        
        else:
            handler(request)

    return phased_toilash_handler


def toilash_function(handler):

    def toilash_handler(request):

        if request.tool == "toilash":

            with open(request.config) as config_file:

                config_data = json.load(config_file)
                
                if request.type == "single":

                    job = SingleChromToIlash(config_data["toilash_single"])
                    job.run()

                elif request.type == "multiple":
                    
                    deploy_to_ilash(config_data["toilash_multiple"])
        
        else:
            handler(request)

    return toilash_handler


def shapeit_function(handler):

    def shapeit_handler(request):

        if request.tool == "shapeit":

            with open(request.config) as config_file:

                config_data = json.load(config_file)
                shapeit_workflow = ShapeIt(config_data)
                shapeit_workflow.run()
        
        else:
            handler(request)

    return shapeit_handler


def infomap_function(handler):

    def infomap_handler(request):

        if request.tool == "infomap":
            run_infomap(request.graph, request.output_prefix)
        
        else:
            handler(request)

    return infomap_handler


def graph_function(handler):

    def graph_handler(request):
        
        if request.tool == "graph" and request.graph_tools == "build":
            
            onlyfiles = [join(request.match_dir, f) for f in listdir(request.match_dir) if isfile(join(request.match_dir, f)) and f.endswith(".match")]
            sample_graph = FileSampleGraph(31, 97)
            sample_graph.build_storage()

            for f in onlyfiles:
                build_graph_from_file(f, sample_graph)
            
            sample_graph.flush_adjacency_list(request.output)
            sample_graph.purge()
        
        elif request.tool == "graph" and request.graph_tools == "filter":

            filter_sample_graph(request.graph, request.exclude, request.output)
        
        else:
            handler(request)

    return graph_handler


def qc_function(handler):

    def qc_handler(request):

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
        
        else:
            handler(request)

    return qc_handler


def ilash_function(handler):

    def ilash_handler(request):
        
        if request.tool == "ilash":
            run_ilash(request.ped, request.map, request.output)
        
        else:
            handler(request)

    return ilash_handler


def dist_convert_function(handler):

    def dist_convert_handler(request):

        if request.tool == "convert" and request.type == "dist":
            build_map_file(request.haps, request.dist, request.chr, request.output)
        
        else:
            handler(request)

    return dist_convert_handler


def haps_convert_function(handler):

    def haps_convert_handler(request):

        if request.tool == "convert" and request.type == "haps":
            haps_to_ped(request.haps, request.fam, request.output)
        
        else:
            handler(request)
    
    return haps_convert_handler


def sample_convert_function(handler):

    def sample_convert_handler(request):
        
        if request.tool == "convert" and request.type == "sample":
            sample_to_fam(request.sample, request.output)
        
        else:
            handler(request)

    return sample_convert_handler


@to_infomap_function
@phased_toilash_function
@toilash_function
@shapeit_function
@infomap_function
@graph_function
@qc_function
@ilash_function
@dist_convert_function
@haps_convert_function
@sample_convert_function
def master_handler(request):
    print("Input is invalid :(")
