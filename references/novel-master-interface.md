# novel-master 接口规范（Phase 0 读取 + Phase 7 回写）

> 本文档精确描述与 novel-master 真实 v2 项目的读写契约。所有路径与键名均来自
> 用户《觉醒》项目的实际结构（已验证）。

## 一、Phase 0 读取契约（只读）

### 1.1 角色数据（每个角色一个子目录）
```
settings/characters/<角色名>/
  ├─ voice.md        → 声线卡（身份/状态/情绪值/认知偏差/关系网）
  ├─ state.json      → v2 状态机
  └─ bias_pack.json  → 认知偏差包（sensory_mapping/decision_bias/speech_tells/forbidden_generic）
```
`state.json` 真实字段（中文/英文混合，脚本需兼容）：
`name, identity, version, snapshots, location, is_dead, known_info_boundary, emotion_value, relationship_net_version, relationships{type,strength}, cognitive_bias_pack, updated_chapter`

### 1.2 大纲（按卷命名）
```
outline/arc-outline.md
outline/arc1-觉醒-outline.md
outline/arcN-<卷名>-outline.md   ← 命名规律：arc + 序号 + 卷名 + -outline
```

### 1.3 章节（整卷文件，按集切分）
```
chapters/arc1-觉醒.md   ← 内含：
  ## 第1集 《觉醒之夜》    ← 集标记（正则：^##\s*第\d+集）
  ### 壹·一               ← 小节标记（正则：^###\s*[\u4e00-\u9fa5]+·[一二三四五六七八九十]+）
```
切分逻辑：以 `## 第N集` 为一个可改编单元；`### 壹·一` 为小节。

### 1.4 追踪数据（中文键名，必须兼容）
`tracker/foreshadowing.json`：
```json
{ "伏笔列表": [ { "编号":"fp-002a", "埋入章节":1, "内容":"...", "暗示层次":"轻",
                 "预期回收章节":7, "回收状态":"已部分回收(第一部内)", "备注":"..." } ] }
```
`tracker/conflicts.json`：
```json
{ "冲突列表": [ { "type":"death", "who":"苏白", "chapter":4, "desc":"..." } ] }
```

### 1.5 其它
- `tracker/plot_bus.json`：`[{ "chapter":N, "facts":[{ "type":"character_move","who":..,"to":.. }] }]`
- `tracker/ncg.json`：`{ "nodes":[{id,chapter,text,tags,edges}], "super_nodes":[...] }`
- `tracker/style-log.md`：文风日志，含「日漫风格增强」段落（括号体独白/慢镜头标记）
- `state.json`：`{ book, author, current_arc, current_chapter, total_words, ... }`

### 1.6 兼容模式（降级）
若检测到英文键名（`Foreshadowing`/`Conflicts`）或每章独立文件 → 启用兼容解析，不影响主流程。

## 二、Phase 7 回写契约（显式确认后写）

回写至 novel-master 项目目录，不破坏源数据：
```
<书名>/
├─ output/storyboard/   → storyboard-第N集.json + storyboard-第N集.md
├─ output/assets/       → assets-characters.json + assets-scenes.json（角色三视图/场景卡提示词）
└─ tracker/《改编状态追踪.md》 → 分集×钩子×伏笔回收映射表
```

### 2.1 《改编状态追踪.md》模板

```markdown
# 《觉醒》改编状态追踪

> 由 story-to-video-master v2.1.0 自动生成（Phase 7 回写）

## 分集×钩子×伏笔映射
| 集号 | 源章节 | 集尾钩子 | 钩子类型 | 关联伏笔 | 回收进度 |
|------|--------|---------|---------|---------|---------|
| 第1集 | arc1-觉醒.md 第1集 | E1-H1 铁片存在 | 信息差 | fp-002a | 未回收 |
| 第2集 | arc1-觉醒.md 第2集 | H2 铁片=枪管材质 | 真相 | fp-002c | 跨部待回收 |

## 角色资产锁定状态
| 角色 | character_id | 三视图 | 状态 |
|------|-------------|--------|------|
| 陆沉 | char_luchen | front/side/back | 已锁定 |
| 林渡 | char_lindu | front | 待补侧/背 |

## 场景资产锁定状态
| 场景 | scene_id | 参考图 | 状态 |
|------|---------|--------|------|
| 工坊·晨 | scene_gongfang | — | 已锁定 |

## 连续性校验
- 地理一致性：✅（对照 plot_bus）
- 伏笔一致性：⚠️（fp-002d 跨部，第3集标注待回收）
- 角色一致性：✅
```

## 三、读写安全原则
- Phase 0~6 全程**只读** novel-master，绝不修改源文件
- Phase 7 回写仅在用户确认后执行，且只写入 `output/` 与新增 `tracker/《改编状态追踪.md》`
- 回写不覆盖 novel-master 已有任何文件
