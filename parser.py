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
    build_convert_parser(convert_parser)

    return master_parser


def build_convert_parser(convert_parser):

    subparsers = convert_parser.add_subparsers(dest="type", title="File types")

    sample_parser = subparsers.add_parser("sample", help="This tool converts a .sample file into a plink .fam file.")
    sample_parser.add_argument(
        "--sample", "-s", required=True, type=str, metavar="path_to_sample_file", help="Path to a .sample file.")
    sample_parser.add_argument(
        "--fam", "-f", required=True, type=str, metavar="path_to_fam_file", help="Path to the output .fam file.")

    haps_parser = subparsers.add_parser("haps", help="This tool converts a .haps file into a .ped file.")
    haps_parser.add_argument(
        "--haps", required=True, type=str, metavar="path_to_haps_file", help="Path to a .haps file.")
    haps_parser.add_argument(
        "--fam", "-f", required=True, type=str, metavar="path_to_fam_file", help="Path to a .fam file."
    )
    haps_parser.add_argument(
        "--ped", required=True, type=str, metavar="path_to_ped_file", help="Path to the output ped file."
    )
