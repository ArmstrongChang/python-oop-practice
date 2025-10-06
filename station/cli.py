# 這是命令列入口 (Entry Point):
# - 解析參數 (device-id、iterations、上下限)
# - 建立感測器與測項 (依賴注入: 將實作丟給介面)
# - 反覆執行測項、彙整結果
# - 以 JSON 輸出到標準輸出 (stdout)，方便被其他程式/ 腳本接管

from __future__ import annotations
import argparse
import json
from typing import Any, Dict, List

from station.sensors import MockTemperatureSensor
from station.test_items import TemperatureLimitTest

def main() -> None:
    # 1) 解析命令列參數
    parser = argparse.ArgumentParser(description="Run a simple manufacturing test sequence.")
    parser.add_argument("--device-id", required=True, help="裝置/工件編號 (用於追溯) ")
    parser.add_argument("--iterations", type=int, default=1, help="重複執行次數")
    parser.add_argument("--low", type=float, default=20.0, help="溫度下限(°C)")
    parser.add_argument("--high", type=float, default=40.0, help="溫度上限(°C)")
    args = parser.parse_args()

    # 2) 建立感測器 (先用 Mock ; 未來可改成真實 Sensor 實作)
    sensor = MockTemperatureSensor()

    # 3) 組裝測試序列 (可放多個測項 ; 此處示範單一測項)
    sequence: List[TemperatureLimitTest] = [
        TemperatureLimitTest(
            name="TEMP_RANGE_CHECK",
            sensor=sensor,
            low=args.low,
            high=args.high,
        )
    ]

    # 4) 執行流程並彙整結果
    summary: Dict[str, Any] = {
        "device_id": args.device_id, #?
        "iterations": args.iterations,
        "results": [],
    }

    for i in range(args.iterations):
        iteration = {"iteration": i + 1, "items": []}
        for item in sequence:
            iteration["items"].append(item.run())
        summary["results"].append(iteration)

    # 5) 以 JSON 輸出 (stdout)
    # json.dumps(obj) = 把 Python 的物件（dict、list 等）序列化成 JSON 格式的字串
    # indent=2 => 美化輸出，讓 JSON 用 縮排 2 個空格 排版，輸出會自動換行 + 排版
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    # 允許用 'python station/cli.py ...' 直接執行此檔
    # 也可用 'python -m station.cli ...' 重套件模式執行。
    main()


"""
package com.example.station.cli;

import java.util.*;

import com.example.station.sensor.impl.MockTemperatureSensor;
import com.example.station.testitem.TestItem;
import com.example.station.testitem.impl.TemperatureLimitTest;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

/**
 * 命令列執行：
 * 參數：
 *   --device-id <ID>（必填）
 *   --iterations <N>（預設 1）
 *   --low <L>（預設 20.0）
 *   --high <H>（預設 40.0）
 *
 * 範例：
 *   java -cp target/test-station-java-0.1.0.jar com.example.station.cli.Main \
 *        --device-id MFG-001 --iterations 3
 */
public class Main {
    private static class Args {
        String deviceId = null;
        int iterations = 1;
        double low = 20.0;
        double high = 40.0;
    }

    private static Args parseArgs(String[] argv) {
        Args a = new Args();
        for (int i = 0; i < argv.length; i++) {
            switch (argv[i]) {
                case "--device-id":
                    if (i + 1 < argv.length) a.deviceId = argv[++i];
                    break;
                case "--iterations":
                    if (i + 1 < argv.length) a.iterations = Integer.parseInt(argv[++i]);
                    break;
                case "--low":
                    if (i + 1 < argv.length) a.low = Double.parseDouble(argv[++i]);
                    break;
                case "--high":
                    if (i + 1 < argv.length) a.high = Double.parseDouble(argv[++i]);
                    break;
                case "-h":
                case "--help":
                    printHelpAndExit(0);
                    break;
                default:
                    System.err.println("Unknown arg: " + argv[i]);
                    printHelpAndExit(1);
            }
        }
        if (a.deviceId == null) {
            System.err.println("Missing required: --device-id");
            printHelpAndExit(1);
        }
        return a;
    }

    private static void printHelpAndExit(int code) {
        System.out.println("Usage: java ... Main --device-id <ID> [--iterations N] [--low L] [--high H]");
        System.exit(code);
    }

    public static void main(String[] argv) {
        Args args = parseArgs(argv);

        // 建立感測器（目前使用 Mock；日後可換成真實實作）
        MockTemperatureSensor sensor = new MockTemperatureSensor();

        // 建立測項清單（可加多個）
        List<TestItem> sequence = List.of(
                new TemperatureLimitTest("TEMP_RANGE_CHECK", sensor, args.low, args.high)
        );

        // 執行流程並彙整結果
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("device_id", args.deviceId);
        summary.put("iterations", args.iterations);

        List<Map<String, Object>> results = new ArrayList<>();
        for (int i = 0; i < args.iterations; i++) {
            Map<String, Object> iteration = new LinkedHashMap<>();
            iteration.put("iteration", i + 1);

            List<Map<String, Object>> items = new ArrayList<>();
            for (TestItem item : sequence) {
                items.add(item.run());
            }
            iteration.put("items", items);
            results.add(iteration);
        }
        summary.put("results", results);

        // 輸出 JSON（縮排方便閱讀）
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        System.out.println(gson.toJson(summary));
    }
}
"""