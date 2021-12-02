import numpy as np
from tqdm import tqdm, trange


def remove_segments(chrom, match_addr, remove_addr, output_addr):
    
    remove_list = []

    with open(remove_addr) as remove_file:
        for line in tqdm(remove_file, desc="Reading Remove List"):

            temp_chr, start, end = line.strip(" ").split()

            if temp_chr == chrom:
                remove_list.append((int(start), int(end)))

    count = 0

    with open(match_addr, 'r') as match_file:
        with open(output_addr, 'w') as output_file:

            for line in tqdm(match_file, desc="Removing lines"):

                data = line.strip().split('\t')
                first = int(data[5])
                last = int(data[6])
                flagged = False

                for item in remove_list:
                    if (item[0] <= first < item[1]) or (item[1] >= last > item[0]):
                        count += 1
                        flagged = True
                        break

                if not flagged:
                    output_file.write(line)

    print("DONE!")
    print("Total " + str(count) + " tracts removed.")


def get_exclusions(chrom, map_addr, match_addr, output_addr):

    map_data = load_map_data(map_addr)
    hits = np.zeros(map_data[0].shape)

    with open(match_addr) as match_file:

        for line in tqdm(match_file, desc="Reading matches"):
            data = line.strip().split()
            hits[map_data[1][int(data[5])]:map_data[1][int(data[6])]] += 1

    positions = np.array([item[3] for item in map_data[0]])

    mean = hits.mean()
    sd = hits.std()
    thresh = mean + (3 * sd)
    flag = False
    base = -1

    with open(output_addr, "w") as exclusion_file:

        for index, val in tqdm(enumerate(hits), desc="Filtering hits"):

            if val > thresh:
                if base == -1:
                    base = positions[index]
            elif base != -1:

                exclusion_file.write(f'{chrom}\t{base}\t{positions[index]}\n')
                base = -1


def load_map_data(map_addr):

    map_data = np.loadtxt(
        map_addr, skiprows=0, dtype={
            'names': ['chrom', 'RSID', 'gen_dist', 'position'], 'formats': ['i4', 'S10', 'f4', 'i8']})

    pos_dic = {}

    for item in trange(len(map_data)):
        pos_dic[map_data[item][3]] = item

    return map_data, pos_dic
