from infomap import Infomap
from tqdm import tqdm
import pandas as pd



class SampleIdTracker:

    def __init__(self):
        
        self.__counter = 0
        self.__storage = dict()
    
    def get_sample_id(self, sample_identifier):
        
        if sample_identifier not in self.__storage:

            self.__storage[sample_identifier] = self.__counter
            self.__counter += 1
        
        return self.__storage[sample_identifier]
    
    def flush_id_mapping(self, mapping_addr):

        id_mapping = pd.DataFrame([], columns=["name", "id"])

        for key in self.__storage:
            id_mapping = id_mapping.append({"name": key, "id": self.__storage[key]}, ignore_index=True)
        
        id_mapping.to_csv(mapping_addr, index=False, header=False, sep="\t")


def run_infomap(graph_addr, output_prefix):

    im = Infomap("-f undirected")
    tracker = SampleIdTracker()

    with open(graph_addr) as graph_file:

        for line in tqdm(graph_file, desc="Building infomap"):

            sample_1, sample_2, count, dist = line.split("\t")
            sample_1_id, sample_2_id = tracker.get_sample_id(sample_1), tracker.get_sample_id(sample_2)

            im.add_link(sample_1_id, sample_2_id, float(dist))
    
    im.run()
    im.write_json("{}.json".format(output_prefix))

    tracker.flush_id_mapping("{}_id_map.txt".format(output_prefix))


