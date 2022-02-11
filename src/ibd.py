from parser import build_parser
from chain import master_handler


if __name__ == '__main__':

    p = build_parser()
    args = p.parse_args()
    master_handler(args)
