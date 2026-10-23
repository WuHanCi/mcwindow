<p align="center">
  <img src="web/mark.svg" width="72" height="72" alt="麦麦空档图标">
</p>

<h1 align="center">麦麦空档 McWindow</h1>

<p align="center"><strong>想吃麦当劳，也想从容一点。</strong></p>
<p align="center">选一份用得上的优惠，把出发、吃饭和返回的时间安排好。</p>

<p align="center">
  <a href="#preview">看看效果</a> ·
  <a href="#quick-start">快速开始</a> ·
  <a href="#my-coupons">用自己的优惠</a> ·
  <a href="#agent">交给 Agent</a> ·
  <a href="https://github.com/WuHanCi/mcwindow/issues">反馈与建议</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square" alt="Python 3.9 或更新版本">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-263f35?style=flat-square" alt="MIT License"></a>
</p>

想在下一节课前吃顿麦当劳，翻了几张优惠券，却还拿不准吃完能不能赶回来。

麦麦空档是一个在本机运行的麦当劳用餐安排工具。告诉它你想花多少钱、路上要多久、几点得回来，再把想用的优惠放进来，就能看到哪些选择赶得上，以及这一趟该怎么安排。

少一点边吃边看表，多一点好好吃饭的时间。

<a id="preview"></a>

## 先看一顿饭怎么安排

> 现在 11:50，13:00 要上课。预算 25 元，单程 8 分钟，想留 20 分钟好好吃饭。

再加上 6 分钟排队预留、10 分钟回程缓冲，麦麦空档会把优惠和这段空档放在一起比较：

| 选择 | 金额 | 这次用得上吗？ |
| --- | --- | --- |
| 午间轻松组合 A | ¥19.90 | 可以，按「花得更少」优先推荐 |
| 午间分享组合 B | ¥24.90 | 可以，作为另一个选择 |
| 午后小食组合 | ¥15.90 | 14:00 才开始可用，赶不上这次空档 |
| 早间元气组合 | ¥12.90 | 已过早餐优惠的有效时间 |
| 丰盛搭配组合 | ¥32.90 | 超出预算 ¥7.90 |

选好之后，出发到返回的安排也一目了然：

```text
11:50  出发
11:58  到店，预留 6 分钟排队
12:04  点单，留 20 分钟吃饭
12:24  吃完返程
12:32  返回，再留 10 分钟缓冲
12:42  缓冲结束，距离上课还有 18 分钟
```

这一顿预计花 **¥19.90**，预算还剩 **¥5.10**。喜欢这个安排，就导出到日历；想换一个，也能直接比较。

以上为内置演示数据，日期固定为 2026-10-23。[完整示例结果](examples/demo-plan.md) · [示例输入](examples/demo-request.json)

<a id="quick-start"></a>

## 先试一次

准备好 **Python 3.9 或更新版本**即可，无需安装第三方依赖，也不用先申请 Token。

```bash
git clone https://github.com/WuHanCi/mcwindow.git
cd mcwindow
python3 app.py
```

浏览器打开 **<http://127.0.0.1:8765>**。在 Mac 上，也可以下载并解压[项目源码](https://github.com/WuHanCi/mcwindow/archive/refs/heads/main.zip)，双击文件夹里的 `start.command` 启动。

页面默认载入上面的演示。你可以先试这三步：

1. 点击「安排一下」，看看预算内的选择和完整时间线。
2. 把「下次安排开始时间」改为当天 12:20，再算一次，看看时间不够时的结果。
3. 改回 13:00，选一份喜欢的安排，导出日历或 Markdown。

端口被占用时，运行 `python3 app.py --port 8766`，改用 <http://127.0.0.1:8766>。在终端按 **Control+C** 停止服务。

## 按你的节奏来

- **先留出吃饭的时间。** 路程、排队、用餐和缓冲都由你填写。课间只有半小时，或午休想坐久一点，都可以重新算。
- **省钱或早点回来，你来选。** 按「花得更少」或「更早返回」排序，在可行安排里挑合适的一份。
- **每个选择都有理由。** 优惠的有效期、每日可用时段和预算一起检查；没选上的，也能看到原因。
- **把安排带走。** 页面展示完整时间线，也支持导出 `.ics` 日历和 Markdown，方便放进接下来的日程。

<a id="my-coupons"></a>

## 用上自己的优惠

麦麦空档可以连接**麦当劳官方 MCP**，查询已有优惠券、可领取优惠和营销活动。查询后，在页面里整理想比较的优惠，再安排饭点。

