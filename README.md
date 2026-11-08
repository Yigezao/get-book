# Get_book · 抓书工具

给我（Claude）报书名，我来抓。你不必点界面、不必自己找网址。

## 怎么用

```bash
# 公版外文（英文/法文/德文等）
python tools/fetch_gutenberg.py --query "gift of the magi" --title "麦琪的礼物" --author "欧·亨利"

# 中文公版（《朝花夕拾》《吶喊》《紅樓夢》《論語》…，古腾堡共 444 本）
python tools/fetch_gutenberg.py --query "朝花夕拾" --lang zh --title "朝花夕拾" --author "鲁迅"

# 已知古腾堡书号时更稳
python tools/fetch_gutenberg.py --id 7256 --title "麦琪的礼物" --author "欧·亨利"
```

中文书用简体书名查不到时，脚本会自动转繁体再查一次；下载的是繁体原版，默认用 OpenCC 转简体（`--keep-traditional` 保留原样）。

## 从文集拆单篇

```bash
# 《彷徨》里拆出指定的几篇
python tools/split_stories.py --collection Books/彷徨 --pick "祝福,伤逝,在酒楼上"
# 《呐喊》同理
python tools/split_stories.py --collection Books/呐喊 --pick "孔乙己,狂人日记"
```

篇名表在 `tools/collections.json`。边界按**文件里的实际顺序**取下一篇，不按目录顺序。

古腾堡中文集有两个坑，拆篇前必须知道：

- 篇序可能是乱的（《呐喊》《徬徨》都乱）
- 《徬徨》缺《幸福的家庭》《肥皂》《弟兄》三篇，别当成拆失败

拆完会核对「篇名在首段、字数达标、末尾不串下一篇」，不过不落盘。

## 从网页 / 学术存档导入单篇

```bash
# 单篇：指定选择器、跳过页眉、切掉末尾赏析
python tools/import_page.py --file page.html --title 受戒 --author 汪曾祺 \
  --source "https://..." --selector "div#content" --start "正文首句" --cut "【问题】" --mode unwrap

# 批量：清单在 tools/import_manifest.json
python tools/import_batch.py
```

`--mode unwrap` 适合老式 `<pre>` 硬换行＋缩进排版；`--mode lines` 适合一段一个 `<p>` 的网页。
`--cut` 可多次，切掉末尾的赏析、试题、版权行；`--start` 跳到正文首句；`--cut-last` 用于目录与正文重名的篇名；`--end-trim` 剥掉残留后缀。

### 日语（青空文库）

```bash
python tools/import_aozora.py --file card.html --title 罗生门 --author 芥川龙之介 \
  --source "https://www.aozora.gr.jp/cards/000879/card127.html"
```

自动去掉 `<ruby>` 注音，保留正文。

### PDF 教材 / 扫描件

```bash
pdftotext -layout in.pdf out.txt    # 或 pdftotext in.pdf out.txt
python tools/import_page.py --file out.txt --title ... --start "正文首句" --cut "课后题起始" --mode lines
```

输出：

```text
Books/<书名>/
  source/original.txt   清洗后的正文，段落已合行，UTF-8
  source/raw.txt        原始下载文件（留档）
  meta.json             来源 / 作者 / 字数 / 校验结果 / sha256
```

## 藏书目录

```bash
python tools/build_catalog.py
```

- 给 `Books/` 下每本书加 `序号_书名` 前缀（如 `1_棋王`）
- 生成 `Books/总目录.txt`：中文 / 日文 / 外文分组，组内按作者、书名拼音排序
- 每次新增书后跑一次；会按当前排序整体重排编号
- 同时同步 `TXT全文/<编号_书名>.txt`（纯正文，方便直接读/复制）；你自己放进这个文件夹的其他 txt 不会被删

## 待导入（你自己搜罗的 txt / epub）

1. 把文件丢进 `待导入/`
2. 运行：

```bash
python tools/import_local.py
```

脚本会：提取正文 → 写入 `Books/<书名>/` → 原文件移到 `待导入/已处理/` → 自动重建目录和 `TXT全文/`。

命名建议：`书名.txt`、`书名-作者.txt`、`书名_作者.txt`；EPUB 优先读内嵌的 `dc:title` / `dc:creator`。书名已存在会跳过，不会覆盖。

## 书源分层（决定能不能抓）

