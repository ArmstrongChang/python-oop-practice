# 讀檔 > 偵測 > 輸出
# 提供 CLI: python -m src.report sample/multi_sensor_log.jsonl
from __future__ import annotations
import argparse
import csv
import os
from collections import Counter, defaultdict
from typing import Dict, List                   # 型別註解
from .parser import parse_jsonl                  # 讀檔 -> rows
from .rules import detect_events, summarize     # 事件偵測與彙整
import sys                                      # 讀命令列參數

def default_upper() -> Dict[str, float]:
    # 預設上限 (可依場景調整/改成讀設定檔)
        return {
        "temperature": 41.0,
        "humidity": 65.0,
        "pressure": 101.5,
        "general": 95.0,
    }
def default_lower() -> Dict[str, float]:
    # 預設下限
    return {
        "temperature": 36.0,
        "humidity": 40.0,
        "pressure": 99.0,
        "general": 0.0,
    }
""" 增加 CLI 參數 定義 
可傳入 --max-gap 或 --t-high 或 --p-high
"""
def parse_args() -> argparse.Namespace:
    # ap = argparse.ArgumentParser()

    ap = argparse.ArgumentParser(
        description="Parse JSONL sensor logs and export event summary to CSV."
    )
    ap.add_argument(
        "-i", "--input", required=True,
        help="Path to input JSONL file (e.g., sample/multi_sensor_log.jsonl)"
    )
    ap.add_argument(
        "-o", "--output", required=True,
        help="Path to output CSV file (default: result/report.csv)"
    )
    # ap.add_argument("path", help="path to .jsonl")
    ap.add_argument("--max-gap", type=float, default=1.2)
    ap.add_argument("--t-high", type=float, default=41.0)
    ap.add_argument("--h-high", type=float, default=65.0)
    ap.add_argument("--p-high", type=float, default=101.5)
    return ap.parse_args()

def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

def to_row_dict(e) -> Dict[str, str]:
    """
    將 rules.detect_events(...) 回傳的事件物件/資料，轉成 CSV 列
    為了兼容不同事件欄位，用getattr 取值並給預設空字串
    """
    r = e.row
    return {
        "event_kind":   getattr(e, "kind", ""),
        "sensor":       getattr(e, "sensor", ""),
        "message":      getattr(e, "msg", ""),
        "timestamp":    getattr(r, "timestamp", ""),
        "value":        getattr(r, "value", ""),
        "thread_id":    getattr(r, "thread_id", ""),
        "global_seq":   getattr(r, "global_seq", ""),
        "local_seq":    getattr(r, "local_seq", ""),
    }

""" 
    summarizeCSV 此寫法等同於 
    rules.py 的 summarize(events: List[Event]) -> Dict[str, Dict[str, int]] 
"""
def summarizeCSV(events: List) -> Dict[str, Dict[str, int]]:
    by_kind = Counter()
    by_sensor = Counter()
    for e in events:
        by_kind[getattr(e, "kind", "UNKNOWN")] += 1
        by_sensor[getattr(e, "sensor", "UNKNOWN")] += 1

    # 轉成一般 dict 方便列印/ 序列化
    return {
        "by_kind": dict(by_kind),
        "by_sensor": dict(by_sensor),
    }
def write_csv(events: List, out_path: str) -> None:
    ensure_parent_dir(out_path)
    fieldnames = [
        "event_kind", "sensor", "message", "timestamp",
        "value", "thread_id", "global_seq", "local_seq"
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for e in events:
            w.writerow(to_row_dict(e))

# 顏色常數
GRAY    = "\033[90m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
RESET   = "\033[0m"
def print_preview(events: List, limit: int = 10) -> None:
    print("\n=== PREVIEW FIRST {} EVENTS ===".format((min(limit, len(events)))))
    for e in events[:limit]:
        kind = getattr(e, "kind", "")
        sensor = getattr(e, "sensor", "")
        message = getattr(e, "msg", "")
        value = getattr(e.row, "value", "")

        # 顏色邏輯
        color = GREEN
        if ">" in message:
            color  = RED
        elif "Δ" in message:
            color = YELLOW
        print(color + f"   {kind:<10} {sensor:<14} message {message:<25} value {value:<10}" + RESET)   #?

def main() -> None:
    args = parse_args()
    rows = parse_jsonl(args.input)               # 讀 JSONL 路徑，並解析 -> List[SensorRow]

    print(f"[INFO] loaded rows: {len(rows)}")

    events = detect_events(
        rows,
        upper={"temperature": args.t_high,"humidity": args.h_high,"pressure": args.p_high},
        lower=default_lower(),
        max_gap_seconds=0.5
    )
    print(f"[INFO] detected event: {len(rows)}")    # ?

    summary = summarizeCSV(events)                 # 彙整
    print("\n=== SUMMARY ===")
    print("By kind: ", summary["by_kind"])

    # 依事件數排序 sensor，列出前5名
    by_sensor = summary["by_sensor"]
    top5 = sorted(by_sensor.items(), key=lambda kv: kv[1], reverse=True)[:5]
    # print("By sensor (top 5): ", dict(top5))
    print("By sensor: ", summary["by_sensor"])

    print_preview(events, limit=10)

    write_csv(events, args.output)

    # print("\n=== FIRST 10 EVENTS ===")
    # for e in events[:10]:
    #     print(f"{e.kind:>12}  {e.sensor:<15}  {e.msg}")

if __name__ == "__main__":
    main()

