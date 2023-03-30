<div align="center">

# PAITest

</div>

## 📦 版本

[v0.0.2](https://github.com/PAICookers/PAITest/releases/tag/v0.0.2)

## 🛠️ 使用

生成配置帧及对应测试输入帧，以实现硬件通路的简单测试，后续将芯片实际测试输出帧与预期结果进行对比即可。

由于配置帧/测试帧I型需要配合UART配置使用，因此目前仅采用**配置/测试帧II型**方案。

各参数含义如下：

1. `save_path`：保存配置及测试帧文件的路径；
2. `groups`：生成 `N` 组配置-测试用例组合。每次配置包含3帧，而相应配置的测试仅1帧；
3. `direction`：PC相对于PAICORE的位置，测试输出帧将从此方向输出。配置-测试用例中，单块PAICORE芯片地址将随机生成，但相对位置将不变，具体有如下几个选项：

   ```python
   TestChipDirection.EAST
   TestChipDirection.SOUTH
   TestChipDirection.WEST
   TestCHipDirection.NORTH
   ```
4. 应用示例：

   ```python
   from paitest import *
   from pathlib import Path

   '''Path to store the config & test frames'''
   save_path = Path.cwd() / "test"
   '''N groups(3 frames in each group) of configuration frames to generated'''
   groups = 1
   '''PC direction relative to the CORE'''
   direction = TestChipDirection.EAST

   GenTestCases(save_path, direction, groups)
   ```
5. 生成的 `N` 组配置帧II型、测试输入帧II型及参考测试输出帧II型在 `save_path` 下：

   ```python
   save_path
   ├ config.bin
   ├ testin.bin
   └ testout.bin
   ```

## 🗓️ TODO

- [ ] 上板验证
- [ ] 配置/测试帧III/IV型
- [ ] 参数检验