| 类型 | 状态 | 说明 |
|---|---|---|
| 外文公版（欧·亨利、莫泊桑、奥斯汀…） | ✅ 已打通 | Gutendex 搜索 + Gutenberg 下载 |
| 中文公版 · 古籍 | ✅ 已打通 | 古腾堡中文库，含《論語》《紅樓夢》《史記》《聊齋》等 |
| 中文公版 · 民国（鲁迅） | ✅ 已打通 | 古腾堡有《吶喊》《徬徨》，可按篇拆；《徬徨》缺 3 篇 |
| 中文公版 · 郁达夫/老舍/许地山/赵树理 | ✅ 可抓 | 古腾堡没有，改走学术存档/官网 |
| DACHS 学术存档（海德堡大学镜像） | ✅ 主力 | 沈从文、汪曾祺、丁玲、沙汀、老舍等大量单篇；篇目靠站内搜索定位 |
| 中国作家网（中国作协） | ✅ 可用 | 官方转载，如郁达夫《春风沉醉的晚上》 |
| 杂志/出版社转载（搜狐号、网易号） | ⚠️ 可用 | 如《收获》文本、新华网同文；页尾赏析要切 |
| 豆瓣小组、教育类网站 | ⚠️ 兜底 | 仅在前述源都没有时使用；属于公开转载，个人学习用 |
| 教材删改版（组卷网/5156edu 等） | ❌ 不收 | 标「有删改」的不算全文，不写入 Books |
| 青空文库（日语公版） | ✅ 已打通 | 芥川、谷崎等；ruby 注音自动清理 |
| Wolne Lektury（波兰公版） | ✅ 已打通 | 舒尔茨等，切掉许可证尾块 |
| textlog.de / textarchiv.com（德语公版） | ✅ 已打通 | 卡夫卡《地洞》、茨威格《看不见的珍藏》 |
| 公版作品的中文译本 | ⚠️ 有版权 | 译者版权独立；需图书馆/购买，不能当公版原文抓 |
| 维基文库 | ❌ 不可用 | 本机直连超时，WebFetch 也被策略拦 |
| ctext（中国哲学书电子化计划） | ❌ 不可用 | 网页有 Cloudflare 人机验证，API 全文要注册 IP/付费 |
| 网络小说 | ⏳ 待接 | 计划包一层 so-novel |
| 你本地有 EPUB/PDF/剪贴文本 | ⏸ 待写 | 你提供文件，我负责清洗、切篇、校验 |

## 校验规则（宁可失败也不给半本书）

写入 `original.txt` 前必须全过；任一失败退出码 2，只留 `raw.txt` 供排查：

- 找到 Gutenberg 首尾标记
- 篇幅达标：英文 ≥ `--min-words`（默认 150），中文 ≥ `--min-chars`（默认 300 汉字；长篇请提高）
- 无替换字符 `�`
- 正文无残留 `Project Gutenberg` / 站名 / `Produced by` 致谢行
- 至少 2 个段落

`meta.json` 里的 `sha256` 用于判断重复抓取、下游是否换了版本；`script` 记录是简体、繁体还是拉丁字母。

## 接口约定

输出可直接喂给 `../Book_Agent_Pipeline/tools/prepare.py` 的 `--input`，无需二次整理：

```bash
python ../Book_Agent_Pipeline/tools/prepare.py \
  --input "Books/麦琪的礼物/source/original.txt" \
  --out "../Book_Agent_Pipeline/books/麦琪的礼物" --title "麦琪的礼物" --author "欧·亨利"
```

## 已知限制

- 中文用的是古腾堡的繁体原版，简体由 OpenCC（`opencc-python-reimplemented`）转，已装。
- 中文排版按「空行或行首缩进」断段；「右对齐日期行 + 篇名」会专门拆开。
- 单篇短篇小说不会切章；章节识别交给下游 `prepare.py`，避免两处逻辑打架。
- 古腾堡中文库只有 444 本；现代/当代单篇主要靠 DACHS 学术存档和官网转载。
- 部分网页源有少量 OCR/转录错字（如《麦子》的「补子/褂子」），未逐字校勘，引用前核对原书。
- 教材删改版不当作全文；《归去来》目前只有删改版，故未写入。
- Gutenberg 本机下载约 8 秒，长书更久；脚本内已带 3 次重试。
- DACHS 同一作品常有 `www.white-collar.net` 与 `white-collar.net` 两套路径，章节文件可能只在其中一套（如《妻妾成群》006/007 节只在非 www 路径）。
- 章节残缺的书（如《生死场》缺第 3 章、第 10/11 章为残页）不写入 Books，避免半本书。
- 抓取状态与来源明细见 `抓取报告.md`、`抓取报告-外国短篇.md`、`抓取报告-中国当代.md`；`_work/` 是临时页面缓存，可删。
