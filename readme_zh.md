# 《模拟火车世界》DLC汉化 / Train Sim World DLC Chinese Translation

由于多乐堂本地化组已经对线路图上多达17个第三方DLC无能为力，直接不给除了英语和德语以外的语言，只能自己动手，丰衣足食。这里含有所有的翻译原文件。

当前已汉化DLC：

- ✅ 伯明翰跨城线 Class 170 纵贯铁路&西米德兰铁路（Rivet Games）
- ✅ 西海岸干线：伯明翰-克鲁（AABS）

## 安装

Steam: 把 pak 文件扔进 `<文档>\My Games\TrainSimWorld6\Saved\UserContent`。
Epic: 把 pak 文件扔进 `<文档>\My Games\TrainSimWorld6EGS\Saved\UserContent`。

## 开发

你需要 unpak，以及一个 Google Cloud 账号。先使用 unpack 解包出语言文件，然后放到这里的dist文件夹里面。接下来，先使用 `command_helper export` 转换成 csv，然后用 translate.py 进行翻译（注意先调整术语表`glossary.csv`并且搞到你谷歌云的鉴权！），然后用 `command_helper apply` 将更改合入，最后用 `command_helper pack` 打包。

