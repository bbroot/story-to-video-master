# 分镜规范参考（Phase 4）

> 好莱坞分镜语法体系 + storyboard-director/v1.1 兼容 JSON 规范。

## 一、景别（Shot Size）

| 代码 | 英文 | 说明 |
|------|------|------|
| ELS | Extreme Long Shot | 大远景，环境主导 |
| LS | Long Shot | 远景，人物全身入景 |
| FS | Full Shot | 全景，人物全貌 |
| MS | Medium Shot | 中景，腰以上 |
| MCU | Medium Close-Up | 近景，胸以上 |
| CU | Close-Up | 特写，面部/局部 |
| ECU | Extreme Close-Up | 大特写，细节 |

## 二、运镜（Camera Movement）

| 代码 | 说明 |
|------|------|
| 固定 | 镜头静止 |
| 推 | 向主体靠近（强调、压迫） |
| 拉 | 远离主体（揭示环境、抽离） |
| 摇 | 水平/垂直旋转 |
| 移·跟 | 平移/跟随主体 |
| 手持 | 晃动真实感（紧张/纪实） |
| 急推·急拉 | 快速变焦（冲击、惊愕） |

## 三、分镜数量判断（先问四问）

1. 有几个视觉重点？
2. 动作有无变化？
3. 情绪有无起伏？
4. 是否需要景别切换强调？

| 单集字数（切分后估算） | 镜头数 |
|----------------------|--------|
| ≤1200 | 6-8 |
| 1201-2500 | 8-12 |
| >2500 | 12-16 |

## 四、内心戏转译规则（继承 novel-master 展示而非告知）

| 心理状态 | 外化动作 | 外化场景 |
|---------|---------|---------|
| 愤怒 | 拍桌/摔杯/咬牙 | 暴雨独行 |
| 悲伤 | 低头沉默/手握拳 | 空房间独坐 |
| 紧张 | 手指反复敲击 | 黑暗走廊 |
| 恐惧 | 瞳孔放大/后退/声颤 | 阴影逼近 |
| 兴奋 | 眼神发光/小动作 | 阳光洒入 |
| 犹豫 | 来回踱步/反复握拳松拳 | 十字路口 |

## 五、日漫风格层（来自 style-log 标记）

若 `tracker/style-log.md` 标注：
- `「角色的内心独白」` 括号体 → 设计"独白穿插镜"（角色面部+极简背景+留白）
- `慢镜头·X视角` → 设计"高光慢镜头"（特写+降帧+光效）
- 不破坏冷峻骨架：日漫元素落在情绪高点，用量克制

## 六、storyboard-director/v1.1 JSON Schema

```json
{
  "schemaVersion": "storyboard-director/v1.1",
  "chapter": "第N集",
  "sourceChapter": "arcX-*.md 具体标记",
  "globalStyle": "电影写实|日系动漫|2.5D",
  "cast": ["char_id_1", "char_id_2"],
  "relationshipGraph": "文字关系描述",
  "modelingSpec": {"材质风格":"","表面磨损":"","纹理精度":""},
  "atmosphereSpec": {"整体氛围":"","情绪基线":""},
  "referencedAssets": {
    "characterSheets": ["assets/char_x_front.png"],
    "sceneSheets": ["assets/scene_y.png"]
  },
  "shots": [
    {
      "shotId": "1.1",
      "durationSec": 3,
      "narrativeGoal": "建立场景与情绪",
      "subjectAnchors": ["@角色名@char_id"],
      "scene": "scene_id",
      "rigAndPose": "姿势描述",
      "camera": "景别+运镜+焦段",
      "lighting": "光线描述",
      "actionChain": "连续动作",
      "composition": "构图",
      "dramaticBeat": "情绪节拍",
      "continuityLocks": ["连续性锁点"],
      "dialogue": "对白（原文保留）",
      "sound": "音效/环境音",
      "emotion": "情绪",
      "negativeConstraints": "反向约束",
      "prompt": "完整图像生成提示词"
    }
  ]
}
```

字段约束：
- `subjectAnchors` 必须使用 `@角色名@char_id` 双锚格式（角色名用于人读，char_id 用于工具链绑定）
- `referencedAssets` 中的资产 id 必须与 Phase 3 角色/场景卡 `character_id`/`scene_id` 一致
- 跨镜头复用角色前，`referencedAssets.characterSheets` 必须已含该角色三视图之一
