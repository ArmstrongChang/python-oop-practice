# 這個檔案定義 "測試項目"
# 測項通常會讀取一個或多個感測器值，拿來和限值比較，最後輸出PASS/ FAIL。

from __future__ import  annotations
from dataclasses import dataclass
from typing import Dict, Any
from .abc_types import TestItem, TemperatureSensor

@dataclass
class TemperatureLimitTest(TestItem):
    """
    "溫度區間檢查" 測試:
    - name      : 測項名稱 (例如 'TEMP_RANGE_CHECK')
    - sensor    : 任何符合 TemperatureSensor 介面的實例 (可 Mock、可真實)
    - low       : 下限
    - high      : 上限
    """
    name: str
    sensor: TemperatureSensor
    low: float
    high: float

    def run(self) -> Dict[str, Any]:
        """
        執行一次量測 -> 和上下限比較 -> 回傳標準化的 dict 結果，
        注意: 這裡不寫印出或存檔，純邏輯; I/O 交給上層 (cli)。
        """
        sample = self.sensor.read_celsius()
        ok = self.low <= sample.value <= self.high

        # 回傳結構化結果，未來存CSV/SQLite/上傳 API都很方便
        return {
            "test" :self.name,
            "measurement": {
                "name": sample.name,
                "value": sample.value,
                "unit": sample.unit,
            },
            "limits": {
                "low": self.low,
                "high": self.high
            },
            "result" : "PASS" if ok else "FAIL",
        }


"""
區間判定測項
package com.example.station.testitem.impl;

import java.util.HashMap;
import java.util.Map;

import com.example.station.model.Sample;
import com.example.station.sensor.TemperatureSensor;
import com.example.station.testitem.TestItem;

/**
 * 溫度上下限檢查測項：
 * - 讀取一次溫度
 * - 比對 [low, high] 區間
 * - 回傳標準化結果（之後容易存檔/上傳）
 */
public class TemperatureLimitTest implements TestItem {
    private final String name;
    private final TemperatureSensor sensor;
    private final double low;
    private final double high;

    public TemperatureLimitTest(String name, TemperatureSensor sensor, double low, double high) {
        this.name = name;
        this.sensor = sensor;
        this.low = low;
        this.high = high;
    }

    @Override
    public String getName() { return name; }

    @Override
    public Map<String, Object> run() {
        Sample s = sensor.readCelsius();
        boolean ok = (s.getValue() >= low) && (s.getValue() <= high);

        Map<String, Object> measurement = new HashMap<>();
        measurement.put("name", s.getName());
        measurement.put("value", s.getValue());
        measurement.put("unit", s.getUnit());

        Map<String, Object> limits = new HashMap<>();
        limits.put("low", low);
        limits.put("high", high);

        Map<String, Object> result = new HashMap<>();
        result.put("test", name);
        result.put("measurement", measurement);
        result.put("limits", limits);
        result.put("result", ok ? "PASS" : "FAIL");
        return result;
    }
}
"""