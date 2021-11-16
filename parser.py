import argparse
import sys


class HelpOnErrorParser(argparse.ArgumentParser):

    def error(self, message):

        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)
