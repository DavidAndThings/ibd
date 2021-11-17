import tempfile
import pandas as pd
import numpy as np
from tqdm import tqdm, trange


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

    sample_table = pd.read_table(sample_addr, sep=" ")
    fam_table = sample_table.drop(["missing"], axis=1)
    fam_table.to_csv(fam_addr, header=False, sep="\t", index=False)


def haps_to_ped(haps_addr, fam_addr, ped_addr):

    size = count_columns_in_file(haps_addr, " ") - 5
    dim = count_lines_in_file(haps_addr)
    id_list = []

    with open(fam_addr, 'r') as famFile:

        for line in tqdm(famFile):
            
            data = line.strip().split()
            id_list.append((data[0], data[1]))

    convert_haps(haps_addr, size, dim, id_list, ped_addr)


def convert_haps(hap_addr, size, dim, id_list, output_addr):

    haps = np.zeros((size, dim), dtype=np.dtype('uint8'))
    counter = 0

    with open(hap_addr, 'r') as file:
        for line in tqdm(file):

            temp_haps = line.strip().split()[5:]
            haps[:, counter] = [int(item) for item in temp_haps]
            counter += 1

    haps[haps == 0] = 2

    with open(output_addr, 'w') as output:
        for i in trange(haps.shape[0] // 2):
            # prepended = '%05d' % i
            output.write(f'{id_list[i][0]} {id_list[i][1]} 0 0 0 -9 ')

            for j in trange((haps.shape[1]) - 1):
                output.write('{} {} '.format(haps[2 * i, j], haps[2 * i + 1, j]))

            output.write('{} {}\n'.format(haps[2 * i, haps.shape[1] - 1], haps[2 * i + 1, haps.shape[1] - 1]))


def count_lines_in_file(file_addr):

    with open(file_addr) as f:

        counter = 0

        for line in tqdm(f):

            if line != "\n":
                counter += 1

        return counter


def count_columns_in_file(file_addr, sep):

    with open(file_addr) as f:

        line = f.readline()
        return len(line.strip().split(sep))
