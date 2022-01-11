from helpers import *
from os import listdir
from os.path import isfile, join
import re
from qc import get_high_quality_regions, plot_hits


class ShapeIt:

    def __init__(self, haps_dir, sample_dir, dist_dir, output_addr):

        self.__haps = get_files_from_dir(haps_dir, ".haps")
        self.__sample = get_files_from_dir(sample_dir, ".sample")
        self.__dist = get_files_from_dir(dist_dir, ".txt")

        self.__output_addr = output_addr
        self.__temp_manager = TempFileManager()
    
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

        get_high_quality_regions(map_file, match_file, chrom, filtered_match_file)
        plot_hits(map_file, match_file, chrom, filtered_match_file, "qc_hit_plot_chr{}.png".format(chrom))


def get_files_from_dir(dir_addr, post_fix):

    all_files = [
        join(dir_addr, f) for f in listdir(dir_addr) 
        if isfile(join(dir_addr, f)) and f.endswith(post_fix)
    ]

    files_dir = {}
    
    for i in  all_files:
        
        chrom = re.match(".+([0-9]{1,2}).+", i).group(1)
        files_dir[chrom] = i
    
    return files_dir
