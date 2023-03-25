from .paitest import *


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str,
                        default="./test", help="path to store test frames")
    parser.add_argument("-g", "--groups", type=int,
                        default=1, help="how many groups of test frames to be generated")
    parser.add_argument("-d", "--direction", type=TestChipDirection,
                        default=TestChipDirection.EAST, help="Test chip direction relative to the location of core")

    args = parser.parse_args()

    save_path = Path(args.path)
    direction = args.direction
    groups = args.groups

    GenTestCases(save_path, direction, groups)
