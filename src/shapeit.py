from helpers import *
from os import listdir
from os.path import isfile, join
import re
from qc import get_high_quality_regions, plot_hits
from tqdm import tqdm


# The .haps, .sample and genetic distance files are assumed to be clustered based on 
# chromosome and each file name contains a string starts with chr followed by the number
# marking the chromosome for which the file contains data.

class ShapeIt:

    def __init__(self, config):

        self.__haps = get_files_from_dir(config["haps_dir"], ".haps")
        self.__sample = get_files_from_dir(config["sample_dir"], ".sample")
        self.__dist = get_files_from_dir(config["dist_dir"], ".txt")

        self.__output_dir = config["output_dir"]
        self.__identified_regions = config["identified_regions"]
        self.__temp_manager = TempFileManager()
    
    def run(self):

        for chrom in tqdm(self.__haps, desc="Running IBD community detection workflow (SHAPEIT)"):
            self.get_quality_ibd_regions(chrom)
    
    # chr is an integer representing the chromosome under processing
    # the number must in range 1-22
    def get_quality_ibd_regions(self, chrom):
        
        fam_file = self.__temp_manager.get_new_file()
        ped_file = self.__temp_manager.get_new_file()
        map_file = self.__temp_manager.get_new_file()
        match_file = self.__temp_manager.get_new_file()
        filtered_match_file = self.__temp_manager.get_new_file()

        sample_to_fam(self.__sample[chrom], fam_file)
        haps_to_ped(self.__haps[chrom], fam_file, ped_file)
        build_map_file(self.__haps[chrom], self.__dist[chrom], chrom, map_file)
        run_ilash(ped_file, map_file, match_file)

        get_high_quality_regions(map_file, match_file, chrom, filtered_match_file, self.__identified_regions)
        plot_hits(map_file, match_file, chrom, filtered_match_file, self.__output_dir + "/qc_hit_plot_chr{}.png".format(chrom))


def get_files_from_dir(dir_addr, post_fix):

    all_files = [
        join(dir_addr, f) for f in listdir(dir_addr) 
        if isfile(join(dir_addr, f)) and f.endswith(post_fix)
    ]

    files_dir = {}
    
    for i in  all_files:
        
        chrom = re.match(".+chr([0-9]{1,2}).+", i).group(1)
        files_dir[chrom] = i
    
    return files_dir
