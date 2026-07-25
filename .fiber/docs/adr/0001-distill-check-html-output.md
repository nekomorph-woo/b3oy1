# ADR-0001：`distill --check` HTML 报告产物约定

- 状态：Accepted
- 日期：2026-07-25
- 关联：wayfinder map #3、ticket #7（产物落点）、ticket #6（`--check` 实现）

## 背景

`scripts/distill.py` 即将新增 dry-run 检查模式 `--check`（map #3 / ticket #6），
产出一份自包含 HTML 报告。在实现落地前，需先固定产物文件的落点、命名、生命周期
约定，避免实现期临时拍脑袋，也避免产物被误入库。

## 决策

1. **固定默认文件名**：`distill-check.html`，落在仓库根（即 `cwd`）。
2. **覆盖语义**：每次 `--check` 直接覆盖同路径文件，**不堆历史、不带时间戳、不先删**。
3. **可覆盖路径**：CLI 提供 `--check-out <path>`，用户指定自定义输出路径。
   未传则用默认 `distill-check.html`。
4. **不入库**：`distill-check.html` 加入 `.gitignore`。
   仅忽略默认文件名；`--check-out` 自定义路径由用户自行管理。

## 与其它 ticket 的关系

- 独立于 #4（前缀噪音与 diff 数据来源）、#5（HTML 布局）——本约定只管产物落点，
  不管报告内容。
- #6（`--check` 实现）遵循本约定的文件名 / 路径 / 覆盖语义。

## 后果

- 报告是本地查看用的一次性产物，不留版本痕迹；如需存档，用户自行 `--check-out`
  到带时间戳的路径或另行保存。
