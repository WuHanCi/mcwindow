# 发布与参赛

## 发布与报名记录

- 公开仓库：https://github.com/WuHanCi/mcwindow
- 报名 Issue：https://github.com/M-China/mcd-developer-innovation-challenge/issues/1117
- 提交账号：WuHanCi。
- 提交时间：2026-10-23 15:58:59（北京时间）。
- 官方确认：报名成功。M-China-Official 于2026-10-23 16:59:22（北京时间）回复“您的作品已成功参赛”。
- 回执：https://github.com/M-China/mcd-developer-innovation-challenge/issues/1117#issuecomment-6361308736

## 报名准备

1. 已完成真实基础联调：工具发现、卡包查询、候选建立和未核对时拦截。具体门店及订单条件仍由使用者在实际用餐前核对。
2. 阅读项目及官方 `CONTEST_DECLARATION.md`，确认自己可以接受并作出声明。
3. 发布到本人 GitHub 公开仓库，建议仓库名 `mcwindow`。
4. 检查公开仓库根目录有 `README.md`、`CONTEST_DECLARATION.md`、`MCP_INTEGRATION.md`、`mcp-config.example.json`、`SKILL.md` 和代码。
5. 按官方模板提交 Issue，等待活动机器人明确回复报名成功。

截至2026-10-23核对，报名截止：**2026-10-25 23:59，北京时间**。排名按公开 Star 数据统计。

## 已提交的 Issue 内容

仓库已公开发布，以下内容已按官方格式提交。字段名和字段内容保持在同一行，地址不用 Markdown 链接格式。

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

1. 选择演示模式，出发时间设为11:50。
2. 展示25元预算、13:00上课、单程8分钟、排队6分钟、用餐20分钟、缓冲10分钟。
3. 点击「安排一下」，展示19.90元候选和12:32返回的时间线。
4. 展开未采用原因：午后券时段不匹配、早餐券已过期、丰盛搭配超预算。
5. 把下次安排改为12:20，展示没有可行安排；不为了用券硬凑结果。
6. 改回13:00，导出日历。
7. 展示真实 MCP 查询、候选建立和规划流程。

## WorkBuddy 专项奖励

开发工具为 Codex，本次按普通参赛项目提交。
