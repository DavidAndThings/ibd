from helpers import *
from os import listdir
from os.path import isfile, join
from qc import get_high_quality_regions, plot_hits
import re
from threading import Thread, Lock


# The config argument has the same format as that of the config argument
# for the ToIlashJob class plus one extra field: threads
def deploy_to_ilash(config):

    for i in range(int(config["threads"])):

        job = ToIlashJob(config, i)
        job.start()


class ToIlashJob(Thread):

    lock=Lock()

    # The config argument has the same format as that of the config arg in
    # the JobManager class
    def __init__(self, config, id):

        super().__init__()

        self.threadID = id
        self.__job_manager = JobManager(config)
        self.__job_manager.split_config()

    def run(self):

        while True:

            ToIlashJob.lock.acquire()

            if self.__job_manager.has_jobs():

                job_config = self.__job_manager.pick_job()
                job = SingleChromToIlash(job_config)
                ToIlashJob.lock.release()

                job.run()
            
            else:
                ToIlashJob.lock.release()
                break


class JobManager:

    # The config argument must be a python dictionary which contains the 
    # following fields: bed_dir, bim_dir, fam_dir, genetic_map_dir, exclude_regions, 
    # output_dir, job_name.
    # If a chromosome is to be analyzed, there must be a corresponding bed, bim, fam and genetic_map
    # file for that chromosome. Those files must each contain the string chr{chromosome_number}
    # in their file name.
    # There will be a .match file named job_name_chr{i}.match and a .png file job_name_chr{i}.png
    # for each of the chromosomes available.
    def __init__(self, config):
        
        self.__config = config
        self.__chrom_configs = []
    
    def split_config(self):

        bed_files = get_files_from_dir(self.__config["bed_dir"], ".bed")
        bim_files = get_files_from_dir(self.__config["bim_dir"], ".bim")
        fam_files = get_files_from_dir(self.__config["fam_dir"], ".fam")
        genetic_map_files = get_files_from_dir(self.__config["genetic_map_dir"], ".txt")

        assert len(set([len(bed_files), len(bim_files), len(fam_files), len(genetic_map_files)])) == 1

        for chrom in bed_files:

            config = {
                "bed": bed_files[chrom], "bim": bim_files[chrom], 
                "fam": fam_files[chrom], "genetic_map": genetic_map_files[chrom],
                "chrom": chrom, "exclude_regions": self.__config["exclude_regions"],
                "output_match": "{}/{}_chr{}.match".format(self.__config["output_dir"], self.__config["job_name"], chrom), 
                "output_png": "{}/{}_chr{}.png".format(self.__config["output_dir"], self.__config["job_name"], chrom)
            }

            self.__chrom_configs.append(config)
    
    def pick_job(self):
        return self.__chrom_configs.pop(0)
    
    def has_jobs(self):
        return len(self.__chrom_configs) > 0


# Run the pipeline from ShapeIt phasing to QCed ilash output
class SingleChromToIlash:

    # The config argument must be a python dictionary which contains the following
    # fields: bed, bim, fam, genetic_map, chrom, exclude_regions, output_match, 
    # output_png
    def __init__(self, config):

        self.__config = config
        self.__temp_manager = TempFileManager()
    
    def run(self):

        chrom = self.__config["chrom"]

        haps_file = self.__temp_manager.get_new_file()
        sample_file = self.__temp_manager.get_new_file()

        fam_file = self.__temp_manager.get_new_file()
        ped_file = self.__temp_manager.get_new_file()
        map_file = self.__temp_manager.get_new_file()
        match_file = self.__temp_manager.get_new_file()

        filtered_match_file = self.__config["output_match"]
        output_png = self.__config["output_png"]

        shapeit_phase({**self.__config, "output_haps": haps_file, "output_sample": sample_file})

        sample_to_fam(sample_file, fam_file)
        haps_to_ped(haps_file, fam_file, ped_file)
        build_map_file(haps_file, self.__config["genetic_map"], chrom, map_file)
        run_ilash(ped_file, map_file, match_file)

        get_high_quality_regions(map_file, match_file, chrom, filtered_match_file, self.__config["exclude_regions"])
        plot_hits(map_file, match_file, chrom, filtered_match_file, output_png)

        self.__temp_manager.purge()


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

