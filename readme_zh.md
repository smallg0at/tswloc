# Train Sim World DLC 中文翻译

由于官方本地化团队无法应对路线图上多达 17 个第三方 DLC，且仅提供英文和德文，我借助 Google 翻译自行完成了翻译。本仓库包含所有原始的翻译源文件。

尽管该代码用于中文翻译，也可用于其他语言！

当前已本地化的 DLC：

- ✅ Birmingham Cross‑City Line — Class 170 (Rivet Games)
- ✅ West Coast Main Line: Birmingham–Crewe (AABS)

## 安装

Steam：将 .pak 文件放入 `<Documents>\My Games\TrainSimWorld6\Saved\UserContent`。
Epic：将 .pak 文件放入 `<Documents>\My Games\TrainSimWorld6EGS\Saved\UserContent`。

## 开发

- 前置要求
    - 安装 unpak 和 Python（及所需依赖）。
    - Google Cloud 账号：进行认证（gcloud auth application-default login）或将 GOOGLE_APPLICATION_CREDENTIALS 指向服务账号的 JSON。
    - **\[重要\]** 在自动翻译前准备/调整 glossary.csv。我建议使用当前列表，但将所有键分别改为你的目标语言，否则后续校正会很麻烦。

- 使用 unpak 解包
    1. 找到 DLC 的 .pak 文件（Steam/Epic 安装目录或导出的副本）。按 Ctrl+Shift+C 可复制其路径。
    2. 将语言文件提取到 dist 目录（示例命令 — 请根据你构建的 unpak 版本使用 unpak --help 确认精确参数）：
         - Windows 示例：
             - `unpak extract "C:\path\to\DLC.pak" -o ".\dist\"`
    3. 验证提取出的语言文件（`.locres`）是否存在，路径通常类似 `dist\TS2Prototype\Plugins\DLC\AABS_Class350_BTP\Content\Localization\AABS_Class350_BTP\en-GB\AABS_Class350_BTP.locres`。
    4. 将 `en-GB` 文件夹名改为你的语言代码，并在 command_helper.py 中将所有 `zh` 替换为你的语言代码。
    5. 除了 `.locres` 文件本身外，删除其他所有文件，保留目录结构。

- 转换、翻译与重打包
    1. 将提取出的语言文件放入本仓库的 dist 文件夹（每个 DLC 一个文件夹）。
    2. 运行：
         - `python command_helper extract`
             （将本地化文件转换为 CSV）
    3. 翻译：
         - 编辑 translate.py 中的 `TARGET_LANG` 和 `FILE`。确保 Google Cloud 已认证且 glossary 已设置。
         - 运行 translate.py，会生成新的 csv。
    4. 合并更改：
         - `python command_helper apply`
    5. 重打包：
         - `python command_helper pack`
    6. 测试：
        - 在游戏中测试，并保持打开 csv 以便修正错误。
