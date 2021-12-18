from abc import abstractmethod, ABC
from tqdm import trange, tqdm
from tempfile import NamedTemporaryFile
import pandas as pd


class SampleGraph(ABC):

    # sample_id_1 and sample_id_2 are strings
    # weight must be a number
    @abstractmethod
    def store_edge(self, sample_id_1, sample_id_2, weight):
        pass

    # returns a data table with 4 columns, sample_id_1, sample_id_2
    # count and total_weight
    @abstractmethod
    def get_adjacency_list(self):
        pass

    # Clean the temperory storage on which the sample graph was stored.
    @abstractmethod
    def purge(self):
        pass


# An implementation of the SampleGraph class backed by temporary
# static files
class FileSampleGraph(SampleGraph):

    # m would be the number of buckets into which the sample graph will split.
    def __init__(self, p, m, output_dir):

        super().__init__()
        self.__p, self.__m = p, m
        self.__storage_tables = {}
        self.__output_dir = output_dir
    
    def build_storage(self):
        
        for i in trange(self.__m, desc="Generating data storage"):
            self.__storage_tables[i] = NamedTemporaryFile(mode="a", dir=self.__output_dir)

    def store_edge(self, sample_id_1, sample_id_2, weight):
        
        hash_id = polynomial_rolling_hash(sample_id_1 + "_" + sample_id_2, self.__p, self.__m)
        self.__storage_tables[hash_id].write("{}\t{}\t{}\n".format(sample_id_1, sample_id_2, weight))
    
    def get_adjacency_list(self):
        
        all_tables = [process_sample_graph(t.name) for t in self.__storage_tables.values()]

        for t in all_tables:
            
            print(t)
        

    def purge(self):
        
        for i in self.__storage_tables:
            self.__storage_tables[i].close()


# match_addr is the address of the .match file output of the ilash program
# sample_graph must be a SampleGraph object. Any object of a class extending the 
# SampleGrahph class will be acceptable
def build_graph_from_file(match_addr, sample_graph):
    
    with open(match_addr, "r") as match_file:

        for line in tqdm(match_file, desc="Building sample graph from file {}".format(match_addr)):
            
            data_row = line.strip().split("\t")
            sample_graph.store_edge(data_row[0], data_row[2], data_row[9])


# function to compute the polynomial rolling has of a string
# p is usually set as 31 for an alphabet of 26 English letters
# m is ususally set as 10e9 + 9
def polynomial_rolling_hash(str_input, p, m):
    
    power_of_p = 1
    hash_val = 0
 
    # Loop to calculate the hash value
    # by iterating over the elements of string
    for i in range(len(str_input)):

        hash_val = ((hash_val + (ord(str_input[i]) - ord('a') + 1) * power_of_p) % m)
        power_of_p = (power_of_p * p) % m
 
    return int(hash_val)


def process_sample_graph(sample_graph_addr):

    sample_graph = pd.read_csv(
        sample_graph_addr, sep="\t", 
        names=["sample_1", "sample_2", "weight"],
        dtype={"sample_1": str, "sample_2": str, "weight": float}
    )

    return sample_graph.groupby(["sample_1", "sample_2"]).count()