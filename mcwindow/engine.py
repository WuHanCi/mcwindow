"""Intersect travel, meal, class and coupon windows. All money is integer fen."""
from datetime import datetime, timedelta, timezone
import hashlib
import math

CHINA = timezone(timedelta(hours=8))


class ValidationError(ValueError):
    pass


def timestamp(value, field):
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return result.replace(tzinfo=CHINA) if result.tzinfo is None else result.astimezone(CHINA)
    except (ValueError, TypeError):
        raise ValidationError(field + "必须是 ISO 日期时间")


def integer(value, field, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValidationError("%s必须是 %d 到 %d 的整数" % (field, low, high))
    return value


def hhmm(value):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except (ValueError, TypeError):
        raise ValidationError("每日可用时段须使用 HH:MM")


def iso(value):
    return value.isoformat(timespec="minutes")


def offer_windows(offer, now, deadline):
    start = timestamp(offer.get("valid_from", iso(now)), "优惠开始时间")
    end = timestamp(offer.get("valid_to", iso(deadline)), "优惠结束时间")
    if end <= start:
        raise ValidationError("优惠结束时间须晚于开始时间")
    daily = offer.get("daily_windows", [])
    if not isinstance(daily, list) or len(daily) > 12:
        raise ValidationError("每日可用时段须为最多12段的列表")
    if not daily:
        return [(start, end)]
    result = []
    for offset in range(-1, 3):
        date = (now + timedelta(days=offset)).date()
        for window in daily:
            if not isinstance(window, list) or len(window) != 2:
                raise ValidationError("每日可用时段格式为 [[\"11:00\", \"14:00\"]]")
            a, b = hhmm(window[0]), hhmm(window[1])
            left = datetime.combine(date, a, CHINA)
            right = datetime.combine(date, b, CHINA)
            if right <= left:
                right += timedelta(days=1)
            if max(start, left) < min(end, right):
                result.append((max(start, left), min(end, right)))
    return sorted(result)


def plan(request):
    if not isinstance(request, dict):
        raise ValidationError("请求须为 JSON 对象")
    now = timestamp(request.get("now"), "当前时间")
    deadline = timestamp(request.get("free_until"), "下次安排时间")
    available = (deadline - now).total_seconds() / 60
    if not 0 < available <= 1440:
        raise ValidationError("下次安排须晚于当前时间，且相隔不超过24小时")
    budget = integer(request.get("budget_fen"), "预算（分）", 0, 100000)
    travel = integer(request.get("travel_minutes"), "单程时间", 0, 120)
    queue = integer(request.get("queue_minutes"), "排队预留", 0, 120)
    meal = integer(request.get("meal_minutes"), "用餐时间", 1, 120)
    buffer = integer(request.get("buffer_minutes"), "回程缓冲", 0, 120)
    source = request.get("source", "manual")
    if source not in ("demo", "manual", "mcp"):
        raise ValidationError("数据来源须为 demo、manual 或 mcp")
    offers = request.get("offers", [])
    if not isinstance(offers, list) or len(offers) > 100:
        raise ValidationError("候选须为最多100项的列表")
    feasible, excluded, ids = [], [], set()
    arrival = now + timedelta(minutes=travel)
    latest_return = deadline - timedelta(minutes=buffer)
    for index, offer in enumerate(offers):
        if not isinstance(offer, dict):
            raise ValidationError("每个候选须为 JSON 对象")
        name = str(offer.get("name", "")).strip()
        if not name or len(name) > 120:
            raise ValidationError("候选名称须为1到120个字符")
        oid = str(offer.get("id", "offer-%d" % index))[:120]
        if oid in ids:
            raise ValidationError("候选 id 不能重复")
        ids.add(oid)
        reasons = []
        price = offer.get("price_fen")
        if price is None:
            reasons.append("尚未确认价格")
        else:
            integer(price, "候选价格（分）", 0, 100000)
            if price > budget:
                reasons.append("超出预算 ¥%.2f" % ((price - budget) / 100))
        if source != "demo" and offer.get("verified") is not True:
            reasons.append("价格、门店及使用条件尚未核对")
        if source == "mcp" and not str(offer.get("evidence", "")).strip():
            reasons.append("缺少 MCP 原文依据")
        windows = offer_windows(offer, now, deadline)
        valid_to = timestamp(offer.get("valid_to", iso(deadline)), "优惠结束时间")
        if valid_to <= now:
            reasons.append("优惠已过期")
        schedule = None
        for left, right in windows:
            # Validity applies at ordering after the queue, not at meal completion.
            order = max(arrival + timedelta(minutes=queue), left)
            finish = order + timedelta(minutes=meal)
            returned = finish + timedelta(minutes=travel)
            if order < right and returned <= latest_return:
                schedule = (order, finish, returned)
                break
        if schedule is None and valid_to > now:
            reasons.append("可用时段与空档不匹配，或往返用餐时间不足")
        base = {"id": oid, "name": name, "price_fen": price,
                "valid_to": iso(valid_to), "note": str(offer.get("note", ""))[:500],
                "evidence": str(offer.get("evidence", ""))[:2000], "source": source}
        if reasons:
            excluded.append(dict(base, reasons=reasons))
            continue
        order, finish, returned = schedule
        spare = math.floor((deadline - returned).total_seconds() / 60)
        feasible.append(dict(base, depart_at=iso(now), arrive_at=iso(arrival),
                             order_at=iso(order), finish_at=iso(finish), return_at=iso(returned),
                             buffer_until=iso(returned + timedelta(minutes=buffer)),
                             spare_minutes=spare, unspent_fen=budget - price,
                             wait_minutes=math.ceil((order - arrival).total_seconds() / 60)))
    strategy = request.get("strategy", "budget")
    if strategy not in ("budget", "time"):
        raise ValidationError("排序方式须为 budget 或 time")
    if strategy == "time":
        feasible.sort(key=lambda x: (x["return_at"], x["price_fen"], x["name"]))
    else:
        feasible.sort(key=lambda x: (x["price_fen"], x["return_at"], x["name"]))
    return {"source": source, "now": iso(now), "free_until": iso(deadline),
            "budget_fen": budget, "strategy": strategy,
            "available_minutes": math.floor(available), "buffer_minutes": buffer,
            "required_minutes": travel * 2 + queue + meal + buffer,
            "feasible": feasible, "excluded": excluded,
            "recommendation": feasible[0] if feasible else None,
            "message": "有 %d 个候选能落进你的空档" % len(feasible) if feasible else
                       "这次先不安排：没有同时满足预算、时间和使用条件的候选。"}


def escape_ics(value):
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


def fold_line(value):
    lines, line, size = [], "", 0
    for char in value:
        length = len(char.encode("utf-8"))
        if size + length > 75:
            lines.append(line)
            line, size = " ", 1
        line += char
        size += length
    return "\r\n".join(lines + [line])


def calendar(result, offer_id=None):
    offer = next((x for x in result["feasible"] if x["id"] == offer_id), None) if offer_id else result["recommendation"]
    if offer is None:
        raise ValidationError("没有可导出的可行安排")
    utc = lambda v: timestamp(v, "日历时间").astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    identity = "%s|%s|%s" % (offer["id"], offer["depart_at"], offer["return_at"])
    uid = hashlib.sha256(identity.encode()).hexdigest()[:24] + "@mcwindow.local"
    description = "预计支出 ¥%.2f；按设定的路程、排队和用餐时间安排。" % (offer["price_fen"] / 100)
    if result["source"] == "demo":
        description = "演示安排。" + description
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//McWindow//Meal Window//ZH", "CALSCALE:GREGORIAN",
             "BEGIN:VEVENT", "UID:" + uid, "DTSTAMP:" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
             "DTSTART:" + utc(offer["depart_at"]), "DTEND:" + utc(offer["buffer_until"]),
             "SUMMARY:" + escape_ics(("[演示] " if result["source"] == "demo" else "") + "麦麦空档 · " + offer["name"]),
             "DESCRIPTION:" + escape_ics(description), "STATUS:TENTATIVE", "END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(fold_line(line) for line in lines) + "\r\n"


def report(result):
    rows = ["# 麦麦空档规划", "", "来源：" + {"demo": "演示数据", "mcp": "MCP 查询资料", "manual": "手动录入"}[result["source"]],
            "当前：%s；下次安排：%s；预算：¥%.2f" % (result["now"], result["free_until"], result["budget_fen"] / 100), "", result["message"], ""]
    for item in result["feasible"]:
        rows.extend(["## " + item["name"], "", "预计 ¥%.2f；%s 出发，%s 点单，%s 返回，另留 %d 分钟缓冲。" %
                     (item["price_fen"] / 100, item["depart_at"], item["order_at"], item["return_at"], result["buffer_minutes"]), ""])
    if result["excluded"]:
        rows.extend(["## 未采用的候选", ""])
        for item in result["excluded"]:
            rows.append("- %s：%s" % (item["name"], "；".join(item["reasons"])))
    return "\n".join(rows) + "\n"
