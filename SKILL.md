---
name: mcwindow
description: 根据用户的空档、预算和麦当劳官方 MCP 优惠信息安排可行的用餐计划，并导出日历。用于课间、会议间隙等时间受限的用餐决策。
---

# 麦麦空档 McWindow

先判断时间和预算是否允许，再推荐候选。没有可行安排时明确说出原因。用 `scripts/plan.py` 计算时间。

## 获取资料

1. 收集当前时间、下次安排开始时间、预算、单程路程、排队预留、用餐时间、回程缓冲；日期按北京时间。只问缺失且会影响结果的参数。
2. 通过已配置的麦当劳 MCP 连接，发现实时工具及其 `inputSchema`。可用工具为 `campaign-calendar`、`available-coupons`、`query-my-coupons`、`now-time-info`；按实时定义填写参数。
3. 用用户需要的查询工具取得原文。`available-coupons` 查询可领取券，`query-my-coupons` 查询账户已有券，`campaign-calendar` 查询活动。
4. 把选中的候选整理成 [references/input-schema.md](references/input-schema.md) 的结构。价格统一为整数分；仅在原文明确金额单位时转换。门店限制、就餐方式、日期、是否需领券等条件要让用户核对。缺失价格填 `null`，待确认的候选填 `verified: false`。
5. 每个 MCP 候选的 `evidence` 填写工具名与相关优惠摘录，`source` 为 `mcp`。演示使用 `--demo`，来源标为 `demo`。

有星期限制时，按券面中文说明将候选有效期裁剪到本次空档中被允许的具体日期。跨日可拆成独立候选；星期按券面说明映射为具体日期，每日时段单独填写。返回的App专用提示、门店未校验等限制写入备注，未确认时保持 `verified: false`。

## 计算与交付

输入和结果保存在用户工作目录的 `private/` 中。相对路径按本 Skill 所在目录解析：

```bash
python3 scripts/plan.py --input /absolute/private/request.json --output /absolute/private/plan.json --report /absolute/private/plan.md
```

仅在有可行推荐时增加 `--ics /absolute/private/mcwindow.ics`。无需联网的演示：

```bash
python3 scripts/plan.py --demo
```

解释推荐的预计支出、出发/到店/点单/返回时间、缓冲及未采用原因。用户可选择最低价格或最早返回，时长按用户填写的参数计算。

也可从项目根目录运行 `python3 app.py`，使用本机页面完成相同流程。此 Skill 与项目代码须整目录保留。
