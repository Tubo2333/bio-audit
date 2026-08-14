# B4 完成报告（阶段 1 · 轨迹迁移器）— 2026-08-14

> 执行窗口 ⑥（窗口 B 内）· B4：轨迹 schema 加 version + 20 条旧轨迹迁移 v2
> （provenance 标 legacy）+ 只读迁移器 + 迁移后 golden 0 差异 + schema 校验器 + 迁移清单。
> 依据：refactor-plan-v1.1 C2（轨迹 schema version + 只读迁移器）、audit-report A15、
> execution-plan-v1 §六.五（B4 清单，已冻结）。
> 验收：**B4 验收清单 6 项全部通过**（见下逐项打勾）。

## 一、产出清单

```
src/bioaudit/models/trajectory.py      # ★ 轨迹 v2 schema（version 必填）+ TrajectoryProvenance
                                       #   + validate_trajectory（A15 显式报错）+ schema 常量
src/bioaudit/report/schema.py          # ★ report/schema 常量定义（再导出，单一事实源）
src/bioaudit/capture/trajectory_migrator.py  # ★ 只读迁移器（TrajectoryMigrator，绝不写 src）
src/bioaudit/paths.py                  # TRAJECTORIES_DIR → data/trajectories/v2（canonical）；
                                       #   TRAJECTORIES_LEGACY_DIR → v1 原文件（备份）
src/bioaudit/data/trajectories/v2/     # ★ 20 条 v2 轨迹（迁移产物，评分 0 漂移）
scripts/migrate_trajectories.py        # 迁移入口（薄包装；--dry-run 不写盘）
src/bioaudit/cli.py                    # + migrate-trajectories / trajectory-validate 子命令
ui/app.py                              # v2 对象/数组统一取 decisions
tests/test_trajectory_v2.py            # ★ 迁移器/schema/只读/golden 测试（13 项）
```

## 二、v2 schema（摘要）

```jsonc
{
  "version": 2,                       // ★必填（无默认；≠2 → validation-error）
  "trajectory_id": "deg_correct",     // ★必填
  "act": "deg",                       // 可选；迁移器按文件名前缀推断（deg_/pan_/scrna_）
  "provenance": {
    "source": "legacy",               // C2：旧轨迹标 legacy
    "migrated_from": "deg_correct.json",
    "migrated_at": "<ISO 时间戳>",
    "migrator": "bioaudit.capture.trajectory_migrator",
    "note": "v1 → v2 迁移：新增 version/provenance/act 元数据；decisions 内容逐条保留，不参与评分"
  },
  "decisions": [/* 与 v1 完全一致的决策数组 */]
}
```

**不变量**：`version/provenance/act` 是纯元数据，评分引擎只消费 `decisions` →
迁移后 golden 重放仍 0 差异（基线未更新，无漂移）。

## 三、迁移器设计（只读，B4 验收项 3）

- 输入 `src_dir`（默认 `data/trajectories/`，20 条 v1 裸数组）→ 输出 `dst_dir`
  （默认 `data/trajectories/v2/`）；**只写 dst，src 文件字节不变**（测试有哈希守卫）；
- 输入已是 v2 → 仅校验（幂等，不重复包装）；
- 每个迁移产物先过 `validate_trajectory` 再落盘（A15）；
- 用法：`bio-audit migrate-trajectories [--dry-run]` 或
  `python scripts/migrate_trajectories.py`。

## 四、20 条迁移清单（B4 验收项 6）

迁移时间：2026-08-14T15:36:29Z（UTC）；迁移器：`bioaudit.capture.trajectory_migrator`；
v1 原文件保留于 `data/trajectories/`（即备份，字节哈希未变）；v2 产物位于
`data/trajectories/v2/`，新文件名与原文件名一致。

| # | 轨迹文件 | act | 决策数 | sha256（v1 原文件，未变） | sha256（v2 产物） |
|---|----------|-----|--------|--------------------------|-------------------|
| 1 | deg_correct.json | deg | 5 | `bb41f30d…62a2` | `ac496877…cf0f` |
| 2 | deg_edge_n2.json | deg | 1 | `e1b50248…82b` | `e3e442d9…a4c0` |
| 3 | deg_edge_nofilter.json | deg | 3 | `84890a32…b31` | `257e5be1…15d2` |
| 4 | deg_error.json | deg | 5 | `8a77175e…99f` | `4f80e3d0…456f` |
| 5 | pan_correct.json | pan | 16 | `897e288b…04c` | `f2761039…a03b` |
| 6 | pan_edge_claim.json | pan | 1 | `ba676bb6…8d9` | `82a2854b…6366` |
| 7 | pan_edge_consistency.json | pan | 1 | `dc83d740…757` | `abe96785…da34` |
| 8 | pan_edge_epv.json | pan | 1 | `272183a5…e17` | `8d5328d2…5b61` |
| 9 | pan_edge_purity.json | pan | 1 | `6b80e108…5d0f` | `f9630291…7981` |
| 10 | pan_error.json | pan | 16 | `c40fffd4…700` | `3aa15727…2643` |
| 11 | scrna_correct.json | scrna | 12 | `f9128e91…c8c1` | `8ae049c1…56a2` |
| 12 | scrna_crc_correct.json | scrna | 12 | `ad1b2e2f…3d31` | `c43c5b3c…52dc` |
| 13 | scrna_crc_error.json | scrna | 12 | `710ab64e…2c2c` | `932026dc…0253` |
| 14 | scrna_edge_default.json | scrna | 1 | `9ca59c43…88e` | `89c78645…1f35` |
| 15 | scrna_edge_nodoublet.json | scrna | 1 | `b807e92c…a4a4` | `da4d2db4…ae46` |
| 16 | scrna_edge_singleanno.json | scrna | 1 | `6e6a1110…4742` | `30f18689…75e6` |
| 17 | scrna_error.json | scrna | 12 | `1542da9c…f053` | `69eb5a6a…355a` |
| 18 | scrna_melanoma_cellvoyager.json | scrna | 12 | `d69f2d07…5531` | `1b74abece…dd5b` |
| 19 | scrna_melanoma_correct.json | scrna | 12 | `ab7ddf12…bb7b` | `2e9e2886…4c7` |
| 20 | scrna_nsclc_correct.json | scrna | 12 | `b66e9671…ac5` | `63470734…d4ca` |

