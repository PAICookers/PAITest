<div align="center">

# PAITest

</div>

## 📦 版本

[v0.0.10 Prerelease](https://github.com/PAICookers/PAITest/releases/tag/v0.0.10)

## 🛠️ 使用

生成配置帧及对应测试输入帧，以实现硬件通路的简单测试，后续将芯片实际测试输出帧与预期结果进行对比即可。由于配置帧/测试帧I型需要配合UART配置使用，因此目前仅采用**配置/测试帧II型**方案，且 `chip_addr` 与 `core*_addr` 均固定为 `(0, 0)`。

```python
from paitest import paitest

'''Path to store the config & test frames'''
save_path = Path.cwd() / "test"
'''N groups'''
groups = 1
'''PAITest instance'''
PAITestManager = paitest("EAST")

# Random test 'groups' cores with 'groups' different parameters
paitest.GetRandomCasesForNCores(groups, save_path)

# Random test 10 cores but don't use core (6, 6)
config_frames, testin_frames, testout_frames = \
    PAITestManager.Get1CaseForNCores(10, save_dir=save_path, masked_core_coord=(6, 6))

# Save frames in .bin file
PAITestManager.SaveFrames("./test/config_1.bin", config_frames)
```

生成的 `N` 组配置帧II型、测试输入帧II型及参考测试输出帧II型在 `save_path` 下：

```python
save_path
├ config.bin
├ testin.bin
└ testout.bin
```

## 🗓️ TODO

- [ ] 上板验证
- [ ] 参数检验
- [ ] 配置/测试帧III/IV型
