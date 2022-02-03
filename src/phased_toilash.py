from helpers import *
from qc import get_high_quality_regions, plot_hits
from threading import Thread, Lock


def deploy_phased_toilash(config):

    threads = []
    job_manager = PhasedToIlashJobManager(config)

    for i in range(int(config["threads"])):
        
        t = PhasedToIlashJob(job_manager, i)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print("Finished all jobs :)")


class PhasedToIlashJob(Thread):

    lock = Lock()

    def __init__(self, job_manager, id):

        super().__init__()

        self.thread_id = id
        self.__job_manager = job_manager
    
    def run(self):
        
        while True:

            PhasedToIlashJob.lock.acquire()

            if self.__job_manager.has_jobs():

                job_config = self.__job_manager.pick_job()
                job = SingleChromPhasedToIlash(job_config)

                PhasedToIlashJob.lock.release()
                job.run()
            
            else:
                PhasedToIlashJob.lock.release()
                break


class PhasedToIlashJobManager:

    # The config argument must be a python dictionary which contains the 
    # following fields: sample_dir, haps_dir, genetic_map_dir, exclude_regions, 
    # output_dir, job_name.
    # If a chromosome is to be analyzed, there must be a corresponding bed, bim, fam and genetic_map
    # file for that chromosome. Those files must each contain the string chr{chromosome_number}
    # in their file name.
    # There will be a .match file named job_name_chr{i}.match and a .png file job_name_chr{i}.png
    # for each of the chromosomes available.
    def __init__(self, config):
        
        self.__chrom_configs = phased_toilash_split_config(config)
    
    def pick_job(self):
        return self.__chrom_configs.pop(0)
    
    def has_jobs(self):
        return len(self.__chrom_configs) > 0


class SingleChromPhasedToIlash:

    # The config argument must be a python dictionary containing the following 
    # fields: haps, sample, genetic_map, chrom, exclude_regions, output_match, 
    # output_png
    def __init__(self, config):
        
        self.__config = config
        self.__temp_manager = TempFileManager()
    
    def run(self):

        chrom = self.__config["chrom"]

        haps_file = self.__config["haps"]
        sample_file = self.__config["sample"]

        fam_file = self.__temp_manager.get_new_file()
        ped_file = self.__temp_manager.get_new_file()
        map_file = self.__temp_manager.get_new_file()
        match_file = self.__temp_manager.get_new_file()

        filtered_match_file = self.__config["output_match"]
        output_png = self.__config["output_png"]
        
        sample_to_fam(sample_file, fam_file)
        haps_to_ped(haps_file, fam_file, ped_file)
        build_map_file(haps_file, self.__config["genetic_map"], chrom, map_file)
        run_ilash(ped_file, map_file, match_file)

        get_high_quality_regions(map_file, match_file, chrom, filtered_match_file, self.__config["exclude_regions"])
        plot_hits(map_file, match_file, chrom, filtered_match_file, output_png)

        self.__temp_manager.purge()


def phased_toilash_split_config(config):

    haps_files = get_files_from_dir(config["haps_dir"], ".haps")
    sample_files = get_files_from_dir(config["sample_dir"], ".sample")
    genetic_map_files = get_files_from_dir(config["genetic_map_dir"], ".txt")

    assert len(set([len(haps_files), len(sample_files), len(genetic_map_files)])) == 1

    configs = []

    for chrom in haps_files:

        chrom_config = {
            "haps": haps_files[chrom], "sample": sample_files[chrom], 
            "genetic_map": genetic_map_files[chrom],
            "chrom": chrom, "exclude_regions": config["exclude_regions"],
            "output_match": "{}/{}_chr{}.match".format(config["output_dir"], config["job_name"], chrom), 
            "output_png": "{}/{}_chr{}.png".format(config["output_dir"], config["job_name"], chrom)
        }

        configs.append(chrom_config)
        
    return configs
