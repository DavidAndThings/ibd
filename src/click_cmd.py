import click
from numpy import require
from helpers import sample_to_fam, haps_to_ped, run_ilash, build_map_file
from qc import get_high_quality_regions, plot_hits
from graph import FileSampleGraph, build_graph_from_file, filter_sample_graph
from os import listdir
from os.path import isfile, join
from cluster import run_infomap
import json
from phased_toilash import deploy_phased_toilash
from to_infomap import ToInfomap


@click.group()
def ibd():
    pass


@ibd.group()
def convert():
    pass


@convert.command(help="This tool converts a .sample file into a plink .fam file.")
@click.option("--sample", "-s", required=True, type=str, help="This tool converts a .sample file into a plink .fam file.")
@click.option("--output", "-o", required=True, type=str, help="Path to the output .fam file.")
def sample(sample, output):
    sample_to_fam(sample, output)


@convert.command(help="This tool converts a .haps file into a .ped file.")
@click.option("--haps", required=True, type=str, help="The input .haps file.")
@click.option("--fam", required=True, type=str, help="The input .fam file.")
@click.option("--output", required=True, type=str, help="Path to the output .ped file.")
def haps(haps, fam, output):
    haps_to_ped(haps, fam, output)


@convert.command(help="This tool builds a plink .map file from a .haps and a genetic distance file")
@click.option("--haps", required=True, type=str, help="The input .haps file.")
@click.option("--dist", required=True, type=str, help="The input SHAPEIT genetic dist file.")
@click.option("--chrom", required=True, type=str, help="The number of the chromosome under analysis. Must be 1-22.")
@click.option("--output", required=True, type=str, help="Path to the output .map file.")
def dist(haps, dist, chrom, output):
    build_map_file(haps, dist, chrom, output)

