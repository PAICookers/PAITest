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

    args = parser.parse_args()

    save_path = args.path
    direction = args.direction
    groups = args.groups

    GenTestCases(save_path, direction, groups)

    # Then, run "python main.py -p ./test -g 10 -d EAST" in your environment.