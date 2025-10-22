
from dataclasses import dataclass                   # 用來宣告資料結構 (自動產生 __init__ 等)
from datetime import datetime                       # 解析時間字串用
from typing import Iterator, List, Optional         # 型別註解
import json                                         # 解析JSON 每行

@dataclass
class SensorRow:
    timestamp: str      # 原始字串時間
    sensor: str         # 感測器名稱
    value: float        # 數值
    thread_id: str      # 產生該筆資料的 thread
    global_seq: int     # 全域序號 (整體流水號，可選)
    local_seq: int      # 感測器內的在地序號 (用來偵測 out-of-order)
    ts: datetime        # 解析後的時間 (方便排序/運算)

def parse_line_to_row(line: str) -> Optional[SensorRow]:
    """
    將一行 JSON 文字轉成 SensorRow
    失敗 (格式錯) 就回傳 None，不中斷整體流程
    """
    try:
        data = json.loads(line)                      # 解析 JSON 行-> dict
        # print(f"data: {data}")
        # 修正: value 一定要是 float，避免字串/整數混用
        data["value"] = float(data["value"])
        # 把字串時間轉成 datetime
        ts = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
        # 建出資料列物件 (多補上 ts 欄位)
        return SensorRow(
            timestamp=data["timestamp"],
            sensor=data["sensor"],
            value=data["value"],
            thread_id=str(data.get("thread_id", "")),
            global_seq=int(data.get("global_seq", 0)),
            local_seq=int(data.get("local_seq", 0)),
            ts=ts
        )
    except Exception as e:
        print(f"[WARN] line skipped: {e}")           # 不拋例外，友善略過壞行
        return None

def parse_jsonl(path: str) -> List[SensorRow]:
    """讀取 JSONL 檔（每行一筆 JSON），回傳整理好的 SensorRow 清單。"""
    rows: List[SensorRow] = []                                # 預先建立 list
    with open(path, "r", encoding="utf-8") as f:              # 逐行讀
        for line in f:
            line = line.strip()                               # 去除換行/空白
            if not line:                                      # 空行略過
                continue
            row = parse_line_to_row(line)                     # 嘗試解析
            if row is not None:                               # 成功才加入
                rows.append(row)
    return rows