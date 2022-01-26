from pickle import FALSE
import tempfile
import pandas as pd
import numpy as np
from tqdm import tqdm, trange
import subprocess


class TempFileManager:

    def __init__(self):

        self.__files = []

    def get_new_file(self):

        new_file = tempfile.NamedTemporaryFile(mode="w")
        self.__files.append(new_file)
        return new_file.name

    def purge(self):

        for f in self.__files:
            f.close()


def sample_to_fam(sample_addr, fam_addr):

    sample_table = pd.read_table(sample_addr, sep=" ", skiprows=[1])
    fam_table = sample_table.drop(["missing"], axis=1)
    fam_table.to_csv(fam_addr, header=False, sep="\t", index=False)


def haps_to_ped(haps_addr, fam_addr, ped_addr):

    size = count_columns_in_file(haps_addr, " ") - 5
    dim = count_lines_in_file(haps_addr)
    id_list = []

    with open(fam_addr, 'r') as famFile:

        for line in tqdm(famFile, desc="Reading the .fam file", leave=FALSE):
            
            data = line.strip().split()
            id_list.append((data[0], data[1]))

    convert_haps(haps_addr, size, dim, id_list, ped_addr)


def convert_haps(hap_addr, size, dim, id_list, output_addr):

    haps = np.zeros((size, dim), dtype=np.dtype('uint8'))
    counter = 0

    with open(hap_addr, 'r') as file:
        for line in tqdm(file, desc="Reading the .haps file", leave=False):

            temp_haps = line.strip().split()[5:]
            haps[:, counter] = [int(item) for item in temp_haps]
            counter += 1

    haps[haps == 0] = 2

    with open(output_addr, 'w') as output:
        for i in trange(haps.shape[0] // 2, desc="Writing .ped file", leave=False):
            # prepended = '%05d' % i
            output.write(f'{id_list[i][0]} {id_list[i][1]} 0 0 0 -9 ')

            for j in range((haps.shape[1]) - 1):
                output.write('{} {} '.format(haps[2 * i, j], haps[2 * i + 1, j]))

            output.write('{} {}\n'.format(haps[2 * i, haps.shape[1] - 1], haps[2 * i + 1, haps.shape[1] - 1]))


def run_ilash(ped_addr, map_addr, match_addr):

    ilash_config = pd.DataFrame(
        [
            ["map", map_addr], ["ped", ped_addr], ["output", match_addr],
            ["slice_size", 350], ["step_size", 350], ["perm_count", 20],
            ["shingle_size", 15], ["shingle_overlap", 0], ["bucket_count", 5],
            ["max_thread", 20], ["match_threshold", 0.99], ["interest_threshold", 0.70],
            ["min_length", 2.9], ["auto_slice", 1], ["slice_length", 2.9],
            ["cm_overlap", 1], ["minhash_threshold", 55]
        ]
    )

    with tempfile.NamedTemporaryFile(mode="w") as ilash_config_file:

        ilash_config.to_csv(ilash_config_file.name, index=False, header=False, sep=" ")
        subprocess.run(["./ilash", ilash_config_file.name], check=True)


def build_map_file(haps_addr, dist_addr, chrom, output_addr):

    with open(haps_addr, mode="r") as haps_file:

        map_data = []

        for line in tqdm(haps_file, desc="Extracting the first 3 columns of the .map file", leave=False):
            map_data.append(line.split()[0:3])

        query_file = tempfile.NamedTemporaryFile(mode="w")

        map_table = pd.DataFrame(map_data, columns=["chr", "id", "pos"])
        map_table["pos"] = pd.to_numeric(map_table["pos"])
        map_table[["id", "pos"]].to_csv(query_file.name, sep="\t", header=False, index=False)

        dist_file = tempfile.NamedTemporaryFile(mode="w")

        dist_table = pd.read_table(dist_addr, sep=" ")
        dist_table["id"] = chrom + dist_table["position"].astype(str)
        dist_table[["id", "position", "Genetic_Map(cM)"]].to_csv(dist_file.name, sep="\t", header=False, index=False)

        output_table = interpolate_map(query_file.name, dist_file.name, chrom)

        # Sort the position column in ascending order
        output_table["position"] = pd.to_numeric(output_table["position"])
        output_table = output_table.sort_values(["position"], ascending=(True,))
        output_table.to_csv(output_addr, sep='\t', header=False, index=False)

        dist_file.close()
        query_file.close()


def count_lines_in_file(file_addr):

    with open(file_addr) as f:

        counter = 0

        for line in tqdm(f, desc="Counting columns", leave=False):

            if line != "\n":
                counter += 1

        return counter


def count_columns_in_file(file_addr, sep):

    with open(file_addr) as f:

        line = f.readline()
        return len(line.strip().split(sep))


def interpolate_map(query_addr, gene_map_addr, chrom):

    query_data = np.loadtxt(
        query_addr, dtype={'names': ['RSID', 'position'], 'formats': ['S20', 'i8']}, delimiter='\t')

    gen_data = np.loadtxt(gene_map_addr, dtype={
        'names': ['RSID', 'position', 'gen_dist'], 'formats': ['S20', 'i8', 'f8']}, delimiter='\t')

    gen_dict = {}

    for i in range(gen_data.shape[0]):
        gen_dict[gen_data[i][1]] = i

    last_index = 0
    temp_dist = 0
    output_table = pd.DataFrame(data=None, columns=["chr", "RSID", "dist", "position"])

    for queryItem in tqdm(query_data, desc="Interpolating the .map file", leave=False):
        if queryItem[1] in gen_dict:
            temp_dist = gen_data[gen_dict[queryItem[1]]][2]
            last_index = gen_dict[queryItem[1]]
        else:
            temp_dist, last_index = find_head(gen_data, last_index, queryItem[1])

        output_table = output_table.append(
            {
                "chr": chrom, "RSID": str(queryItem[0]),
                "dist": str(temp_dist), "position": int(queryItem[1])
            }, ignore_index=True)

        # outputFile.write(' '.join([chrom, str(queryItem[0]), str(temp_dist), str(queryItem[1])]) + '\n')

    return output_table


def find_head(gen_data, index, position):

    while index < gen_data.shape[0] and gen_data[index][1] < position:
        index += 1

    result = (position - gen_data[index - 1][1]) * (gen_data[index - 1][2] - gen_data[index - 2][2]) / \
             (gen_data[index - 1][1] - gen_data[index - 2][1])

    return result + gen_data[index - 1][2], index - 1


# Run the shapeit phasing software. To execute this function, a ShapeIt binary must 
# be present in the working directory. The config argument is a python dictionary that
# must include the following fields: bed, bim, fam, genetic_map, output_haps, output_sample
def shapeit_phase(config):

    subprocess.run(
        [
            "./shapit", "--input-bed", 
            "{}\s{}\s{}".format(config["bed"], config["bim"], config["fam"]),
            "--input-map", config["genetic_map"], 
            "--output-max", "{}\s{}".format(config["output_haps"], config["output_sample"])
        ], check=True
    )
