# Train Sim World DLC 中文翻译

[English](./readme.md)

本仓库是联络线汉化组 TSW 简体中文本地化项目的工作源码。

仓库中的翻译由 @smallg0at、@ibox233、Saber_Pike 和 @RaidenAZ 完成。

重要：部分 DLC 的本地化源文件未包含在本仓库中，不要假定它们的 csv 一定存在。

## 本仓库覆盖范围

本仓库包含多个第三方 DLC 的本地化/修复内容，具体列表见：

https://www.trainsimcommunity.com/mods/c3-train-sim-world/c19-patches/i7144-dlc-145br145-third-party-dlc-simplified-chinese-localisation-and-fixes-145

## 安装

Steam：将 .pak 文件放入 `<Documents>\My Games\TrainSimWorld6\Saved\UserContent`。

Epic：将 .pak 文件放入 `<Documents>\My Games\TrainSimWorld6EGS\Saved\UserContent`。

如果 `UserContent` 目录不存在，请手动创建，并确认游戏设置中已启用 mods。

## 完整本地化教程

### 0. 适配其他语言

本仓库目前是为 zh/zh-CN 路径写死配置的。

**请先 fork 本仓库。**

如果你要 fork 出来做其他目标语言，请按以下精确顺序，在项目中一致地替换语言代码：

- zh-CN -> 你的目标语言区域代码
- zh -> 你的目标文件夹代码

清空 original、dist、riviera_patch 文件夹中的所有内容。
删除项目根目录下所有的 csv 文件。

### 1. 前置要求

- Python 3
  - 需要安装 Google Cloud API 与 GenAI 相关包
  - （如果你打算使用这些服务而非其他翻译工具）
- repak 已加入 PATH
- Utils/UnrealLocres.exe（仓库已自带）
- 自动翻译所需的可选 API 凭据：
  - translate.py 需要 GOOGLE_APPLICATION_CREDENTIALS
  - translate-next.py 需要环境变量 GEMINI_API_KEY
  - （如果你打算使用这些服务而非其他翻译工具）

> [!WARNING]
> 切勿将你的密钥上传到 GitHub 仓库。如果要把密钥放在本地项目附近，请先加入 `.gitignore`。

### 2. 本仓库的文件夹职责

- original/：用于导出的 DLC 本地化源文件
- 根目录 CSV 文件：可编辑的翻译表（*.locres.csv 和 *_translated.csv）
- dist/：用于打包的最终本地化 locres 文件树
- riviera_patch/：Riviera 修复补丁专用的独立文件树
- dist_godmode/：单独的 Foob_GodMode 包的最终本地化 locres 文件树
- csv/csv_godmode/：Foob_GodMode 包的翻译表（Foob_GodMode_translated.csv）

### 3. repak 基础知识（必需）

repak 在两个地方会用到：

- 解包 DLC pak 以获取本地化资源
- 将本仓库的产物重新打包为 mod pak

快速检查：

repak --help

如果命令未找到，请先安装 repak 并确认它已加入 PATH。

### 4. 正确地从 DLC pak 中提取（仅 locres）

不要解包整个 DLC pak。先列出路径并筛选出本地化文件，再只解包所需文件。

#### 自动方式

找到 getlocresscript.ps1，将 `Set-Location` 设置为 DLC 文件夹，编辑顶部的参数后运行。

你可能需要调整脚本执行策略。

#### 手动方式

1. 列出源 pak 中的本地化路径：

    `repak list "C:\path\to\DLC.pak" | sls "Localization"`

2. 找出对应源语言的正确 locres 文件：

- `TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en/<PackName>.locres`
- 或 `TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en-GB/<PackName>.locres`

3. 仅解包这些 locres 路径：

    `repak unpack "C:\path\to\DLC.pak" --include "TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en/<PackName>.locres" --include "<filepath2>" --output "./original"`

    如果某个 DLC 使用 en-GB 而非 en，请相应替换 include 路径。

4. 验证最终源文件结构：

    `original/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en/<PackName>.locres`

    或 `original/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en-GB/<PackName>.locres`

### 5. 准备源文件

将 DLC 本地化文件放在 original/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en 或 en-GB 目录下。
将它们复制到 dist 文件夹，然后把所有名为 `en` 或 `en-GB` 的文件夹层级改成你的目标语言代码。
例如：dist/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/<langcode>。

源文件结构示例：

```
original/TS2Prototype/Plugins/DLC/AABS_Class805/Content/Localization/AABS_Class805/en/AABS_Class805.locres
dist/TS2Prototype/Plugins/DLC/AABS_Class805/Content/Localization/AABS_Class805/zh/AABS_Class805.locres
```

