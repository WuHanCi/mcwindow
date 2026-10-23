# 验证记录

日期：2026-10-23。环境：macOS、Python 3.9.6、Node.js 24.18.0。

## 自动检查

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
node --check web/app.js
```

**33项测试通过**：19项规划器测试、9项MCP协议测试、5项HTTP接口测试。

覆盖预算与时间边界、跨午夜、多时段、时区、候选状态、排序、日历转义与折行、JSON/SSE、会话协商、分页、HTTP错误及业务失败、页面与导出接口。

Skill Creator 格式校验通过。官方参赛声明的 Git blob SHA-1 为 `136e76f3160317049f19f5ba03f4d0fedd70fc3c`，与官方原文一致。

## 浏览器交互

- 25元预算、70分钟空档，5个演示候选中2个可行；19.90元方案12:32返回，12:42完成缓冲。
- 切换24.90元方案，页面更新选中状态与预算余量。
- 日历导出显示成功，导出内容另通过HTTP与CLI测试。
- 空档缩短至30分钟，结果为0个可行候选。
- 无效时间显示参数提示，并清除旧推荐。
- 切换数据模式、新增和编辑候选、候选确认状态均正常。
- 319px与390px宽度下完成窄屏检查。

## 真实 MCP 联调

1. 使用用户在本机页面输入的 Token 连接服务，发现4个查询工具。
2. 读取实时参数定义，以 `{"page":"1","pageSize":"20"}` 调用 `query-my-coupons`。
3. 返回 `isError: false`、业务层 `success: true`、`code: 200`，获得优惠券列表。
4. 从相关信息建立一个MCP候选，包含价格、有效期、每日时段、星期和App渠道信息。
5. 页面切换为“MCP 候选”；90分钟空档下，适用条件待确认的候选进入待确认列表。

本次实测工具为 `query-my-coupons`，其余3个工具完成发现。推荐时间线和导出使用演示数据验证；门店与订单条件由使用者在候选页确认。

## 发布与报名

- 公开仓库：https://github.com/WuHanCi/mcwindow，默认分支 main。
- 必需文件已从远端 Git tree 核对。
- 报名 Issue：https://github.com/M-China/mcd-developer-innovation-challenge/issues/1117。
- 提交账号：WuHanCi。
- 提交时间：2026-10-23 15:58:59（北京时间）。
- 回执：M-China-Official 于2026-10-23 16:59:22（北京时间）回复“您的作品已成功参赛”。
- 回执链接：https://github.com/M-China/mcd-developer-innovation-challenge/issues/1117#issuecomment-6361308736
