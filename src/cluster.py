from infomap import Infomap
from tqdm import tqdm
import pandas as pd



class SampleIdTracker:

    def __init__(self):
        
        self.__counter = 0
        self.__id_storage = dict()
        self.__name_storage = []
    
    def get_sample_id(self, sample_name):
        
        if sample_name not in self.__id_storage:

            self.__id_storage[sample_name] = self.__counter
            self.__name_storage.append(sample_name)
            self.__counter += 1
        
        return self.__id_storage[sample_name]
    
    def get_sample_name(self, sample_id):
        return self.__name_storage[sample_id]


# Run the mapequation clustering algorithm
def run_infomap(graph_addr, output_addr):

    im = Infomap("-f undirected")
    tracker = SampleIdTracker()

    with open(graph_addr) as graph_file:

        for line in tqdm(graph_file, desc="Building infomap"):

            sample_1, sample_2, count, dist = line.split("\t")
            sample_1_id, sample_2_id = tracker.get_sample_id(sample_1), tracker.get_sample_id(sample_2)

            im.add_link(sample_1_id, sample_2_id, float(dist))
    
    im.run()

    flush_clustering_results(im, tracker, output_addr)


# flush the output of the clustering algorithm to file
def flush_clustering_results(infomap_obj, tracker, output_addr):

    cluster_assignments = pd.DataFrame([], columns=["sample_name", "cluster"])
    infomap_modules = infomap_obj.get_modules(depth_level=1)

    for sample_id in infomap_modules:
        
        cluster_assignments = cluster_assignments.append(
            {
                "sample_name": tracker.get_sample_name(sample_id),
                "cluster": infomap_modules[sample_id]
            }, 
            ignore_index=True
        )
    
    cluster_assignments.to_csv(output_addr, sep="\t", index=False, header=False)