> 完整 64 位哈希见迁移时生成的校验记录（v1 哈希与 `docs/specs/2026-08-13-golden-baseline/`
> asset_manifest.json 中旧轨迹条目一致；v2 为新增工件，不在旧 manifest 范围，
> 哈希已随本报告留档）。所有 20 条 v2 的 `provenance.source == "legacy"`，
> `provenance.migrated_from == 原文件名`，`decisions` 与 v1 逐条语义一致（测试守卫）。

## 五、B4 验收清单逐项打勾（execution-plan-v1 §六.五）

- [x] **1. 轨迹 schema 加 version 字段（v1.1 C2）；report/schema 常量定义**
      → `models/trajectory.py`：`TRAJECTORY_SCHEMA_VERSION=2`（version 必填，无默认）、
      `LEGACY_TRAJECTORY_VERSION=1`、`PROVENANCE_SOURCE_LEGACY`；
      `report/schema.py` 再导出（单一事实源）；测试 `test_schema_constants`。
- [x] **2. 20 条旧轨迹迁移为 v2：provenance {source: legacy, ...} 标注，旧文件保留备份**
      → `data/trajectories/v2/` 20 条全部 `provenance.source="legacy"` + migrated_from/migrated_at/
      migrator/note；v1 原文件原位保留（哈希不变，即备份）；测试
      `test_migrate_all_20_to_v2` / `test_v2_decisions_equal_v1`。
- [x] **3. 迁移器为只读工具（输入旧轨迹 → 输出新轨迹文件，不改原文件）**
      → 只写 dst_dir；src 目录零写入（测试 `test_migrator_read_only_does_not_touch_originals`
      逐文件哈希守卫；`test_migrator_dry_run_writes_nothing`）。
- [x] **4. 迁移后 golden 仍 0 差异（version/provenance 是元数据，不得改变评分）**
      → `scripts/golden_replay.py`：✅ 0 差异（20 轨迹 137 决策，基线未更新）；
      测试 `test_golden_zero_diff_after_migration`。
- [x] **5. schema 校验器：v2 轨迹缺必填字段时显式报错（audit-report A15）**
      → `validate_trajectory`：version/trajectory_id/provenance/decisions 任一缺失或
      version≠2 → `BioAuditError(validation-error)` 带字段明细；
      测试 `test_v2_missing_required_field_explicit_error[4 字段]` +
      `test_v2_unsupported_version_explicit_error`；CLI `bio-audit trajectory-validate`
      对坏文件返回退出码 1。
- [x] **6. 迁移报告：20 条轨迹迁移清单（新文件名/版本/provenance 标注）**
      → 本报告 §四（20 行清单 + 版本 + provenance 标注 + 双哈希）。

## 六、验证记录

| 验证 | 结果 |
|------|------|
| 迁移前 20 条 v1 哈希 vs 迁移后 | ✅ 逐文件 SHA256 完全一致（未动原文件） |
| v2 产物 schema 检查（version=2 / source=legacy / decisions 一致） | ✅ 20/20 通过 |
| `python scripts/golden_replay.py` | ✅ 0 差异（20 轨迹 137 决策） |
| `python -m pytest -q` | ✅ 75 passed |
| `python scripts/check_no_cwd_paths.py` | ✅ 未发现相对 cwd 路径 |
| `bio-audit migrate-trajectories --dry-run` | ✅ 20 条清单，不写盘 |
| `bio-audit trajectory-validate`（坏文件） | ✅ 退出码 1 + validation-error |

## 七、遗留项

- 轨迹 v2 的 `provenance.source` 未来扩展：capture（M1/M3，阶段 2）与 manual；
- 资产清单：旧 asset_manifest.json（2026-08-13 冻结基线）覆盖 v1 原文件（哈希未变），
  v2 产物为新增工件，哈希已在本报告留档；若 B6 数据管线需统一清单可再生成 v2 段。
