# 麦麦空档 McWindow

**给饭点，留个刚好的空。**

面向课间、会议间隙等时间受限的用餐场景：把预算、往返时间、用餐时间和优惠可用时段放进同一个规划器，回答“现在出发来不来得及，哪一个候选更适合”。

公开仓库：[WuHanCi/mcwindow](https://github.com/WuHanCi/mcwindow)。参赛申请：[官方活动 Issue #1117](https://github.com/M-China/mcd-developer-innovation-challenge/issues/1117)，[官方已确认报名成功](https://github.com/M-China/mcd-developer-innovation-challenge/issues/1117#issuecomment-6361308736)。

## 能做什么

- 输入预算、下一项安排开始时间、单程路程、排队、用餐、缓冲时间。
- 检查优惠有效期及每日可用时段，支持跨午夜时段。
- 按最低价格或最早返回排序，展示完整出发/到店/点单/用餐结束/返回时间线。
- 对超预算、已过期、时段不匹配、价格未知、尚未核对条件的候选逐项解释。
- 一键导出 `.ics` 日历和 Markdown 安排。
- 连接麦当劳官方 MCP，获取实时工具定义、查询原文，再由用户核对并建立候选。
- 提供可被 Agent 使用的 `SKILL.md` 及确定性 CLI 规划器。

## 在 Mac 上启动

要求 Python **3.9 或更新版本**；没有第三方运行依赖。

1. 在 Finder 中进入项目文件夹，双击 `start.command`；或在该文件夹运行 `python3 app.py`。
2. 浏览器打开 <http://127.0.0.1:8765>。
3. 默认演示：2026年10月23日11:50出发，70分钟空档、25元预算，5个示例候选中2个可行。

服务仅绑定 `127.0.0.1`。端口占用时运行 `python3 app.py --port 8766`，再打开相应地址。按 Control+C 停止。

## 真实 MCP 使用

1. 访问 [麦当劳官方开放平台](https://open.mcd.cn/mcp)，手机号登录 → 控制台 → 激活 Token。
2. 在本机页面的「MCP 连接」中输入 Token，点击「连接并获取工具」。
3. 选择 `query-my-coupons`、`available-coupons` 或 `campaign-calendar`，查看实时 `inputSchema`，填写参数后查询。
4. 阅读官方返回原文，点击「依据查询结果建立候选」，录入原文明确的名称、实际应付价格、有效期和时段；核对门店、就餐方式和领取状态。条件不明确时不勾选「已核对」。
5. 保存后回到「空档规划」计算，按需要导出日历。

三类查询分别对应可领取券、账户已有券和营销活动。选中优惠后，将名称、金额和可用时段整理为候选，Agent Skill 也可以协助完成。

Agent 客户端配置见 `mcp-config.example.json`，`${MCD_MCP_TOKEN}` 对应本机 Token。按客户端支持的方式填写环境变量或本地配置。

## Skill / CLI 使用

把整个项目作为技能目录保留，支持 Agent Skills 的客户端读取根目录 `SKILL.md`。文件内含工作流程和输入规范。

```bash
python3 scripts/plan.py --demo
python3 scripts/plan.py --input private/request.json --output private/plan.json --ics private/meal.ics --report private/plan.md
```

输入规范见 [references/input-schema.md](references/input-schema.md)。`private/` 用于保存本机输入和规划结果，已加入 Git 忽略列表。

## 规划依据

先计算到店时间，再寻找“优惠有效期 ∩ 每日可用时段”内最早可点单时刻。点单从到店加排队时间起算，用餐、返回及缓冲在下次安排前完成。价格用整数分比较，未通过的候选按原因展示。

适用于一次到店、单餐候选的比较。价格、门店与就餐方式在候选页确认，路程、排队和用餐时长可自行调整。

## 验证与当前状态

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
node --check web/app.js
```

**33项自动测试通过。2026-10-23 完成真实 MCP 工具发现和 `query-my-coupons` 查询**，跑通查询、候选建立和规划流程。详细记录见 [VALIDATION.md](VALIDATION.md)。

## 参赛材料

- `CONTEST_DECLARATION.md`：从官方仓库原样保留。
- `MCP_INTEGRATION.md`：工具、协议、调用流程和联调记录。
- `mcp-config.example.json`：只含环境变量占位符。
- `SUBMISSION.md`：报名记录及提交正文。
- 开发工具：Codex。本次按普通参赛项目提交。

活动说明：[官方规则](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/activityGuidelines.md)。

## 目录

```text
app.py                 本机 HTTP 服务
mcwindow/engine.py     时间交集与预算规划、导出
mcwindow/mcp_client.py Streamable HTTP 客户端
mcwindow/demo.py       内置演示数据
web/                  无第三方框架的交互页面
scripts/plan.py        Skill / CLI 入口
tests/                业务边界与协议测试
```

代码与页面采用 [MIT License](LICENSE)。
