from paitest import paitest
from paitest.frames import FrameDecoder

if __name__ == "__main__":
    """Here are simple exmaples"""

    # PAITest instance
    PAITestManager = paitest("EAST")

    # 1. Generate 1 group for N cores with N **different** parameters reg.
    a_cf, a_ti, a_to = PAITestManager.Get1GroupForNCoresWithNParams(
        3, save_dir="./test", verbose=True  # Turn on the verbose mode
    )
    paitest.SaveFrames(
        "./test/example_configframes.bin", a_cf, byteorder="big"    # Big-edian format
    )
    print(a_cf, a_ti, a_to)

    # 2. Generate 1 group for N cores with the **same** parameter reg.
    a_cf, a_ti, a_to = PAITestManager.Get1GroupForNCoresWith1Param(1, save_dir="./test")

    # 3. Generate N groups for 1 core with N **different** parameters reg.
    a_cf, a_fi, a_fo = PAITestManager.GetNGroupsFor1CoreWithNParams(
        3, save_dir="./test1"
    )

    # 3. Replace the core coordinate with (9, 9)
    a_cf_replaced = PAITestManager.ReplaceCoreCoord(a_cf[:3], (9, 9))
    print(f"a_cf_replaced: {a_cf_replaced}")

    # Then, decode the replaced frames to check whether the replacement is correct
    decoder = FrameDecoder()
    attr = decoder.decode(a_cf_replaced)

    replaced_coord = attr.get("core_coord")
    if replaced_coord == (9, 9):
        print("Replacement OK")
