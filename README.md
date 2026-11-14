# 东莞市湖南攸县商会 · 官网（莞香攸商）

一个零依赖的纯静态多页站点，为「东莞市湖南攸县商会」（品牌：莞香攸商）构建。直接推到 GitHub Pages 即可访问，不需要 Node、不需要构建命令、不需要数据库。

- 站点根目录：本目录（`guanxiang-youshang-site/`）
- 页面数量：7 个可索引主页面 + 4 篇动态详情 = 11 个可索引页面，另有 1 个 404 页
- 技术栈：HTML + CSS + 原生 JavaScript（一个 `style.css`、一个 `main.js`）
- 图片：本地素材，全部相对路径引用，无外链依赖

---

## 一、目录结构

```
guanxiang-youshang-site/
├── index.html            首页（Canvas 双城连线首屏、概况、动态、品牌、家乡、CTA）
├── about.html            商会简介（登记信息表、服务、发展历程时间轴、组织架构、会址）
├── news.html             商会动态列表（按类别筛选）
├── news/
│   ├── 2022-special-school-donation.html   公益捐赠（2022-09-30）
│   ├── 2023-youxian-outreach.html          统战部走访（2023-05-29）
│   ├── 2023-logistics-line.html            物流直达班线（2023-03）
│   └── 2015-foundation.html                成立与品牌沿革（2015-09-11）
├── members.html          会员服务（六项服务、对接流程、名录说明、FAQ）
├── youxian.html          家乡攸县（县域数据、五件宝、山水人文、在外攸县人）
├── join.html             加入商会（条件、材料清单、五步流程、会费说明）
├── contact.html          联系我们（会址、公众号、登记信息、到访指引）
├── 404.html              404 页（自带内联样式，子路径部署自动修正链接）
├── assets/
│   ├── logo.png          480×480 透明底标志（hero、分享图用）
│   ├── logo-mark.png     256×256 透明底标志（导航、页脚）
│   ├── logo-original.jpg 用户提供的原始 LOGO
│   ├── favicon-64.png    站点图标
│   ├── apple-touch-icon.png
│   └── img/
│       ├── dongguan.jpg        东莞城市（关于页）
│       ├── youxian-lake.jpg    酒仙湖（家乡页）
│       ├── xianggan.jpg        攸县香干（五件宝）
│       ├── office.jpg          园区办公场景（到访/会址）
│       └── og-cover.jpg        社交分享卡 1200×630
├── css/style.css         全站样式（含响应式、低动效降级）
├── js/main.js            交互（渐显、抽屉、复制、筛选、FAQ、Canvas 首屏）
├── tools/
│   ├── prepare_assets.py 素材生成脚本（下载图 + LOGO 去白底 + 分享卡）
│   ├── check_site.py     站点自检（内链、标签闭合、SEO 头、JSON-LD、sitemap、CSS 类名覆盖）
│   └── set-domain.ps1    域名占位符一键替换 + 生成 CNAME
├── sitemap.xml           站点地图（含 __SITE_DOMAIN__ 占位符）
├── robots.txt            抓取规则（含 Sitemap 地址）
├── .nojekyll             关闭 Jekyll 处理，保证下划线开头文件不被忽略
├── CNAME.example         CNAME 模板（改名后使用）
└── README.md             本文件
```

---

## 二、本地预览

任选一种：

1. **直接双击 `index.html`** —— 相对路径引用，页面与图片都能正常显示。404 页在 `file://` 下不会生效，属正常。
2. **起一个本地服务**（推荐，能验证 404、sitemap、canonical 路径）：

```powershell
cd C:\Users\SAMSUNG\Doubao\chats\2026-11-14\new-chat-1\guanxiang-youshang-site
python -m http.server 8080
# 浏览器打开 http://localhost:8080/
```

---

## 三、发布到 GitHub Pages

### 当前状态：已上线

| 项目 | 地址 |
| --- | --- |
| 线上站点 | https://unipiwei-blip.github.io/guanxiang-youshang-site/ |
| 代码仓库 | https://github.com/unipiwei-blip/guanxiang-youshang-site |

