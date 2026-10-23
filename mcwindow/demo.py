"""Sample data for a reproducible demonstration."""


def demo():
    def offer(oid, name, price, end="2026-10-23T23:59:00+08:00", windows=None):
        return {"id": oid, "name": name, "price_fen": price,
                "valid_from": "2026-10-23T00:00:00+08:00", "valid_to": end,
                "daily_windows": windows or [], "verified": True,
                "evidence": "McWindow 演示数据",
                "note": "演示候选"}
    return {"source": "demo", "now": "2026-10-23T11:50:00+08:00",
            "free_until": "2026-10-23T13:00:00+08:00", "budget_fen": 2500,
            "travel_minutes": 8, "queue_minutes": 6, "meal_minutes": 20,
            "buffer_minutes": 10, "strategy": "budget", "offers": [
                offer("lunch-a", "午间轻松组合 A", 1990, windows=[["11:00", "14:00"]]),
                offer("lunch-b", "午间分享组合 B", 2490),
                offer("afternoon", "午后小食组合", 1590, windows=[["14:00", "17:00"]]),
                offer("breakfast", "早间元气组合", 1290, "2026-10-23T10:30:00+08:00"),
                offer("over-budget", "丰盛搭配组合", 3290)
            ]}