### 6. 将 locres 导出为 CSV

运行：

`python command_helper.py extract`

它做了什么：

- 扫描 original/TS2Prototype/Plugins/DLC
- 查找 en-GB 或 en 的 locres
- 将每个 DLC 导出为根目录下的 <PackName>.locres.csv

### 7. 翻译 CSV

根据你想要的质量/速度，选择一个翻译辅助脚本。

translate.py（Google Cloud Translate v2）：

- 使用 GOOGLE_APPLICATION_CREDENTIALS
- 质量较差，但便宜
- 翻译后应用 glossary.csv 术语替换
- 输出 <PackName>_translated.csv

translate-next.py（Gemini API）：

- 使用 GEMINI_API_KEY
- 对铁路术语和格式有更严格的翻译规则
- 返回结构化 JSON 输出并映射回 CSV
- 推荐使用

translate-next-tbt.py（Gemini API，仅处理 TBT 行）：

- 引擎/规则与 translate-next.py 相同，但只翻译 `target` 列恰好为 `TBT` 的行，其余行保持不变
- 会原地覆盖输入文件（将 `FILE` 设为某个 `_translated.csv` 文件名，而不是 `.locres.csv`）
- 在 `merge`/`godmode-extract` 给已翻译好的 csv 新增 `TBT` 占位行之后，用这个脚本而不是重新翻译整个文件

重要提示：

- 运行前请在所选脚本中设置 TARGET_LANG 和 FILE。
- 批量翻译前请保持 glossary.csv 是最新的。

### 8. 人工质检

打开生成的 *_translated.csv，至少检查以下内容：

- 站名
- 服务名称和路线模式
- 占位符如 {0}、{1}、{TrainName}（必须保持完整）
- 应保留为铁路术语的缩写

可选工具：

- merge.py 可以在进行局部替换时，将一个 CSV 中选定的列合并到另一个 CSV 中。
- reprocess.py 会为仍标记为 `TBT` 的行，从同一文件中 `source` 文本完全相同且已翻译的另一行复制翻译结果。建议在运行 translate-next-tbt.py 之前先运行它，免费去重重复字符串：`python reprocess.py ./csv/<PackName>_translated.csv`。

### 9. 将翻译应用回 locres

运行：

python command_helper.py apply

它做了什么：

- 导入每个根目录下的 *_translated.csv
- 写入 dist/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/zh/<PackName>.locres

### 10. 打包 mod 文件

主程序包：

python command_helper.py pack

- 从 dist/ 构建 ZHLoc.pak
- 尝试自动将 ZHLoc.pak 复制到你 Documents 中的 Train Sim World 6 UserContent 文件夹

Riviera 补丁包：

python command_helper.py pack-riviera

- 从 riviera_patch/ 构建 ZHLoc-riviera-fix.pak

### 11. 安装并在游戏内测试

Steam：

<Documents>\My Games\TrainSimWorld6\Saved\UserContent

Epic：

<Documents>\My Games\TrainSimWorld6EGS\Saved\UserContent

如果 UserContent 不存在，请手动创建。
在游戏设置中启用 mods（Advanced -> Enable Mods）。

### 12. DLC 更新后如何同步翻译

`dist/` 中的 zh locres 是二进制文件，其中的 key 槽位是固定的。`apply` 只能覆盖该二进制文件中已存在的 key 对应的文本——它不能新增 key 槽位，因此当某个补丁引入了新字符串时，需要额外运行一次 `override` 来重建结构，之后 `apply` 才能识别这些新 key。

1. 使用 getlocresscript.ps1 从新的 DLC pak 中提取更新后的 locres：编辑脚本顶部的 `$pakFile`（新 pak 的文件名）和 `Set-Location` 路径（你本地的 DLC 安装目录），然后运行它。它只会将 en/en-GB/zh 的 locres 路径解包到 original/ 中，覆盖旧的 `original/.../en[-GB]/<PackName>.locres`。
   - 此时先不要动 `dist/.../zh/<PackName>.locres`——`merge` 需要它当前（更新前）的内容。
