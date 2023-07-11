<div align="center">

# PAITest

</div>

## 📦 版本

[v1.1.0](https://github.com/PAICookers/PAITest/releases/tag/v1.1.0)

✨支持大/小端格式输出

## 🛠️ 使用

配置帧及对应测试输入帧，以实现硬件通路的简单测试，后续将芯片实际测试输出帧与预期结果进行对比即可。

⚠️ 由于配置帧/测试帧I型需要配合串口配置使用，因此目前仅采用**配置/测试帧II型**方案，且 `CHIP_ADDR` 与 `CORE*_ADDR` 均固定为 `(0, 0)`。

1. 实例化 `PAITest`。在这个版本下，参数 `test_chip_coord` 的优先级大于 `direction`；当仅配置 `dirction` 时通过此计算 `test_chip_coord`，否则使用 `test_chip_coord` 参数

   ```python
   from paitest import paitest

   # Set the address of chip under test and the test chip address.
   PAITestManager = paitest("EAST", (0, 0), test_chip_coord=(1, 0))
   ```
2. `Get1GroupForNCoresWithNParams`，产生1组针对 `N` 个核的配置-测试帧，每个核配置**不同参数**。可以指定单个需要**屏蔽**的核坐标

   ```python
   groups = 10             # Generate 10 groups
   save_to_dir="./test"    # Save frames into ./test directory

   # Generate configuration frames, testin & testout frames
   cf, ti, to = PAITestManager.Get1GroupForNCoresWithNParams(groups, save_dir=save_to_dir, verbose=True)

   # Mask a cord coordinate so that avoid generating the same coordinate.
   cf, ti, to = PAITestManager.Get1GroupForNCoresWithNParams(groups,
       save_dir=save_to_dir, masked_core_coord=(12, 16), gen_txt=True)
   ```

   ⚠️ 指定 `verbose=True` 以开启日志显示，默认关闭
3. `Get1GroupForNCoresWith1Param`，产生1组针对 `N` 个核的配置-测试帧，每个核配置**相同参数**。可以指定单个需要**屏蔽**的核坐标

   ```python
   # Same as Get1GroupForNCoresWithNParams
   cf, ti, to = PAITestManager.Get1GroupForNCoresWith1Param(10, save_dir="./test")
   ```
4. `GetNGroupsFor1CoreWithNParams`，产生 `N` 组针对1个核的配置-测试帧，每个核配置**不同参数**。可以指定单个需要**屏蔽**的核坐标

   ```python
   # Same as Get1GroupForNCoresWithNParams
   cf, ti, to = PAITestManager.GetNGroupsFor1CoreWithNParams(1, save_dir="./test")
   ```
5. `ReplaceCoreCoord`，替换**单个**或**一组**帧中的 `CORE_ADDR` 为指定坐标

   ```python
   # Replaced core coordinate with (9, 9)
   replaced = PAITestManager.ReplaceCoreCoord(original_frames, (9, 9))
   ```

   ⚠️ 一组指一组完整的配置帧，包含3帧。对于测试输入帧，即为单帧。
6. `SaveFrames`，保存帧数据至指定文件，支持 `.bin` 或 `.txt` 格式，支持指定大/小端输出

   ```python
   # Save into binary files with big-edian format(default)
   PAITestManager.SaveFrames("./test/config.bin", replaced, byteorder="big")

   # Or text files
   PAITestManager.SaveFrames("./test/config.txt", replaced)
   ```

   ⚠️ 指定 `byteorder="big"/"little"` 以大/小端格式储存帧数据，默认大端

## 🗓️ TODO

- [X] 上板验证
- [ ] 参数检验
- [ ] 配置/测试帧III/IV型