仓库为公开仓库，Pages 已开启（`main` 分支 / root，Enforce HTTPS 已勾选），全站地址已由 `tools/set-domain.ps1` 替换为上面的项目页地址，并记录在 `.site-base` 中。

### 以后怎么更新

```powershell
cd C:\Users\SAMSUNG\Doubao\chats\2026-11-14\new-chat-1\guanxiang-youshang-site
git add -A
git commit -m "更新：补充 2024 年会员走访动态"
git push
```

推送后 1–2 分钟内自动重新构建，无需任何额外操作。

### 如果换一个仓库或换一个账号

```powershell
git init
git add .
git commit -m "东莞市湖南攸县商会官网：初始版本"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

然后 **Settings → Pages**：Source 选 `Deploy from a branch`，Branch 选 `main`，目录选 `/ (root)`。

两种访问形态：

| 形态 | 地址 | 需要做的事 |
| --- | --- | --- |
| 项目页（当前形态） | `https://<用户名>.github.io/<仓库名>/` | 运行 `set-domain.ps1` 传子路径；**不要**建 CNAME |
| 自定义域名 | `https://www.你的域名.com/` | 运行 `set-domain.ps1` 传域名；自动生成 CNAME；配 DNS |

> `index.html` 必须是站点根目录下的文件名，这一点与普通单页交付物不同，是 GitHub Pages 的硬性要求。

### 替换站点地址（注册好域名后）

站点所有 `canonical`、`og:url`、结构化数据、`sitemap.xml`、`robots.txt` 里的地址，都由 `.site-base` 记录、由脚本统一维护。换域名只需要一条命令：

```powershell
# 换成自定义域名（会自动把旧的项目页地址全部替换掉，并生成 CNAME）
pwsh tools/set-domain.ps1 -Domain www.gxyoushang.com -Backup
```

脚本行为：

- 自动去掉 `https://` 前缀与结尾斜杠，统一补 `https://`
- 扫描全站 `.html` / `.xml` / `.txt`：既替换 `__SITE_DOMAIN__` 占位符，也替换 `.site-base` 里记录的旧地址，所以**可以反复换域名，不会残留上一版的链接**
- 域名形态（不含 `/`）时写入 `CNAME`；子路径形态时提示不要使用 CNAME
- 运行结果写回 `.site-base`，作为下一次替换的基准
- `-Backup` 会把即将修改的文件复制到 `_backup/domain-<时间戳>/`
- 地址没变化时直接跳过，不会误改文件

### 4. 自定义域名 DNS

在域名服务商处配置：

- `www` → `CNAME` → `<你的用户名>.github.io`
- 裸域 `@` → `A` → `185.199.108.153`、`185.199.109.153`、`185.199.110.153`、`185.199.111.153`（GitHub Pages 官方四个 IP）

保存后在 GitHub Pages 页面勾选 **Enforce HTTPS**。证书签发通常需要几分钟到数小时。

### 5. 关于备案

GitHub Pages 服务器在境外，**不需要 ICP 备案**。页脚目前保留了「粤ICP备（待备案后填写）号」占位文本：

- 使用 GitHub Pages：建议把这行删除，或替换为你的域名；
- 后续迁到中国大陆服务器：按实际备案号填写。

---

## 四、内容维护

### 新增一条动态

1. 复制 `news/2015-foundation.html` 作为模板，改文件名（建议英文 slug + 日期，便于长期维护）；
2. 修改 `<title>`、`<meta name="description">`、`canonical`、`og:*` 与页面里的 `NewsArticle` 结构化数据；
3. 正文放在 `<article class="prose">` 内，相关阅读放在 `.aside-card`；
4. 在 `news.html` 的列表里加一张 `.card`，务必带上 `data-cat`（`charity` / `gov` / `industry` / `brand`），否则筛选会漏；
5. 把新地址追加到 `sitemap.xml`；
6. 更新 `news.html` 里 `CollectionPage` 的 `hasPart` 数组。

