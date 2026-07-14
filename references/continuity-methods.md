# 连续性收口方法（Phase 3/4 质控）

> 跨镜头角色一致性 + 场景连续性，是 AI 视频最大的翻车点。本文件给出工程化收口方法。

## 一、角色一致性（三视图前置锁定）

源自专业分镜工作站的强制方法论：**先建角色卡节点（含三视图），再写镜头节点**。

1. Phase 3 为每个复用角色生成 `characterSheet`：
   - 正面 / 侧面 / 背面三视图（front/side/back）
   - 固定体型、发色、服饰、标志性配饰
2. 镜头 prompt 使用 `@角色名@char_id` 绑定，工具链据此注入三视图锚点
3. 反向约束（`negativeConstraints`）锁定：
   - 同一角色全程五官清晰稳定不变形
   - 禁止额外手指/肢体
   - 禁止服饰随机变化

## 二、场景连续性

1. 每个复用场景先有 `visualRefId` 视觉参考资产（场景卡 JSON）
2. 镜头 `scene` 字段引用 `scene_id`，确保取景一致
3. `continuityLocks` 标注跨镜头必须保持的元素（如"开场帧→角色位置"）

## 三、地理连续性（novel-master v2 专属）

- 读取 `tracker/plot_bus.json` 的 `character_move` 事实 → 校验某角色在某集是否应出现在某地点
- 读取 `settings/characters/<名>/state.json` 的 `location` → 角色当前所在
- 若分镜把角色放在与其 v2 状态矛盾的地点 → 标红修正（继承 novel-master 量子审计的 geo 维度）

## 四、伏笔/道具连续性

- `tracker/foreshadowing.json` 的「内容」→ 关键道具（如铁片）外观需跨集一致
- `continuityLocks` 标注"铁片纹路/材质"等必须在特写中保持一致

## 五、收口检查单

```
[ ] 所有跨镜头复用角色均有 characterSheet 三视图
[ ] 所有跨镜头复用场景均有 visualRefId
[ ] 角色地理位置与 plot_bus/state 一致
[ ] 关键道具外观跨集一致
[ ] 无"突然""莫名"类跳变（继承 novel-master 禁忌词）
```
