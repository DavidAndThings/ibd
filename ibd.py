from parser import build_parser
from chain import *


if __name__ == '__main__':

    p = build_parser()

    sample_conv = SampleConvertHandler()
    haps_conv = HapsConvertHandler()

    sample_conv.set_next(haps_conv)

    args = p.parse_args()
    sample_conv.handle(args)
