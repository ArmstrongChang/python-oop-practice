from __future__ import annotations
from abc import ABC, abstractmethod #ABC = Abtract Base Class
from dataclasses import dataclass
from typing import Dict, Any

#這個檔案放 抽象層 定義(介面) :  不關心 "怎麼做"，只規範"長什麼樣"
# 在 Python 專案裡，沒有硬性規範一定要像 Java 一樣「一個檔一個 class」
# 小型專案/範例 常會把相關的抽象 / 型別定義放在同一支檔，方便管理
# 大型專案 會拆成 sample.py, sensor_base.py, testitem_base.py 這樣比較清楚

# @dataclass 是語法糖，幫你自動生成一些樣板程式碼，如下:
# __init__() → 建構子
# __repr__() → 印出好看的字串
# __eq__() → 可以直接比對兩個 Sample 是否相等
@dataclass
class Sample:
    """
     一筆量測資料的標準型態。
     - name: 量測項目名稱 (如 'temperature')
     - value: 量測數值 (float)
     - unit: 單位 (如 'C'、'V')
     用 dataclass 自動產生 __init__/__repr__等樣板程式碼。
    """
    name: str
    value: float
    unit: str

class TemperatureSensor(ABC):
    """
    溫度感測器的 "介面": 任何溫度感測器都必須提供 read_celsius()
    不用管內部是 USB、Serial、NI-DAQ; 重點是回傳一筆 Sample。
    如同JAVA的 Sample readCelsius()
    """
    @abstractmethod
    def read_celsius(self) -> Sample:
        """
        讀取目前攝氏溫度。子類別必須實作
        """

        ...

class TestItem(ABC):
    """
    測試項目的 "介面": 每個測項至少要有 name 與 run()。
    run() 回傳一個標準化的 dict，方便統一紀錄或上傳
    Dict[str, Any] 如同 JAVA Map<String, Object>
    """
    name: str

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        執行測試項目並回傳結果 (結構化 dict)，子類別必須實作。
        """
        ...