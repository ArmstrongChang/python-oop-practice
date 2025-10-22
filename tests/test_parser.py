#test/test_parser.py
from src.parser import read_log
from pathlib import Path

def test_read_log():
    # 採用絕對路徑解析
    file_path = Path(__file__).parent.parent / "sample" / "multi_sensor_log.jsonl"
    # rows = read_log("sample/multi_sensor_log.jsonl") # 相對路徑因為執行目錄在tests底下，導致找不到sample目錄下的檔案
    rows = read_log(file_path)
    assert len(rows) > 0
    assert all(hasattr(r, "sensor") for r in rows)