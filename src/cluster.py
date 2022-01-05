from infomap import Infomap
from tqdm import tqdm


def run_infomap(graph_addr, output_addr):

    im = Infomap("undirected")

    with open(graph_addr) as graph_file:

        for line in tqdm(graph_file, desc="Building infomap"):

            sample_1, sample_2, count, dist = line.split("\t")
            im.add_link(sample_1, sample_2, float(dist))
    
    im.run()
    im.write_json(output_addr)