1. 前往[麦当劳开放平台](https://open.mcd.cn/mcp)，登录后在控制台激活 Token。
2. 打开页面里的「MCP 连接」，输入 Token，点击「连接并获取工具」。
3. 选择查询工具，按照页面展示的参数定义填写并查询。
4. 在返回结果下点击「依据查询结果建立候选」，填入名称、实际应付价格、有效期和可用时段。核对门店、就餐方式与领取状态后，勾选「价格和适用条件已确认」并保存。
5. 回到「空档规划」，填好自己的时间和预算，点击「安排一下」。

| 想查什么 | 选择的工具 |
| --- | --- |
| 我的卡包里有哪些券 | `query-my-coupons` |
| 还有哪些券可以领取 | `available-coupons` |
| 最近有哪些活动 | `campaign-calendar` |
| 服务器当前时间 | `now-time-info` |

也可以在「优惠候选」中手动添加。每份优惠都可以修改价格、日期、每日时段和使用条件，确认后再参与比较。

服务运行在 `127.0.0.1`；Token 与查询结果保留在当前页面会话中，刷新后重新连接。[MCP 配置与联调记录](MCP_INTEGRATION.md)

<a id="agent"></a>

## 也可以交给 Agent

项目自带 [Agent Skill](SKILL.md)。把整个项目作为技能目录交给支持 Agent Skills 的客户端，再配置麦当劳 MCP 连接，就可以从一句日常需求开始：

> 我 13:00 要上课，这顿想花 25 元以内，去麦当劳单程大概 8 分钟。帮我看看手里的券有没有合适的，留 20 分钟吃饭，再留 10 分钟缓冲。

Skill 会补问影响结果的缺失信息，查询优惠，协助核对并整理价格与时段，再调用项目里的规划器计算，给出推荐和时间线。

MCP 客户端配置见 [mcp-config.example.json](mcp-config.example.json)，其中 `${MCD_MCP_TOKEN}` 对应你的本机环境变量或客户端配置。

### 命令行用法

不启动页面，也能先跑一次演示：

```bash
python3 scripts/plan.py --demo
```

以示例 JSON 为起点，导出规划、日历和报告：

```bash
mkdir -p private
python3 scripts/plan.py \
  --input examples/demo-request.json \
  --output private/plan.json \
  --ics private/meal.ics \
  --report private/plan.md
```

把 `--input` 换成自己的 JSON 文件即可。[输入格式](references/input-schema.md) · [示例日历](examples/demo.ics)

<a id="development"></a>

## 开发与文档

页面、CLI 和 Skill 共用同一套 Python 规划逻辑：先算到店与排队时间，再寻找优惠可用时段内的点单时间，最后检查用餐、返回和缓冲能否在下次安排前完成。价格按整数分比较，支持跨午夜时段。

一次规划比较一次到店、单餐的多个选择；路程、排队和用餐时长按填写的数值计算。

| 想了解什么 | 从这里开始 |
| --- | --- |
| Agent 工作流程 | [SKILL.md](SKILL.md) |
| 输入字段与示例 | [references/input-schema.md](references/input-schema.md) |
| MCP 协议、工具与配置 | [MCP_INTEGRATION.md](MCP_INTEGRATION.md) |
| 测试与实际联调结果 | [VALIDATION.md](VALIDATION.md) |
| 报名记录与演示脚本 | [SUBMISSION.md](SUBMISSION.md) |

<details>
<summary>代码结构与检查命令</summary>

```text
app.py                 本机 HTTP 服务
mcwindow/engine.py     时间与预算计算、日历与报告导出
mcwindow/mcp_client.py 官方 MCP 客户端
mcwindow/demo.py       演示数据
web/                  HTML / CSS / JavaScript 页面
scripts/plan.py        CLI 与 Skill 入口
tests/                规划、MCP 协议与 HTTP 测试
```

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
node --check web/app.js
```

2026-10-23 验证：33 项自动测试通过；完成真实 MCP 工具发现和 `query-my-coupons` 查询，其余工具完成发现。详情见 [验证记录](VALIDATION.md)。

</details>

## 一起把饭点安排得更好

遇到不好用的地方，或有想加入的场景，欢迎[提一个 Issue](https://github.com/WuHanCi/mcwindow/issues)。说说你原本想怎么用、在哪一步卡住，会很有帮助。也欢迎通过 Pull Request 改进交互、文档和规划逻辑。

## 项目与许可

麦当劳 MCP 创意参赛作品，开发工具为 Codex。[参赛申请 #1117](https://github.com/M-China/mcd-developer-innovation-challenge/issues/1117) 已获[官方确认](https://github.com/M-China/mcd-developer-innovation-challenge/issues/1117#issuecomment-6361308736)。[活动规则](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/activityGuidelines.md) · [参赛声明](CONTEST_DECLARATION.md)

由 [Wuhanci](https://github.com/WuHanCi) 开发，代码与页面采用 [MIT License](LICENSE)。
