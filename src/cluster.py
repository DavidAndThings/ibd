from infomap import Infomap
from tqdm import tqdm



class SampleIdTracker:

    def __init__(self):
        
        self.__counter = 0
        self.__storage = dict()
    
    def get_sample_id(self, sample_identifier):
        
        if sample_identifier not in self.__storage:

            self.__storage[sample_identifier] = self.__counter
            self.__counter += 1
        
        return self.__storage[sample_identifier]


def run_infomap(graph_addr, output_addr):

    im = Infomap("-f undirected")
    tracker = SampleIdTracker()

    with open(graph_addr) as graph_file:

        for line in tqdm(graph_file, desc="Building infomap"):

            sample_1, sample_2, count, dist = line.split("\t")
            sample_1_id, sample_2_id = tracker.get_sample_id(sample_1), tracker.get_sample_id(sample_2)

            im.add_link(sample_1_id, sample_2_id, float(dist))
    
    im.run()
    im.write_json(output_addr)


