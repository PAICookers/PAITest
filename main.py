from paitest.paitest import GenTestCases


if __name__ == "__main__":
    '''Here is a simple exmaple'''
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str,
                        default="./test", help="path to store test frames")
    parser.add_argument("-g", "--groups", type=int,
                        default=1, help="how many groups of test frames to be generated")
    parser.add_argument("-d", "--direction", type=str,
                        default="EAST", help="Test chip direction relative to the location of the core")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Display the log or silently")
    parser.add_argument("-c", "--core", type=int, nargs=2,
                        default=None, help="Fix core address if you want")

    args = parser.parse_args()

    save_path = args.path
    direction = args.direction
    groups = args.groups
    verbose = args.verbose
    core_addr = tuple(args.core) if args.core else None

    GenTestCases(
        save_path,
        direction,
        groups,
        (0, 0),
        # Optional for these parameters below
        fixed_core_addr=core_addr,
        verbose=verbose
    )

    # Then, run "python main.py -p ./test -g 10 -d EAST -c 8 8 -v" in your environment.
