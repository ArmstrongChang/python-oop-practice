# 讀檔 > 偵測 > 輸出
# 提供 CLI: python -m src.report sample/multi_sensor_log.jsonl
import argparse
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
def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="path to .jsonl")
    ap.add_argument("--max-gap", type=float, default=1.2)
    ap.add_argument("--t-high", type=float, default=41.0)
    ap.add_argument("--h-high", type=float, default=65.0)
    ap.add_argument("--p-high", type=float, default=101.5)
    return ap.parse_args()

def main():
    args = parse_args()
    rows = parse_jsonl(args.path)               # 讀 JSONL 路徑，並解析 -> List[SensorRow]

    print(f"[INFO] loaded rows: {len(rows)}")

    events = detect_events(
        rows,
        upper={"temperature": args.t_high,"humidity": args.h_high,"pressure": args.p_high},
        lower=default_lower(),
        max_gap_seconds=0.5
    )

    summary = summarize(events)                 # 彙整
    print("\n=== SUMMARY ===")
    print("By kind: ", summary["by_kind"])

    # 依事件數排序 sensor，列出前5名
    by_sensor = summary["by_sensor"]
    top5 = sorted(by_sensor.items(), key=lambda kv: kv[1], reverse=True)[:5]
    # print("By sensor (top 5): ", dict(top5))
    print("By sensor: ", summary["by_sensor"])

    print("\n=== FIRST 10 EVENTS ===")
    for e in events[:10]:
        print(f"{e.kind:>12}  {e.sensor:<15}  {e.msg}")

if __name__ == "__main__":
    main()

