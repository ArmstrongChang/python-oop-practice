
from collections import defaultdict                 # 方便做依 sensor 分組from dataclasses import dataclass
from typing import List, Dict, Tuple                # 型別註解
from datetime import datetime
from dataclasses import dataclass

from .parser import SensorRow                        # 使用前面定義的結構

@dataclass(frozen=True)
class Event:
    kind: str             # 事件類型: THRESHOLD / GAP / DUP_TS / OUT_OF_ORDER
    sensor: str           # 感測器名稱
    msg: str              # 簡要描述
    row: SensorRow        # 觸發事件時的原始資料

def _pick_limit(limits: Dict[str, float], sensor: str) -> float:
    """
    從 limits 取適用的上/下限
    規則: temperature */ humidity */ pressure* 走對應 key; 其他走 general
    """
    if sensor.startswith("temperature"): return limits.get("temperature")
    if sensor.startswith("humidity"): return limits.get("humidity")
    if sensor.startswith("pressure"): return limits.get("pressure")
    return limits.get("general")

def detect_events(rows: List[SensorRow],
                  upper: Dict[str, float] = None,
                  lower: Dict[str, float] = None,
                  max_gap_seconds: float = 1.2
                  ) -> List[Event]:
    """
    輸入整理好的 rows 與各類上/ 下限，輸出事件清單
    檢查項:
        1) THRESHOLD: 閥值，超出上下限
        2) DUP_TS: 同 sensor 同 timestamp 重複
        3) GAP: 停頓，同一 sensor 相鄰兩筆時間間隔過大
        4) OUT_OF_ORDER: local_seq 逆序/亂序 同一 sensor的 local_seq 非遞增
    """
    upper = upper or {}
    lower = lower or {}
    events: List[Event] = []                                       # 最終事件列表

    by_sensor: Dict[str, List[SensorRow]] = defaultdict(list)       # 相當於 Map<String, List<SensorRow>> bySensor = new HashMap<String, List<SensorRow>>();

    for r in rows:                                                  # 依 sensor 分組
        by_sensor[r.sensor].append(r)

    for sensor, items in by_sensor.items(): #? sensor 和 items 為什麼可以一起寫，是指什麼
        # 以 (時間, local_seq) 排序，確保檢查 gap 與序列時有一致性
        # lst_sorted = sorted(lst, key=lambda r: (r.ts, r.local_seq)) #? lst 是什麼, lambda是什麼演算法
        items.sort(key=lambda r: (r.ts, r.local_seq))

        up = _pick_limit(upper, sensor)         # 取上限 為什麼只丟upper，upper什麼值都沒有 就可以抓到up
        lo = _pick_limit(lower, sensor)         # 取下限

        # 閥值 & 重複時間戳 & 停頓
        # --- 1) Threshold / 2) DUP_TS / 3) GAP ---
        seen_ts = set()                         # 紀錄已見過的 timestamp
        prev: SensorRow = None

        for r in items:
            # 1) 閥值
            if up is not None and r.value > up:     # 超過 up
                events.append(Event("THRESHOLD", sensor, f"value {r.value:.2f} > {up:.2f}", r)) # Event 寫法?
            if lo is not None and r.value < lo:     # 少於 lo
                events.append(Event("THRESHOLD", sensor, f"value {r.value:.2f} < {lo:.2f}", r))

            # 2) 重複時間戳
            if r.timestamp in seen_ts:              # 重複時間
                events.append(Event("DUP_TS", sensor, f"duplicate ts {r.timestamp}", r))
            else:                                   # 存不重複的
                seen_ts.add(r.timestamp)

            # 3) 間隔過大 停頓
            if prev is not None:
                gap = (r.ts - prev.ts).total_seconds() # 取得秒數
                if gap > max_gap_seconds:
                    events.append(Event("GAP", sensor, f"gap {gap:.2f}s > {max_gap_seconds:.2f}", r))
            prev = r

        # --- 4) OUT_OF_ORDER (local_seq 應遞增) ---
        last = -1
        for r in items:
            if r.local_seq < last:
                events.append(Event("OUT_OF_ORDER", sensor, f"local_seq {r.local_seq} < {last}", r))
            last = r.local_seq

    return events

def summarize(events: List[Event]) -> Dict[str, Dict[str, int]]:
    """
    回傳各事件種類總數 kind & 各 sensor 的事件數
    """
    summary = {                     # Dict[str, Dict[str, int]]
        "by_kind": defaultdict(int),
        "by_sensor": defaultdict(int),
    }
    for e in events:
        summary["by_kind"][e.kind] += 1
        summary["by_sensor"][e.sensor] += 1
    # 轉成普通 dict 便於輸出
    summary["by_kind"] = dict(summary["by_kind"])
    summary["by_sensor"] = dict(summary["by_sensor"])
    return summary