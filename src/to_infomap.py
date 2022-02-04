from helpers import *
from graph import FileSampleGraph, build_graph_from_file, filter_sample_graph
from cluster import run_infomap
from tqdm import tqdm


class ToInfomap:

    def __init__(self, config):
        
        self.__matches = get_files_from_dir(config["match_dir"], ".haps")
        self.__exclude_samples = config["exclude_samples"]
        self.__output_dir = config["output_dir"]
        self.__job_name = config["job_name"]
        self.__temp_manager = TempFileManager()
    
    def run(self):
        
        sample_ibd_graph = self.build_sample_ibd_graph()
        filtered_ibd_graph = self.filter_sample_ibd_graph(sample_ibd_graph)
        run_infomap(filtered_ibd_graph, "{}/{}_infomap_cluster.cls".format(self.__output_dir, self.__job_name))
        self.__temp_manager.purge()

    def filter_sample_ibd_graph(self, ibd_graph_addr):

        if self.__exclude_samples is not None:

            output_addr = self.__temp_manager.get_new_file()
            filter_sample_graph(ibd_graph_addr, self.__exclude_samples, output_addr)
            return output_addr
        
        else:
            return ibd_graph_addr
    
    def build_sample_ibd_graph(self):

        sample_graph = FileSampleGraph(31, 97)
        sample_graph.build_storage()
        sample_ibd_graph_file = self.__temp_manager.get_new_file()

        for chr in tqdm(self.__matches, desc="Building sample graph"):

            build_graph_from_file(self.__matches[chr], sample_graph)
        
        sample_graph.flush_adjacency_list(sample_ibd_graph_file)
        sample_graph.purge()

