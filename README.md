<div align="center">

# PAITest

</div>

## 📦 版本

[v0.0.6 Prerelease](https://github.com/PAICookers/PAITest/releases/tag/v0.0.6)

## 🛠️ 使用

生成配置帧及对应测试输入帧，以实现硬件通路的简单测试，后续将芯片实际测试输出帧与预期结果进行对比即可。

由于配置帧/测试帧I型需要配合UART配置使用，因此目前仅采用**配置/测试帧II型**方案，且 `chip_addr` 与 `core*_addr` 均固定为 `(0, 0)`。

各参数含义如下：

1. `save_path`：保存配置及测试帧文件的路径；
2. `groups`：生成 `N` 组配置-测试用例组合。**每组**配置包含3帧，相应配置的测试帧仅1帧；
3. `direction`：PC相对于PAICORE的位置，测试输出帧将从此方向输出。配置-测试用例中，单块PAICORE芯片地址将随机生成，但相对位置将不变，具体有如下几个选项：

   - 东："EAST"、“East”、"east"；
   - 南：“SOUTH”、"South"、"south"；
   - 西："WEST"、"West"、"west"；
   - 北："NORTH"、“North”、"north"；
4. 应用示例（也可参考 `main.py` ）：

   ```python
   from pathlib import Path
   from paitest.paitest import GenTestCases

   '''Path to store the config & test frames'''
   save_path = Path.cwd() / "test"
   '''N groups(3 frames in each group) of configuration frames to generated'''
   groups = 1
   '''PC direction relative to the CORE'''
   direction = "EAST"

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
