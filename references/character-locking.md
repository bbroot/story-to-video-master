# 角色锁定与生图规范（Phase 3.3 冻结闸门 + Phase 6 生图编排）

> 本文件是 story-to-video-master 在「**锁定角色**」与「**角色生图**」两个维度的工程化核心。
> 这两点是 novel→video 质量的生死线：AI 视频最大翻车点就是同角色跨镜头脸/身材/服饰漂移，
> 而小说改视频角色多、集数长，漂移会被指数放大。本规范把"锁定"做成**不可绕过的强制闸门**。

---

## 1. 角色注册表：唯一真相源

Phase 3 初始化、Phase 6 生图后回填，**全程不可被镜头 prompt 绕过**。

文件：`output/assets/character-registry.json`

```json
{
  "schema": "character-registry/v1",
  "characters": [
    {
      "char_id": "char_lindu",
      "name": "林渡",
      "canonical_identity": "年轻男性教官,身高约178,偏瘦,短黑发微乱,眉宇间常带审视,灰岩堡深灰制服配皮质护腕,左颊有一道旧疤",
      "three_view": { "front": "角色/林渡_front.png", "side": "角色/林渡_side.png", "back": "角色/林渡_back.png" },
      "seed": 12345,
      "expressions": {
        "neutral": "角色/林渡_exp_neutral.png",
        "angry": "角色/林渡_exp_angry.png",
        "sad": "角色/林渡_exp_sad.png"
      },
      "negative_constraints": [
        "禁止额外手指或肢体",
        "禁止五官变形或换脸",
        "禁止制服颜色/款式随机变化",
        "禁止发型突变"
      ],
      "locked": false
    }
  ]
}
```

- `canonical_identity`：从角色卡 `appearance.description` + `distinctive_features` 提炼成的**一句话权威描述**，是所有生图提示词的锚点，生图时原样注入。
- `seed`：平台支持时固定（即梦/RunningHub 可传 seed），是跨镜头同人的第二重保险。
- `locked`：由 `lock_character.py validate` 自动计算写入，**不以人工标记为准**。

---

## 2. 冻结闸门（强制，不可跳过）

**角色"锁定"充要条件**（全部满足才 `locked=true`）：
1. `three_view.front / side / back` 三个 PNG 文件均存在
2. `canonical_identity` 文本非空
3. `negative_constraints` 至少 1 条

**闸门规则（硬失败，不降级）**：
- 任何含该角色的镜头，在 Phase 6 生图前**必须** `python3 scripts/lock_character.py validate` 全绿。
- 未锁定角色**禁止进入生图**（脚本返回 `ok=false` 并列出缺失资产），不得"先生成再说"。
- 镜头 prompt 中的 `@角色名` / `@角色名-状态` **必须解析到其锁定参考图**；解析失败 → 显式报错指出缺哪张卡（`lock_character.py rebind` 负责校验）。

---

## 3. 角色生图编排（三视图链式 + 状态变体）

### 3.1 三视图「同一个人」保证（核心反漂移技术）
**绝不独立生成三张**。必须链式：
1. **先生成 front**（文生图），平台支持时**固定 seed**（如 `--seed 12345`）。
2. **side / back 用 front 作为参考图**（image2image / multimodal2video 的 `--image` 绑定），
   强制模型"基于这张脸/身材"衍生侧面与背面。
3. 三视图布局提示词见 Phase 3.1 模板（16:9 横版，左面部特写 + 右三身设定图，纯白背景）。

> 即梦：`dreamina_gen.py text2image --image 角色/林渡_front.png --prompt "侧面/背面三视图,…"`
> RunningHub：`runninghub_gen.py generate --endpoint seedance2.0/图生视频 --asset-ids <front下载URL>`
> LibTV：把 front 图 OSS URL 一并传给 session，由其后端保持同人。

### 3.2 状态 / 表情变体（供 `@角色名-状态` 复用）
为**高频情绪**生成变体 PNG，与 Phase 4.3「内心戏外化」对齐：
`neutral / angry / sad / tense / excited / hesitant`（至少 neutral + 该角色剧情高频情绪）。
存 `角色/<name>_exp_<state>.png`。
- 生变体同样以 **front 为参考图**衍生（保证同人），仅改变神态/表情描写。
- 分镜中 `@林渡-愤怒` 即绑定 `林渡_exp_angry.png`，避免每镜重新描述导致漂移。

### 3.3 落盘约定（与 Phase 6 目录一致）
```
output/<书籍名>/
└── 角色/
    ├── <name>_front.png / _side.png / _back.png   (三视图)
    ├── <name>_exp_<state>.png                      (情绪变体)
    ├── <name>.prompt.txt                           (三视图 T2I 提示词, 由 lock_character.py 生成)
    └── <name>_exp_<state>.prompt.txt               (变体 T2I 提示词)
```
> `角色/<name>.prompt.txt` 由 Phase 3 的 `lock_character.py write-prompt` 生成，Phase 6 直接 `cat` 使用，不在 Phase 6 现编。

---

## 4. 身份漂移回锚

- 若某镜头产出角色明显偏离锁定参考（多手指 / 换脸 / 服饰突变）→ **回锚**：
  用 `front` 参考图重喂 image2image 修正该镜头（提示词追加 `严格保持参考图人物身份`）。
- Phase 7 校验单必须含「**角色与注册表参考图肉眼比对**」步骤，发现漂移立即回锚重生成。

---

## 5. 质量门（Phase 3 / Phase 7 双签）

```
[ ] character-registry.json 含所有复用角色
[ ] 每个角色 front/side/back 三视图已生成 (validate 通过)
[ ] 每个高频情绪变体已生成
[ ] lock_character.py validate 全绿 (无未锁定角色)
[ ] 无镜头引用未锁定角色 / 未注册 @标签
[ ] Phase 7 比对无身份漂移
```

---

## 6. 与本 SKILL 其他模块的关系
- **Phase 3.1 角色卡**：提供 `appearance` / `distinctive_features` → 本文件提炼 `canonical_identity`。
- **Phase 4.3 内心戏外化**：情绪表 → 本文件决定生成哪些 `exp_<state>` 变体。
- **Phase 6 生图**：必须先在 Phase 3 用 `lock_character.py write-prompt` 落盘提示词，生图前 `validate` 闸门。
- **Phase 7 校验**：回锚逻辑依赖本文件注册表。
