# MCP 集成说明

## 连接配置

- 服务地址：`https://mcp.mcd.cn`
- 协议：Streamable HTTP、JSON-RPC 2.0。
- 认证：`Authorization: Bearer ${MCD_MCP_TOKEN}`，在本机页面输入。
- 工具参数：连接后通过 `tools/list` 获取实时 `inputSchema`。
- 参考：[麦当劳 MCP 官方指南](https://github.com/M-China/mcd-mcp-server/blob/main/README.md)。

## 使用的工具

| Tool | 用途 |
| --- | --- |
| `query-my-coupons` | 查询账户已有优惠券 |
| `available-coupons` | 查询可领取优惠券 |
| `campaign-calendar` | 查询营销活动及日期 |
| `now-time-info` | 查询服务器时间 |

## 调用流程

```text
输入 Token → initialize → notifications/initialized
→ tools/list → 展示参数定义 → 填写参数 → tools/call
→ 查看结果 → 建立候选 → 确认价格和适用条件
→ 预算与时间交集计算 → 时间线、日历、Markdown 安排
```

客户端处理会话 ID、协议版本协商和工具列表分页，接受 JSON 与 SSE 响应，按请求 ID 匹配结果。响应上限2MB，读取超时18秒；支持401、403、429、协议错误和业务失败提示。

服务运行于 `127.0.0.1`，Token 和查询结果随当前页面会话保留。

## 业务价值

MCP 提供优惠内容、价格和时段，规划器结合用户的预算、路程、排队与用餐时间，选出能落进空档的候选，并展示完整时间线。

## 实际联调

2026-10-23，通过本机页面完成官方工具发现与 `query-my-coupons` 查询。调用参数为：

```json
{"page":"1","pageSize":"20"}
```

这两个参数在实时定义中均为字符串。服务器返回 `isError: false`、`structuredContent.success: true`、`code: 200`，优惠数据位于 `structuredContent.data.coupons`。

金额位于 `discountInfo`，有效期位于 `tradeStartDateTime` / `tradeEndDateTime`，另有每日时段、星期和渠道信息。选取相关内容建立候选后，页面正常切换为“MCP 候选”。适用条件待确认时，候选进入待确认列表。

本次执行了账户券查询，其余3个工具完成工具发现。具体门店及就餐方式在候选信息中确认。测试详情见 [VALIDATION.md](VALIDATION.md)。
