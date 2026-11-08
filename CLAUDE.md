# Get_book

用户直接报书名，由我抓取，不建 UI、不做交互式输入。

- 公版外文：`python tools/fetch_gutenberg.py --query "<英文名>" --title "<中文名>" --author "<作者>"`
- 公版中文：加 `--lang zh`；简体书名查不到会自动转繁体（古腾堡中文库 444 本）
- 文集拆单篇：`python tools/split_stories.py --collection Books/彷徨 --pick "祝福,伤逝,在酒楼上"`
- 网页/存档单篇：`python tools/import_page.py ...`，批量清单 `tools/import_manifest.json` + `tools/import_batch.py`
- 主力学来源：DACHS 学术存档（海德堡镜像）、中国作家网、杂志/出版社转载；教材删改版不收
- 日语公版：`python tools/import_aozora.py ...`（青空文库，自动去 ruby）
- 其他公版原文：Gutenberg、Wolne Lektury、textlog.de、textarchiv.com；PDF 用 `pdftotext`
- 注意：公版的是原文，中文译本另有译者版权
- 用户自己丢进 `待导入/` 的 txt/epub：跑 `python tools/import_local.py`（提取→入库→重建目录）
- 新增书后跑 `python tools/build_catalog.py`（加序号前缀 + 生成 Books/总目录.txt + 同步 TXT全文/）
- 每篇的来源与状态见 `抓取报告.md`、`抓取报告-外国短篇.md`、`抓取报告-中国当代.md`
- DACHS 有 www / 非 www 两套路径，章节可能只在其中一套；缺章的书不要当全文
- 输出契约与书源分层、校验规则：见 `README.md`
- 校验失败（退出码 2）不要当成功汇报；不要手写正文补齐
- 维基文库、ctext、archive.org 本机都不可达，不要反复重试
- 用户接受个人学习用途；但盗版站、破解 DRM 不做。源里没有就直说，让他自己提供文本
- 古腾堡中文集篇序可能是乱的，别按目录顺序切
