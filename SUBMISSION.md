# 发布与参赛

## 报名前完成

1. 已完成真实基础联调：工具发现、卡包查询、候选建立和未核对时拦截。具体门店及订单条件仍由使用者在实际用餐前核对。
2. 阅读项目及官方 `CONTEST_DECLARATION.md`，确认自己可以接受并作出声明。
3. 发布到本人 GitHub 公开仓库，建议仓库名 `mcwindow`。不得上传真实 Token、原始账户返回、手机号或地址。
4. 检查公开仓库根目录有 `README.md`、`CONTEST_DECLARATION.md`、`MCP_INTEGRATION.md`、`mcp-config.example.json`、`SKILL.md` 和代码。
5. 按官方模板提交 Issue，等待活动机器人明确回复报名成功。

截至2026-10-23核对，报名截止：**2026-10-25 23:59，北京时间**。仓库本身不是报名成功的证据。排名按公开 Star 数据，作品完成不等于进入获奖范围。

## Issue 草稿

下列为待发布仓库地址，目前尚未公开创建。字段名和字段内容保持在同一行，地址不用 Markdown 链接格式。

标题：

```text
【参赛申请】麦麦空档 McWindow：把优惠安排进课间与会议空档
```

正文：

```text
【参赛申请】
项目名称：麦麦空档 McWindow
项目地址：https://github.com/WuHanCi/mcwindow
项目简介：面向课间和会议间隙的麦当劳用餐时间规划 Skill。通过官方 MCP 查询优惠券及活动原文，经用户核对后，结合预算、往返路程、排队、用餐及缓冲时间，筛选可行候选并解释未采用原因，支持时间线展示和 ICS 日历导出。含本机交互页面、确定性 CLI 和可调用的 SKILL.md。
```

官方入口：[活动仓库](https://github.com/M-China/mcd-developer-innovation-challenge) · [活动规则](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/activityGuidelines.md)。

## 60秒演示脚本

1. 说明“下面是明确标注的虚构优惠，演示时间为11:50”。
2. 展示25元预算、13:00上课、单程8分钟、排队6分钟、用餐20分钟、缓冲10分钟。
3. 点击「安排一下」，展示19.90元候选和12:32返回的时间线。
4. 展开未采用原因：午后券时段不匹配、早餐券已过期、丰盛搭配超预算。
5. 把下次安排改为12:20，展示没有可行安排；不为了用券硬凑结果。
6. 改回13:00，导出日历。
7. 真实联调完成后，另展示一份脱敏查询记录和核对流程，不把演示资料说成真实报价。

## WorkBuddy 专项奖励

目前代码由 Codex 辅助编写，没有 WorkBuddy 开发记录。未提供 `workbuddy.md`，不声明已满足该专项条件。若之后实际使用 WorkBuddy 完成调试或开发，按活动要求导出真实对话并整理脱敏记录。
