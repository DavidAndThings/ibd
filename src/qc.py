import numpy as np
from tqdm import tqdm, trange
from helpers import TempFileManager
import matplotlib.pyplot as plt


def get_high_quality_regions(map_addr, match_addr, chrom, output_addr, identified=None):

    manager = TempFileManager()

    if identified is None:

        exclusions = manager.get_new_file()
        get_exclusions(chrom, map_addr, match_addr, exclusions)
        remove_segments(chrom, match_addr, exclusions, output_addr)

    else:
        exclusions_one, exclusions_two = identified, manager.get_new_file()
        get_exclusions(chrom, map_addr, match_addr, exclusions_two)

        results_temp = manager.get_new_file()
        remove_segments(chrom, match_addr, exclusions_one, results_temp)
        remove_segments(chrom, results_temp, exclusions_two, output_addr)
    
    manager.purge()


def plot_hits(map_addr, match_addr, chrom, filtered_match_addr, output_addr):
    
    hits_before, position_before = get_hits(map_addr, match_addr)
    thr = get_threshold(hits_before)
    hits_after, position_after = get_hits(map_addr, filtered_match_addr)

    plt.figure()
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


def remove_segments(chrom, match_addr, remove_addr, output_addr):

    remove_list = []

    with open(remove_addr) as remove_file:
        for line in tqdm(remove_file, desc="Reading Remove List", leave=False):

            data_row = line.strip(" ").split()

            if data_row[0] == chrom:
                remove_list.append((int(data_row[1]), int(data_row[2])))

    count = 0

    with open(match_addr, 'r') as match_file:
        with open(output_addr, 'w') as output_file:

            for line in tqdm(match_file, desc="Removing lines", leave=False):

                data = line.strip().split('\t')
                first = int(data[5])
                last = int(data[6])
                flagged = False

                for item in remove_list:
                    if first <= item[1] and item[0] <= last:
                        count += 1
                        flagged = True
                        break

                if not flagged:
                    output_file.write(line)

    print("DONE!")
    print("Total " + str(count) + " tracts removed.")


def get_exclusions(chrom, map_addr, match_addr, output_addr):

    hits, positions = get_hits(map_addr, match_addr)
    thresh = get_threshold(hits)

    base = -1

    with open(output_addr, "w") as exclusion_file:

        for index, val in tqdm(enumerate(hits), desc="Filtering hits", leave=False):

            if val > thresh:
                if base == -1:
                    base = positions[index]
            elif base != -1:

                exclusion_file.write(f'{chrom}\t{base}\t{positions[index]}\n')
                base = -1


def get_hits(map_addr, match_addr):

    map_data = load_map_data(map_addr)
    hits = np.zeros(map_data[0].shape)

    with open(match_addr) as match_file:
        for line in tqdm(match_file, desc="Reading matches", leave=False):
            data = line.strip().split()
            hits[map_data[1][int(data[5])]:map_data[1][int(data[6])]] += 1

    positions = np.array([item[3] for item in map_data[0]])

    return hits, positions


def get_threshold(hits):

    mean = hits.mean()
    sd = hits.std()
    return mean + (3 * sd)


def load_map_data(map_addr):

    map_data = np.loadtxt(
        map_addr, skiprows=0, dtype={
            'names': ['chrom', 'RSID', 'gen_dist', 'position'], 'formats': ['i4', 'S10', 'f4', 'i8']})

    pos_dic = {}

    for item in trange(len(map_data), desc="Reading .map file", leave=False):
        pos_dic[map_data[item][3]] = item

    return map_data, pos_dic
