import argparse
import sys


class HelpOnErrorParser(argparse.ArgumentParser):

    def error(self, message):

        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def build_parser():

    master_parser = HelpOnErrorParser(
        description="IGH IBD pipeline."
    )

    subparsers = master_parser.add_subparsers(dest="tool", title="IBD tools")

    convert_parser = subparsers.add_parser("convert", help="A sets of tools to convert various types of files.")
    ilash_parser = subparsers.add_parser("ilash", help="Tool to run the ilash program.")
    qc_parser = subparsers.add_parser("qc", help="Tool to filter out bad ilash matches.")

    build_convert_parser(convert_parser)
    build_ilash_parser(ilash_parser)
    build_qc_parser(qc_parser)

    return master_parser


def build_convert_parser(convert_parser):

    subparsers = convert_parser.add_subparsers(dest="type", title="File types")

    sample_parser = subparsers.add_parser("sample", help="This tool converts a .sample file into a plink .fam file.")
    sample_parser.add_argument(
        "--sample", "-s", required=True, type=str, metavar="path_to_sample_file", help="Path to a .sample file.")
    sample_parser.add_argument(
        "--output", "-o", required=True, type=str, metavar="path_to_fam_file", help="Path to the output .fam file.")

    haps_parser = subparsers.add_parser("haps", help="This tool converts a .haps file into a .ped file.")

    haps_parser.add_argument(
        "--haps", required=True, type=str, metavar="path_to_haps_file", help="Path to a .haps file.")
    haps_parser.add_argument(
        "--fam", "-f", required=True, type=str, metavar="path_to_fam_file", help="Path to a .fam file.")
    haps_parser.add_argument(
        "--output", "-o", required=True, type=str, metavar="path_to_ped_file", help="Path to the output ped file.")

    dist_parser = subparsers.add_parser(
        "dist", help="This tool builds a plink .map file from a .haps and a genetic distance file")
    dist_parser.add_argument(
        "--dist", required=True, type=str, metavar="path", help="Path to a genetic distance file.")
    dist_parser.add_argument(
        "--haps", required=True, type=str, metavar="path", help="Path to a .haps file.")
    dist_parser.add_argument(
        "--chr", required=True, type=str, metavar="path", help="The chromosome for which the input files have info.")
    dist_parser.add_argument(
        "--output", "-o", required=True, type=str, metavar="path", help="Path to the output .map file.")


def build_ilash_parser(ilash_parser):

    ilash_parser.add_argument(
        "--map", "-m", required=True, type=str, metavar="path", help="Path to a .map genetic map file.")
    ilash_parser.add_argument(
        "--ped", "-p", required=True, type=str, metavar="path", help="Path to a .ped file.")
    ilash_parser.add_argument(
        "--output", "-o", required=True, type=str, metavar="path", help="Path to the output .match file.")


def build_qc_parser(qc_parser):

    qc_parser.add_argument(
        "--match", required=True, type=str, metavar="path",
        help="Path to a .match file produced by the ilash program"
    )

    qc_parser.add_argument(
        "--map", required=True, type=str, metavar="path", help="Path to a .map file containing the phased genotype data")

    qc_parser.add_argument(
        "--chromosome", "-c", required=True, type=str, metarvar="code", help="The chromosome code of interest.")

    qc_parser.add_argument(
        "--output", "-o", required=True, type=str, metavar="path", help="The filtered match file."
    )