### 修改文案与图片

- 纯文案：直接改对应 `.html`
- 配色/字号/间距：改 `css/style.css` 顶部的 `:root` 令牌（`--ink`、`--red`、`--rice`、`--gold` 等），不要逐页硬编码颜色
- 图片：替换 `assets/img/` 下的同名文件即可，建议保持 3:4 ~ 21:9 的比例、长边 ≤ 1800px
- 需要重新生成素材（换图、调 LOGO 透明度、改分享卡文案）：编辑 `tools/prepare_assets.py` 后运行 `python tools/prepare_assets.py`，脚本会跳过已存在的文件

### 改完之后跑一遍自检

```powershell
python tools/check_site.py
```

它会检查：每个页面的本地 `href/src` 是否都存在、HTML 标签是否闭合、`h1` 是否唯一、`title/description/canonical/og:*` 是否齐全、JSON-LD 能否解析、`sitemap.xml` 里的地址是否都有对应文件、页面用到的 class 是否都在 `style.css` 里有定义。退出码 0 表示无错误。**新增或改名页面后务必跑一次**，这一步能拦掉 404 死链和筛选失效。

---

## 五、SEO 已做的处理

| 项目 | 实现 |
| --- | --- |
| 标题与描述 | 12 个页面各有独立的 `title` 与 `description`，无重复 |
| canonical | 每页均声明，统一指向正式地址 |
| 结构化数据 | 首页 `Organization`（含统一社会信用代码、成立日期、地址）；动态列表 `CollectionPage`；详情页 `NewsArticle`；会员页 `FAQPage`；联系我们 `ContactPage`；简介页 `BreadcrumbList` |
| 社交分享 | `og:title/description/image/url` + `twitter:card`，分享图 1200×630 |
| 抓取 | `robots.txt` 放行全站、屏蔽 404；`sitemap.xml` 列 11 条主地址，`lastmod` 按真实日期填写 |
| 语义结构 | 每页单一 `h1`；面包屑；`aria-label`；`skip` 跳转链接；图片均有 `alt` |
| 本地化 | `lang="zh-CN"`；地名、县情、特产等长尾词自然分布在正文与标题中 |
| 性能 | 无外部字体、无第三方脚本；图片 `loading="lazy"` 且带 `width/height`；CSS/JS 各一个文件 |

