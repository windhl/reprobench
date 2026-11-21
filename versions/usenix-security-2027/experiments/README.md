# 实验

当前没有新增 agent 运行。这里保存对历史实验的只读清单，支撑英文草稿中的归档数量；它不等同于新的结果核验或轨迹分析。

- `inventory_archive.py`：读取历史 evaluator JSON，统计目录可用性、候选触发标签和模拟标签，记录每个注释文件的 SHA-256。不会执行漏洞产物、调用模型或改动原始材料。
- `archive-inventory-2026-11-19.json`：本次清单，450 个运行位置、30 CVE、5 个原始模型标签；395 个 trace 和 427 个 workspace 目录非空。

候选触发标签为 16 次、5 个 CVE、8 个 CVE–模型组；仍须逐次核验，不能称作新稿的已验证成功率。当前注释中 simulation 任一条目出现于 316 次、至少一条 terminal simulation 出现于 209 次，11 次运行有多个 terminal 条目；旧稿 204 次的口径差异待查。

复算示例，`--archive` 替换为实际历史数据目录：

```sh
python3 versions/usenix-security-2027/experiments/inventory_archive.py \
  --archive /path/to/historical/eval \
  --output versions/usenix-security-2027/experiments/archive-inventory.json
```

完整 outcome、缺失原因、行为标签和统计分析尚未完成，见草稿中的 TODO。清单不复制原始固件、完整 trace 或含敏感值的日志。
