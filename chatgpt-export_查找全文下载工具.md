# 查找全文下载工具

> GitHub或者某些工具，或者哪里有没有能够捕获网上某些书全文的工具啥的？例如我输入羊脂球，他就能给我产出全文的文本文件

有这类工具，而且可以分成两种：一种直接找已有的整本书文本，另一种抓取网页正文并整理成 TXT。我查一下现成的 GitHub 项目，也用《羊脂球》看看实际能不能做到。

有！而且 GitHub 上确实有不少这类项目。📚

你想要的其实是一个 **「输入书名 → 自动搜索全网书源 → 抓取完整正文 → 合并成 TXT 文件」** 的工具。

我查了几个现成项目，其中最值得试的是 **So Novel**。

## 最推荐的 3 个工具

<box gap={3}>
  <row align=start gap={3}>
    <AsyncImage query="GitHub freeok so-novel terminal user interface novel downloader screenshot" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      <row align=center wrap="wrap" gap={2}>
        **1. <Link url={.url.uri} title="So Novel"/>**
        <badge color="success">最符合需求</badge>
      </row>
      GitHub 开源小说下载器，支持多书源搜索、批量抓取章节，并导出 TXT、EPUB、PDF。

      支持 Windows、macOS、Linux，可以下载现成安装包，不一定需要写代码。<Cite ref="turn865052view1"/>

      <text color="secondary" size="xs">适合：输入书名，搜索后直接下载全文</text>
      <text size="sm"><Link url="https://github.com/freeok/so-novel/releases" title="下载软件"/></text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align=start gap={3}>
    <AsyncImage query="Project Gutenberg ebook Boule de Suif Guy de Maupassant web page book cover" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **2. <Link url="https://www.gutenberg.org" title="Project Gutenberg（古腾堡计划）"/>**

      免费的公版电子书资源库，可以按书名、作者检索，直接下载 TXT 或 EPUB。

      已经收录莫泊桑的 *Boule de Suif*，但找到的版本是法语短篇集，不是中文译本。<Cite ref="turn865052view2"/>

      <text color="secondary" size="xs">适合：世界名著、英文及其他外语公版作品</text>
      <text size="sm"><Link url={.url.uri} title="查看《羊脂球》原文资源"/></text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align=start gap={3}>
    <AsyncImage query="Trafilatura Python web text extraction GitHub documentation" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **3. <Link url={.url.uri} title="Trafilatura"/>**

      Python 网页正文提取工具。给它一个网页地址，它可以剔除菜单、广告等无关内容，提取正文并保存成 TXT。

      本身不负责按书名寻找完整小说，多章节书籍需要额外编写抓取、合并逻辑。<Cite ref=""/>

      <text color="secondary" size="xs">适合：自己写自动化程序，批量建立书籍文本库</text>
    </box>
  </row>
</box>

## 以《羊脂球》为例

理想的操作流程是：

<box border radius="lg" padding={3} gap={2} align=center>
  <box background="surface-secondary" radius="md" padding={3} width="100%" align=center gap={1}>
    <icon name="search" color="secondary" size="lg"/>
    **输入书名：羊脂球**
  </box>
  <icon name="arrow-down" color="tertiary"/>
  <box background="surface-secondary" radius="md" padding={3} width="100%" align=center>
    <text weight="medium">搜索多个公开书源，识别作者及版本</text>
  </box>
  <icon name="arrow-down" color="tertiary"/>
  <box background="surface-secondary" radius="md" padding={3} width="100%" align=center>
    <text weight="medium">提取全文、清理杂项、合并章节</text>
  </box>
  <icon name="arrow-down" color="tertiary"/>
  <box border={{size:1,color:"success"}} radius="md" padding={3} width="100%" align=center gap={1}>
    <icon name="file-text" color="success" size="xl"/>
    **羊脂球.txt**
    <text color="secondary" size="xs">UTF-8 纯文本文件</text>
  </box>
</box>

我还查了《羊脂球》的实际资源情况：

- **法语原文：** Project Gutenberg 已有可下载文本。
- **英文译文：** 英文维基文库有可阅读的完整单篇文本。<Cite ref=""/>
- **中文译文：** 中文维基文库列出了李青崖、赵少侯两个译本，但目前查到的页面只是版本索引，未提供可直接提取的中文全文。<Cite refs={["turn865052view0","turn217537view0"]}/>

有个关键区别：**莫泊桑的原作已经进入公有领域，不意味着所有现代中文译本也都不受版权保护。** 所以工具能否获取全文，还取决于公开书源是否有对应版本及其授权情况。

## 如果你想实现真正的「输入书名就生成 TXT」

我更建议做成一个小型自动化工具，而不只是安装爬虫：