2. 运行 `python command_helper.py merge`。它会遍历 original/ 中的每一个 DLC；对于每一个已存在 `./csv/<PackName>_translated.csv` 的 DLC，都会询问确认。只对你实际更新过的那个/那些 DLC 回答 `y`（未受影响的 DLC 的 csv 已经是准确的，不需要重新合并——这些可以回答 `n`/跳过）。对于更新的 DLC，它会重新导出新的 en locres 和仍是旧版的 `dist/` zh locres，按 `key` 匹配各行，把已存在的 key 的旧翻译保留下来，并把全新的 key 标记为 `TBT`（同时打印到控制台）。

    > [!WARNING]
    > 匹配只按 `key` 进行，不会比较文本内容。如果补丁修改了某个已存在 key 下的英文文本，`merge` 仍会把*旧*翻译原样保留在该 key 下，而不会有任何提示。如果你怀疑有原地修改文本的情况，请手动抽查。
3. 运行 `python command_helper.py override`（如果是 Foob_GodMode，则运行 `godmode-override`）。它会把（已更新的）en/en-GB locres 强制复制到 `dist/`（或 `dist_godmode/`）中每一个 DLC 的 zh 槽位，重建每个 DLC 的 key 结构以匹配当前 original/ 的内容。此时这样做是安全的，因为第 2 步已经把你关心的所有翻译都收集进了 csv 中——`override`/`godmode-override` 只会改动 dist 里的二进制文件，不会动 csv。
4. 填写 `./csv/<PackName>_translated.csv` 中新增的 `TBT` 行：
   - 先运行 `python reprocess.py ./csv/<PackName>_translated.csv`——它会免费填充那些 `source` 文本与某一行已翻译内容完全相同的 `TBT` 行。
   - 然后在 translate-next-tbt.py 中设置 `FILE = "<PackName>_translated.csv"` 并运行——它只会用 AI 翻译仍标记为 `TBT` 的行，并原地覆盖同一个文件，其余内容保持不变。
   - 对新翻译的行进行人工质检（参见第 7-8 节）。
5. 依次运行 `python command_helper.py apply` 和 `python command_helper.py pack`（如果是 Foob_GodMode，则依次使用 `godmode-extract`（代替第 2 步中的 `merge`）、`godmode-apply`、`godmode-pack`）。

## command_helper.py 命令参考

不带任何参数运行 `python command_helper.py` 即可打印此列表。

| 命令 | 作用 |
| --- | --- |
| `extract` | 将 `original/` 中的 en/en-GB locres 导出为每个 DLC 对应的 `./csv/<PackName>.locres.csv`（跳过 `Foob_GodMode`）。 |
| `apply` | 将每个 `./csv/*_translated.csv` 导入回 `dist/.../zh/<PackName>.locres`。 |
| `merge` | 对于已存在 `./csv/<PackName>_translated.csv` 的 DLC，重新导出 en 和当前的 zh locres 并合并，在 en 源文本仍匹配的情况下优先保留已有的 zh 文本。适用于 DLC 更新新增字符串后的重新同步，不会丢失已有翻译。覆盖前会要求确认，并跳过没有已存在翻译 csv 的 DLC。 |
| `override` | 无条件地、不经确认地将 en/en-GB locres 强制复制到 `dist/` 中每一个 DLC 的 zh 槽位（跳过 `Foob_GodMode`）。重建每个 DLC 的 key 结构以匹配当前 `original/` 内容——在 DLC 补丁新增字符串后必须运行，且只有在 `merge` 已经把现有翻译收集进 csv 之后才能安全运行（见第 12 节）。 |
| `pack` | 对 `dist/` 运行 `repak` 构建 `ZHLoc.pak`，然后将其复制到 TSW6 的 UserContent 文件夹。 |
| `pack-riviera` | 对 `riviera_patch/` 运行 `repak` 构建 `ZHLoc-riviera-fix.pak`。 |
| `godmode-extract` | 与 `merge` 思路相同，专门针对 `Foob_GodMode`：将 `original/`（en）与 `dist_godmode/`（zh）合并为 `./csv/csv_godmode/Foob_GodMode_translated.csv`。 |
| `godmode-override` | 与 `override` 思路相同，专门针对 `Foob_GodMode`：将 en/en-GB locres 强制复制到 `dist_godmode/` 的 zh 槽位。 |
| `godmode-apply` | 将 `./csv/csv_godmode/Foob_GodMode_translated.csv` 导入 `dist_godmode/.../zh/Foob_GodMode.locres`。 |
| `godmode-pack` | 对 `dist_godmode/` 运行 `repak` 构建 `ZHLoc-GodMode.pak`，然后将其复制到 TSW6 的 UserContent 文件夹。 |

## 备注

- Manuals/Liberec-Stara_Paka_Manual 中包含手动翻译资产（包括 zh-CN 输出）。

## 许可证

本项目使用经修改的 WTFPL 变体许可证。

[DO WHAT THE FUCK YOU WANT TO IF ITS FREE PUBLIC LICENSE](./license)