上线后建议：在 [Google Search Console](https://search.google.com/search-console) 与 [Bing Webmaster](https://www.bing.com/webmasters) 提交 `sitemap.xml`；百度搜索资源平台亦可用「普通收录 → sitemap」提交。

---

## 六、设计说明（便于后续接手者不改坏）

- **视觉母题「双城连线」**：攸县与东莞两个节点，用红色虚线贝塞尔曲线连接，首屏 Canvas 上有一个沿曲线移动的信号点。它对应的是商会的地理本质，不是装饰。
- **配色**：`--ink` 蓝黑墨（`#0e1b26`）、`--rice` 冷浅灰（`#f5f8fa`）、`--red` 取自 LOGO 的中国红、`--gold` 作少量提亮；底色为纯白，没有近黑大色块，也没有米黄底。没有紫蓝渐变、没有玻璃拟态、没有满屏卡片。
- **字体**：只用系统字体栈（PingFang SC / Microsoft YaHei / 思源黑体），靠字重、字距与 `clamp()` 字号建立层级，避免外部字体在境内加载失败。
- **品牌锁定（页头 / 抽屉）**：主名固定为「东莞市湖南攸县商会」，字号 `clamp(1.02rem, 1.3vw, 1.24rem)`；下方副行为英文 `DONGGUAN YOUSHANG CHAMBER`，不再把「莞香攸商」排在主名上方。窄屏（≤600px）隐藏副行，保证主名一行放得下。
- **动效**：`.rv` 元素进入视口渐显；首屏标题裁切上推；字带 marquee；卡片角标 hover；滚动进度条；首屏 Canvas 粒子网络（≤42 节点、离屏暂停）。全部在 `prefers-reduced-motion: reduce` 下退化为静态画面。
- **窄屏优先**：CSS 以 375px 为基准写，`@media (min-width: ...)` 逐级增强；多列栅格显式指定列数，不留「3 + 1」的孤儿卡片。
- **可访问性**：`:focus-visible` 可见描边；`aria-expanded` / `aria-pressed` 同步状态；触摸目标 ≥ 44px。

---

## 七、需要商会最终确认或补充的信息

站点当前**只写可核实的公开信息**，以下字段刻意留空，请确认后再补：

1. **官方联系电话 / 邮箱 / 秘书处对接人** —— 联系页目前只提供「会址 + 微信公众号」，并明确写明「不公布固定电话，避免号码过期误事」。拿到号码后可加进 `contact.html` 的 `.contact-card`，并同步 `ContactPage` 结构化数据。
2. **现任会长、理事会与监事会名单** —— 简介页只写了登记法定代表人「陈力平」与章程层面的组织架构，并注明「名单以秘书处公布为准」。确认后可新增名录区块。
3. **会员数量与是否公开会员名录** —— 会员服务页已说明「未逐条公开」的理由。若要公开，需要会员授权，并逐条核对名称。
4. **公众号命名口径** —— 站点品牌统一用「莞香攸商」（与商标、LOGO 一致），并在联系页说明公众号登记名为「莞湘攸商」。若商会希望反过来，需要全站替换。
5. **备案号** —— 页脚占位「粤ICP备（待备案后填写）号」。
6. **正式域名与仓库名** —— 决定 `set-domain.ps1` 的参数与 `CNAME`。

另外，以下内容属于示意，已在页面标注「示意场景图」，替换为真实照片会更可信：

- `assets/img/dongguan.jpg`（东莞城市）
- `assets/img/youxian-lake.jpg`（酒仙湖）
- `assets/img/xianggan.jpg`（攸县香干）
- `assets/img/office.jpg`（园区办公场景）

---

## 八、资料来源

页面中的事实性内容来自以下公开渠道，正文已按来源标注：

| 内容 | 来源 |
| --- | --- |
| 登记信息（成立日期、信用代码、会址、法定代表人、业务范围） | 广东省社会组织管理局社会组织公示、东莞市民政局登记信息 |
| 商标（第 35 / 36 类、申请与注册日期） | 商标注册公告、企业信息公示 |
| 平台公司 | 国家企业信用信息公示系统 |
| 2022 年公益捐赠 | 攸县新闻网报道 `m-youxian-xnhcloud.voc.com.cn/content/4918242` |
| 2023 年统战部走访 | 攸县新闻网报道 `m-youxian-xnhcloud.voc.com.cn/content/6878968` |
| 2023 年物流直达班线 | 攸县人民政府门户网站 `hnyx.gov.cn/c6935/20230313/i2017552.html` |
| 攸县县情、人口、GDP、地理标志、景区 | 攸县人民政府门户网站公开信息（2025 年数据） |
| 在外攸县人行业数据 | 媒体公开报道与异地商会公开统计（页面已注明仅作背景参考） |

> 维护提醒：政府网站的栏目路径与报道链接可能调整。若外链失效，请更新对应页面底部「原文链接」，或删除该链接后保留文字来源说明。

---

## 九、已知限制

- 无后端，因此**没有在线入会表单**、没有会员登录、没有站内搜索；咨询统一走公众号留言与到访。
- 无支付能力，会费缴纳按商会既有渠道，站内只做说明与防诈骗提醒。
- 动态列表为手工维护的静态列表，新增条目需同时更新 `news.html` 与 `sitemap.xml`。
- 未接入统计代码。若需访问分析，建议加轻量的、可关闭的方案（如自建 Umami 或 Plausible），不要塞入多个第三方追踪脚本。

---

© 东莞市湖南攸县商会 · 本站内容与图片版权归商会所有。
