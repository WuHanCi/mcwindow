#!/usr/bin/env python3
"""Deterministic planning entrypoint for the McWindow Skill."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcwindow.demo import demo
from mcwindow.engine import plan, calendar, report, ValidationError


def main():
    parser = argparse.ArgumentParser(description="麦麦空档确定性规划器")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="输入 JSON 文件")
    source.add_argument("--demo", action="store_true", help="使用明确标注的虚构资料")
    parser.add_argument("--output", type=Path, help="输出 JSON；未指定则打印")
    parser.add_argument("--ics", type=Path, help="导出推荐安排为日历")
    parser.add_argument("--report", type=Path, help="导出 Markdown 安排")
    args = parser.parse_args()
    try:
        data = demo() if args.demo else json.loads(args.input.read_text(encoding="utf-8"))
        result = plan(data)
        # Build exports before writing so invalid calendar requests leave no partial outputs.
        ics = calendar(result) if args.ics else None
        markdown = report(result) if args.report else None
        text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        if args.ics:
            args.ics.write_bytes(ics.encode("utf-8"))
        if args.report:
            args.report.write_text(markdown, encoding="utf-8")
    except (ValidationError, ValueError, OSError) as exc:
        parser.exit(2, "规划失败：%s\n" % exc)


if __name__ == "__main__":
    main()
