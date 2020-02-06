# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path

from dortmund2array import __version__
from dortmund2array.transform import BenchmarkData

__author__ = "Levi Borodenko"
__copyright__ = "Levi Borodenko"
__license__ = "mit"


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Tool to convert datasets from 'Benchmark Data Sets for Graph Kernels' (K. Kersting et al., 2016)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="dortmund2array {ver}".format(ver=__version__),
    )

    parser.add_argument(
        "--output",
        "-o",
        action="store",
        type=Path,
        default="./CLEAN/",
        help="Output folder.",
        dest="output_folder",
    )
    parser.add_argument(
        "--input",
        "-i",
        action="store",
        type=Path,
        default="./MUTAG/",
        help="Input folder containing the dataset of the same name.",
        dest="input_folder",
    )

    parser.add_argument(
        "-e",
        action="store_true",
        dest="return_edgelist",
        help="Return edge list instead of adjacency.",
    )

    return parser.parse_args(args)


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)

    data_instance = BenchmarkData(
        raw_path=args.input_folder,
        clean_path=args.output_folder,
        return_edgelist=args.return_edgelist,
    )

    print("Transforming data... This could take a while.")
    data_instance.run()


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