1. 根据书名和作者，优先搜索公版或已授权书源。
2. 自动判断找到的是全文、节选还是书评。
3. 下载各章节，去广告、去重、按顺序合并。
4. 输出 `书名.txt`，同时记录作者、译者、来源和完整性。

这样不仅适合《羊脂球》，也适合后续批量收集经典文学文本。

**我想确认一个关键点：你主要想抓取哪一类书？**

{@body const [type,setType] = DIL.useState("classic")}
<box gap={2}>
  <radio-group direction="col" value={type} onChange={setType}>
    <radio value="classic">世界文学名著（《羊脂球》《变形记》《傲慢与偏见》等）</radio>
    <radio value="chinese">中文文学作品（鲁迅、张爱玲等）</radio>
    <radio value="modern">各种现代出版书籍、畅销书</radio>
    <radio value="all">都需要，最好输入任何书名就能自动找全文</radio>
  </radio-group>
  <button block onClick={()=>GenUI.issueNewTurn(({classic:"我主要想收集世界文学名著的全文 TXT，请推荐最适合的工具和具体使用步骤。",chinese:"我主要想收集中文文学作品的全文 TXT，请推荐工具和具体使用步骤。",modern:"我主要想收集现代出版书籍，请说明合法可用的全文获取工具和使用方式。",all:"我想实现输入任意书名，自动搜索允许获取的书源，尽可能找到全文并生成 TXT 的工具，请给我一套具体方案。"}[type]))}>按我的需求推荐具体方案 <icon name="arrow-right" inline/></button>
</box>

-----

> 我想实现输入任意书名，自动搜索允许获取的书源，尽可能找到全文并生成 TXT 的工具，请给我一套具体方案。

我会按“能真正落地”的方式来设计：先核实哪些书源有公开接口、哪些工具能提取正文，再给你一套从输入书名到生成 TXT 的自动化方案，并明确哪些书能拿到全文、哪些只能返回合法获取途径。

我建议你做一个 **「全网书籍搜索 + 合法全文获取 + 自动 TXT 转换」工具**。📚

目标是：你输入《羊脂球》《百年孤独》《傲慢与偏见》或者任何一本书的名字，程序自动搜索多个书源，找到可以合法下载的完整版本就生成 `.txt`；找不到则返回可阅读、借阅或购买的来源，而不是伪造全文。

这件事完全可以用 Python + GitHub 上的开源项目实现，而且不需要自己训练 AI。

## 一、推荐的整体架构

<box border radius="xl" padding={3} gap={2}>
  <box background="surface-secondary" radius="lg" padding={3} align=center gap={1}>
    <icon name="book-open-text" color="default" size="lg"/>
    **输入任意书名**
    <text color="secondary" size="xs">支持中文、英文、法文等</text>
  </box>
  <row justify="center">
    <icon name="arrow-down" color="tertiary" size="lg"/>
  </row>
  <grid columns={2} gap={2}>
    {#each ["书名标准化","作者与版本识别","多书源并行搜索","授权和下载检查"] as item,i}
      <grid-item>
        <box background="surface" border radius="md" padding={3} align=center gap={1}>
          <icon name={["languages","book-user","search","shield-check"][i]} color="secondary"/>
          <text size="xs" weight="medium" textAlign="center">{item}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <row justify="center">
    <icon name="arrow-down" color="tertiary" size="lg"/>
  </row>
  <box background="surface-secondary" radius="lg" padding={3} align=center gap={1}>
    **下载原始文件 + 提取正文**
    <text color="secondary" size="xs">TXT / EPUB / 合法开放网页</text>
  </box>
  <row justify="center">
    <icon name="arrow-down" color="tertiary" size="lg"/>
  </row>
  <grid columns={2} gap={2}>
    <grid-item>
      <box border={{size:1,color:"success"}} radius="md" padding={3} align=center gap={1}>
        <icon name="file-check" color="success" size="lg"/>
        <text weight="medium" size="sm">获取成功</text>
        <text size="xs" color="secondary" textAlign="center">书名.txt + 来源信息</text>
      </box>
    </grid-item>
    <grid-item>
      <box border radius="md" padding={3} align=center gap={1}>
        <icon name="external-link" color="secondary" size="lg"/>
        <text weight="medium" size="sm">未找到合法全文</text>
        <text size="xs" color="secondary" textAlign="center">返回可用来源链接</text>
      </box>
    </grid-item>
  </grid>
</box>

## 二、具体接入哪些书源？

| 书源 | 主要用途 | 自动化程度 |
|---|---|---|
| <Link url="https://gutendex.com/" title="Gutendex"/> | 搜索古腾堡公版电子书 | 高，提供 JSON API |
| <Link url="https://www.gutenberg.org/" title="Project Gutenberg"/> | 下载原版 TXT / EPUB | 高 |
| <Link url="https://zh.wikisource.org/" title="中文维基文库"/> | 查找公开授权的中文文学文本 | 中，需要处理多页面 |
| <Link url="https://openlibrary.org/" title="Open Library"/> | 识别书名、作者及版次，查找借阅信息 | 高，可搜索元数据 |
| <Link url="https://developers.google.com/books/docs/v1/using" title="Google Books API"/> | 搜索更多书籍，判断是否开放全文 | 高，但不保证可下载 |
| 自己授权的网站 | 下载明确允许保存的书籍 | 取决于网站 |

其中 Gutendex 可以根据书名、作者搜索古腾堡目录并取得文件格式链接；Google Books 能返回书籍访问状态，但“可全文浏览”不一定意味着可以批量下载。<Cite refs={["",""]}/>

### 核心技术栈

- **Python + requests**：访问书籍 API。
- **EbookLib**：将 EPUB 中的各章节转换为文本。
- **BeautifulSoup / Trafilatura**：提取授权网页的正文。
- **RapidFuzz**：模糊匹配中文、英文书名及不同版本。
- **SQLite**：记录搜索结果，避免重复下载。

Trafilatura 本身已经支持提取网页主文本并输出 TXT，非常适合作为这一系统的网页处理组件。<Cite ref=""/>

## 三、先做一个能运行的版本

第一版我建议先实现这几个功能：输入书名、自动查找古腾堡资源、匹配完整书籍、下载 TXT、保存来源。找不到时再查询 Google Books。

下面的程序可以直接在电脑上运行。

### 第一步：安装依赖

在终端运行：

```bash
pip install requests
```

### 第二步：创建 `book_finder.py`

<CodeBlock language="python" editable>
import requests
from pathlib import Path
from difflib import SequenceMatcher
import re
import json
import unicodedata

OUT = Path("books")
OUT.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "BookFinder/1.0"}
TIMEOUT = 20
MAX_BYTES = 30 * 1024 * 1024


