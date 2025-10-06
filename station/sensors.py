# 這個檔案放 "感測器" 的具體實作
# 我們先做一個 Mock 溫度感測器，方便在沒有硬體時也能練習。

from __future__ import annotations
import random
from dataclasses import dataclass
from .abc_types import TemperatureSensor, Sample

@dataclass
class MockTemperatureSensor(TemperatureSensor):
    """
    模擬一顆溫度感測器的實作:
    - base_c: 基準溫度 (例如環境常溫 28C)
    - noise : 雜訊幅度 (用來模擬現實世界的微小波動)
    - _rnd  : 隨機數產生器 (可固定種子，讓結果可重現)
    """
    base_c: float = 28.0
    noise: float = 1.5
    _rnd: random.Random = random.Random(42) # 預設 seed=42，可重現

    def read_celsius(self) -> Sample:
        """
        實作介面規範的 read_celsius():
        用 base + 隨機雜訊 產生一個模擬數值，並包成 Sample 回傳。
        """
        # 以 base_c 為中心，加上一個在 [-noise, noise] 的隨機偏移量」
        # 範圍就是 [-noise, +noise]
        reading = self.base_c + self._rnd.uniform(-self.noise, self.noise)
        return Sample(name="temperature", value=round(reading, 2), unit="C")


"""
模擬感測器
package com.example.station.sensor.impl;

import java.util.Random;

import com.example.station.model.Sample;
import com.example.station.sensor.TemperatureSensor;

/**
 * 模擬一顆溫度感測器：
 * baseC: 基準溫度
 * noise: 雜訊幅度
 * rnd  : 固定 seed 以利重現
 */
public class MockTemperatureSensor implements TemperatureSensor {
    private final double baseC;
    private final double noise;
    private final Random rnd;

    public MockTemperatureSensor() {
        this(28.0, 1.5, 42L);
    }

    public MockTemperatureSensor(double baseC, double noise, long seed) {
        this.baseC = baseC;
        this.noise = noise;
        this.rnd = new Random(seed);
    }

    @Override
    public Sample readCelsius() {
        double reading = baseC + (rnd.nextDouble() * 2 * noise - noise); // [-noise, +noise]
        double rounded = Math.round(reading * 100.0) / 100.0;
        return new Sample("temperature", rounded, "C");
    }
}
"""