def clean_name(name):
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name[:100].strip() or "book"


def normalize(text):
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\W+", "", text).casefold()


def similarity(a, b):
    return SequenceMatcher(
        None, normalize(a), normalize(b)
    ).ratio()


def search_gutenberg(query):
    r = requests.get(
        "https://gutendex.com/books",
        params={"search": query},
        headers=HEADERS,
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.json().get("results", [])


def find_txt(book):
    formats = book.get("formats", {})
    candidates = [
        (mime, url)
        for mime, url in formats.items()
        if mime.startswith("text/plain")
    ]
    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            "utf-8" not in item[0].lower(),
            ".zip" in item[1].lower()
        )
    )
    for mime, url in candidates:
        if ".zip" not in url.lower():
            return url
    return None


def download_txt(book, url):
    with requests.get(
        url, headers=HEADERS,
        timeout=TIMEOUT, stream=True
    ) as r:
        r.raise_for_status()
        chunks = []
        total = 0
        for chunk in r.iter_content(65536):
            total += len(chunk)
            if total > MAX_BYTES:
                raise ValueError("文件超出大小限制")
            chunks.append(chunk)

    raw = b"".join(chunks)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    filename = clean_name(book["title"])
    path = OUT / f"{filename}.txt"
    path.write_text(text, encoding="utf-8")

    metadata = {
        "title": book["title"],
        "authors": [
            a["name"] for a in book.get("authors", [])
        ],
        "source": url,
        "gutenberg_id": book["id"],
        "language": book.get("languages"),
        "status": "downloaded",
        "note": "请自行确认使用地区的版权状态"
    }
    (OUT / f"{filename}.json").write_text(
        json.dumps(
            metadata, ensure_ascii=False, indent=2
        ),
        encoding="utf-8"
    )
    return path


def google_books(query):
    r = requests.get(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": f"intitle:{query}", "maxResults": 5},
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.json().get("items", [])


def main():
    query = input("请输入书名：").strip()
    if not query:
        return

    print("正在搜索 Project Gutenberg...")
    try:
        results = search_gutenberg(query)
    except requests.RequestException as e:
        print("古腾堡搜索失败：", e)
        results = []

    matches = sorted(
        results,
        key=lambda b: similarity(query, b["title"]),
        reverse=True
    )

    if matches:
        print("\n找到以下候选书籍：")
        for i, book in enumerate(matches[:10], 1):
            author = ", ".join(
                a["name"] for a in book.get("authors", [])
            )
            flag = "TXT可用" if find_txt(book) else "无TXT"
            print(f"{i}. {book['title']} | {author} | {flag}")

        choice = input(
            "\n选择编号下载（回车跳过）："
        ).strip()
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= min(10, len(matches)):
                book = matches[n - 1]
                url = find_txt(book)
                if url:
                    try:
                        path = download_txt(book, url)
                        print("已保存：", path)
                        return
                    except Exception as e:
                        print("下载失败：", e)
                else:
                    print("此版本没有直接可用的TXT")

    print("\n查询 Google Books 的可用版本...")
    try:
        for item in google_books(query):
            info = item.get("volumeInfo", {})
            access = item.get("accessInfo", {})
            print(
                info.get("title"),
                "| 可见性:", access.get("viewability"),
                "|", info.get("infoLink", "")
            )
    except requests.RequestException as e:
        print("Google Books 查询失败：", e)

    print("\n尚未获得合法可下载的TXT全文。")


if __name__ == "__main__":
    main()
</CodeBlock>

### 第三步：运行

```bash
python book_finder.py
```

例如输入：

```text
Pride and Prejudice
```

程序会列出匹配的作品，选择版本后，把可用的 TXT 文件保存至 `books/` 文件夹，同时生成一个 JSON 文件记录来源。

这个版本的适用范围要说清楚：**它是可运行的基础版，而不是已经实现全网搜索的最终版**。目前只自动下载古腾堡提供的 TXT，不会抓取受限页面；古腾堡没有的中文书名也可能因为缺少跨语言匹配而搜不到。代码还没有经过我在当前环境中对线上接口的端到端测试。

## 四、下一步把它升级成真正的全自动工具

最值得投入的是以下四项升级：

| 优先级 | 功能 | 解决什么问题 |
|---|---|---|
| P0 | 多语言书名识别 | 输入《羊脂球》，能识别 *Boule de Suif* 及莫泊桑 |
| P0 | 中文维基文库接入 | 增加中文公版文学的覆盖率 |
| P1 | EPUB → TXT 转换 | 书源没有 TXT、只有 EPUB 时也能输出 |
| P1 | 全文完整性检测 | 检查是否缺章节、只有试看或混入大量广告 |
| P2 | 网页界面与批量任务 | 一次输入几十本书，自动生成文本库 |

还有一个必须做的设计：**把“发现书籍”和“允许下载”分开判断。** 搜索结果即使公开可见，也不代表有权批量抓取。对于版权尚未到期、仅开放预览或要求借阅的版本，程序应保留来源链接，而不是绕过限制。

## 五、最终成品可以长这样

{@body const [book,setBook] = DIL.useState("羊脂球")}
{@body const [lang,setLang] = DIL.useState("zh")}
<box border radius="xl" padding={3} gap={3}>
  <row align="center" gap={2}>
    <icon name="library-big" size="lg"/>
    <box flex="1" gap="0">
      <title size="lg">BookFinder</title>
      <caption>书籍全文智能检索器 · 界面原型</caption>
    </box>
    <badge>V1 规划</badge>
  </row>
  <box gap={1}>
    <label>书籍名称</label>
    <input value={book} onChange={setBook} placeholder="例如：羊脂球、傲慢与偏见"/>
  </box>
  <box gap={1}>
    <label>优先语言</label>
    <radio-group direction="row" value={lang} onChange={setLang}>
      <radio value="zh">中文</radio>
      <radio value="en">英文</radio>
      <radio value="any">不限</radio>
    </radio-group>
  </box>
  <box background="surface-secondary" radius="md" padding={3} gap={2}>
    <row align="center" justify="between">
      <text weight="medium" size="sm">计划搜索的书源</text>
      <text size="xs" color="secondary">4 个</text>
    </row>
    <grid columns={2} gap={2}>
      {#each ["Project Gutenberg","中文维基文库","Open Library","Google Books"] as source}
        <grid-item>
          <row align="center" gap={2}>
            <icon name="check-circle-2" color="secondary" size="sm"/>
            <text size="xs">{source}</text>
          </row>
        </grid-item>
      {/each}
    </grid>
  </box>
  <button block disabled={!book.trim()} onClick={()=>GenUI.issueNewTurn(`请进一步设计 BookFinder 完整版，针对“${book}”，优先语言${lang==="zh"?"中文":lang==="en"?"英文":"不限"}。重点实现多语言书名识别、合法公开书源检索、EPUB与网页转TXT、全文完整性检查，并给出完整项目代码及安装步骤。`)}>
    <icon name="search" inline/> 生成这本书的搜索与下载方案
  </button>
  <caption>这是交互界面示意，尚未连接书源，点击后会继续生成实现方案。</caption>
</box>

**我的建议是先做 Python 命令行版，再封装成 Streamlit 网页。** 这样你不必每次打开 GitHub，也不必自己找网址，打开本地网页输入书名即可。

最终这套工具能做到的，不是保证“任意书都能下载”，而是**尽可能找到每本书合法可获取的完整文本，并把重复的查找、筛选、转换工作自动化**。对于经典文学和已开放授权的电子书，这是一条非常实用的路线。