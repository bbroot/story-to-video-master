---
name: story-to-video-master
slug: story-to-video-master
displayName: story-to-video-master 小说→分镜/短剧改编
version: 2.5.0
description: >
  端到端将小说/书籍转化为可执行的分镜 JSON、视频组提示词、完整视频作品的超级 SKILL。
  ★ 通用书籍文件夹理解器:能读取任意用户的书籍文件夹,自动理解所有文件的关系
  (正文/大纲/设定/角色卡/分镜草稿/图片参考/音频/视频),无需固定结构也能改编。
  ★ 深度适配 novel-master 小说创作 SKILL(含 v2 分布式架构),直接读取其结构化输出
  (角色声线卡/偏差包、分卷大纲、整卷章节正文、伏笔台账、冲突记录、NCG、Plot Bus、文风日志),
  实现从小说创作到视觉化改编的无缝双向闭环。
  ★ 适配即梦(Dreamina/Seedance 2.0, 官方CLI)、LibTV(liblib.tv, 官方OpenClaw Skill包+agent-im OpenAPI)、
  RunningHub(标准 OpenAPI+ComfyUI) 三个**可程序化自动调用**平台;
  并为小云雀(火山引擎企业API)、随变 APP(抖音Seedance2.0, 仅手机App)、Tapnow(Web画布, 仅手动)
  三个**仅手动/部分API**平台产出"可直接粘贴"的分镜内容。
  覆盖:故事分析→钩子设计→分集规划→角色/场景资产锁定(三视图前置+冻结闸门)→分镜表→T2I→I2V→ffmpeg。
tags: [storyboard, video-generation, screenplay, filmmaking, short-drama, hook-design, novel-master-adapter, plain-novel-mode, book-folder-understander, jimeng-dreamina, libtv, runninghub, multi-platform, character-locking, consistency-gate]
related_skills: [novel-master, storyboard-sketch-narrative, novel-to-storyboard, storyboard-converter, ark-novel-to-tuiwen, novel-to-video, text-storyboard, character-design, jimeng-skill, dreamina-cli, libtv-skill, runninghub-openapi]related_skills: [novel-master, storyboard-sketch-narrative, novel-to-storyboard, storyboard-converter, ark-novel-to-tuiwen, novel-to-video, text-storyboard, character-design, jimeng-skill, dreamina-cli]
---

# Story to Video Master（双模式：novel-master 深度适配 + 普通小说）

融合**业界已验证的核心方法论 + 真实开源同类 SKILL**，同时完美适配 **novel-master**
小说创作 SKILL，并支持**任意普通小说文本**（无项目结构也可改编）。

> **深度借鉴声明（真实下载并研读的同类 SKILL，非虚构套壳）：**
> 本 SKILL 从 SkillHub 真实下载并吸收了以下开源同类技能的可验证方法论：
> 1. **storyboard-sketch-narrative v1.0.1**（AI 短剧导演助手）——借鉴其「角色圣经」机制
>    （跨镜头持续维护、扫描自动注册、更新即确认）与「先导演思维→摄影思维→分镜→提示词」的 7 步导演模式。
> 2. **novel-to-storyboard v1.0.0**（小说转分镜）——借鉴其「角色/场景特征卡自动提取」
>    （`scripts/parse_novel.py` 的实体解析思路）。
> 3. **storyboard-converter v1.0.0**（影视分镜转换器）——借鉴其 7 字段分镜表
>    （镜头号/景别/运镜/画面/旁白/BGM/时长）+ 风格预设库（景别分布/运镜偏好/色调/BGM 曲线）。
> 4. **ark-novel-to-tuiwen v5.0.0**（小说改推文）——借鉴其「粘贴即改」的普通小说友好入口、
>    输入校验（太短/非小说/分章限制）与抖音合规红线（血腥/色情/诱导关注/迷信/恐怖/负面价值观）。
> 5. **好莱坞分镜语法体系 + Dan Wells 七点结构法 + 钩子半结果传播链 + T2I→I2V→ffmpeg 管线 +
>    诊断反馈循环质控**（公开编剧/导演/AIGC 工程实践）。
> 6. **chunpu/agent-skills 套件**（GitHub 真实开源，已克隆研读）——本 SKILL 的多平台与工程化主力借鉴来源：
>    - **novel-to-video**（小说→视频自然语言工作流）：借鉴其「断点续做」逻辑（扫描文件夹判断进度从断点续跑）、
>      项目目录结构约定（`角色/` `场景/` `道具/` `单集制作/EPXXX/` + `*.prompt.txt` 落盘）、画风/比例先确认流程。
>    - **text-storyboard**（文字分镜翻译层）：借鉴其「15 秒 clip 制」「用物理动作外化情绪（禁止抽象词）」
>      「镜头运动明确方向」「色温/光向/强度具体」「基础信息四要素（人物/场景/时长/概述）」——强化 Phase 1/4 文字分镜质量。
>    - **character-design**（16:9 横版三视图带面部特写）：借鉴其角色三视图提示词结构（左半面部特写+
>      右半正面/侧面/背面，纯白背景，反模板反套路，记忆点辨识度）——强化 Phase 3 角色三视图。
>    - **storyboard-to-seedance-prompt**（分镜→Seedance 提示词）：借鉴其「逐条强化不自作主张」「≥10 名词/≥5 动词/
>      ≥3 镜头术语最低信息线」「末尾固定追加『不要BGM，不要字幕』」「参考图绑定顺序标注」——强化 Phase 5 提示词输出。
>    - **generate-film-video-prompt**（影视提示词五层结构）：借鉴其「画风前置定调」「元素细节填充清单」
>      「对白台词四要素（说话人/方式/微表情/情绪）」「提示词温和化处理」——强化 Phase 5 台词与细节。
>    - **novel-reader**（智能长文本阅读器）：借鉴其「分段读取（每次 3000 字不做 for 循环）+ 资产实时抽取」
>      思想——本 SKILL 的「通用书籍文件夹理解器」呼应其理念，但改为文件夹关系理解而非强制单一结构。
> 7. **yuyou-dev/dreamina-cli-skill**（GitHub 真实开源）——即梦薄封装 wrapper 范式：
>    借鉴其「稳定 JSON 返回 {ok,command,cli_args,data}」「--dry-run 预览」「路径校验」「multimodal2video 参考图绑定
>    （最多 9 图 3 视频 3 音频）」——本 SKILL 的 `scripts/dreamina_gen.py` 据此实现即梦生图/生视频调用封装。
> **8. 六平台官方 API/文档逐一核实(2026-07-14 调研,非虚构)**:
  本 SKILL 的 Phase 5/6 多平台适配均基于对各平台**官方文档/官方 Skill 仓库/官方 CLI** 的真实抓取,不臆造:
  - **即梦 Dreamina**:官方 CLI 安装页 `https://jimeng.jianying.com/cli`(v1.4.11, 子命令 text2image/multimodal2video 等) + `yuyou-dev/dreamina-cli-skill`。
  - **LibTV(liblib.tv)**:官方 OpenClaw Skill 包 `https://github.com/libtv-labs/libtv-skills`(agent-im OpenAPI,声明支持 QClaw/OpenClaw)。
  - **RunningHub**:官方标准 API 页 `https://www.runninghub.cn/call-api/standard-api` + 契约 `HM-RunningHub/ComfyUI_RH_OpenAPI/developer-kit/rh-api-contract.md`。
  - **小云雀**:火山引擎"小云雀 Agent"文档树(企业 API,需下单);消费端 App 纯手动。
  - **随变 APP**:抖音官方协议列明旗下 AI 创作版本,默认模型 Seedance 2.0,仅手机 App。
  - **Tapnow**:官网 `https://app.tapnow.ai`(Web 画布,无官方 API;第三方 Tapnow-Studio-PP 为逆向仿制非官方)。
**novel-master 本身即本 SKILL 最核心的「同类技能」深度借鉴对象**——其 v2 的 Plot Bus / PpC /
> NCG / 伏笔台账 / 偏差包，是适配模式最宝贵的结构化数据源（见 `references/novel-master-interface.md`）。

---

## 一、核心适配原理

### 1.1 适配核心理念

小说与分镜是两套不同的表达系统--小说靠文字让读者脑补画面,分镜必须把内容转译为
**镜头、动作、景别、构图、节奏**。本 SKILL 不做"覆盖式改造",而是做**"接插件式适配"**:
在 novel-master 的输出之上,架设一套专门的改编转化层,零重复输入。

### 1.2 数据继承规则(⚠️ 对齐 novel-master 真实项目结构)

本 SKILL 适配的是你**实际使用的 v2 分目录项目**(以《觉醒》为基准样本):

```
~/.qclaw/workspace/novels/<书名>/
├── settings/
│   ├── world.md            # 世界观总览 → 用于场景氛围 / 设定合规
│   ├── geography.md         # 地理与势力 → 场景参考
│   ├── rules.md             # 世界运行规则 → 一致性校验
│   ├── 角色总览.md          # 全系列角色总表 → 角色索引
│   └── characters/          # 【关键】每个角色一个子目录(非单文件)
│       ├── <角色名>/
│       │   ├── voice.md      # 声线卡(身份/偏差/关系网)
│       │   ├── state.json    # v2 角色子进程状态机(location/emotion/relationships/version)
│       │   └── bias_pack.json# v2 认知偏差包(sensory_mapping/decision_bias/forbidden_generic)
├── outline/
│   ├── arc-outline.md        # 分卷大纲(若存)
│   ├── arc1-觉醒-outline.md  # 按卷命名的大纲(真实命名规律:arcN-<卷名>-outline.md)
│   └── ...
├── chapters/
│   ├── arc1-觉醒.md          # 【关键】整卷文件,非每章一个文件
│   ├── arc2-远荒.md
│   └── ...
├── tracker/
│   ├── foreshadowing.json    # 【关键】中文键名:伏笔列表[编号/埋入章节/内容/暗示层次/预期回收章节/回收状态/备注]
│   ├── conflicts.json        # 【关键】中文键名:冲突列表[type/who/chapter/desc]
│   ├── plot_bus.json         # v2 情节总线(chapter/facts[type/who/to/...])
│   ├── ncg.json              # v2 节点压缩图谱(nodes/super_nodes)
│   └── style-log.md          # 文风日志 → 视觉风格映射(含日漫风格增强标记)
└── state.json                # 当前写作状态(current_arc/current_chapter/total_words/...)
```

| novel-master 真实产出 | story-to-video-master 处理 | 适配方式 |
|----------------------|---------------------------|---------|
| 角色声线卡(`settings/characters/<名>/voice.md` + `state.json`) | → 角色卡 JSON + 三视图提示词 | **直接继承**,含 v2 实时状态(位置/情绪/关系) |
| 认知偏差包(`bias_pack.json`) | → 角色视觉特征锚点 | **继承**,把禁用通用词转译为视觉稳定性约束 |
| 分卷大纲(`outline/arcN-*.md`) | → 分集规划 + 钩子传播链 | **结构复用**,仅补镜头视角 |
| 整卷章节(`chapters/arcN-*.md`,含 `## 第N集`/`### 壹·一` 标记) | → 分镜内容源(按集正则切分) | **可视化转译**,从叙事节点转镜头节点 |
| 伏笔台账(`tracker/foreshadowing.json` 中文键) | → 钩子系统 + 悬念设计 | **直通使用**,伏笔即钩子前身 |
| 冲突记录(`tracker/conflicts.json` 中文键) | → 冲突强度评分 + 高潮定位 | **评分复用**,用于分镜节奏决策 |
| NCG(`tracker/ncg.json`) | → 情节密度与节拍参考 | **复用**,节点 tags 映射情绪曲线 |
| Plot Bus(`tracker/plot_bus.json`) | → 角色实时状态 / 位置连续性 | **复用**,地理连续性校验 |
| 文风日志(`tracker/style-log.md`) | → 视觉风格参数(含日漫风格层) | **风格映射**,文字风格→视觉风格 |

> **重要**:读取脚本(`scripts/load_novel.py`)已对**真实的中文键名 + 整卷章节文件 + 角色子目录**做适配。
> 若遇到英文键名或每章独立文件的项目,脚本会优雅降级到兼容模式。

### 1.3 与 novel-master 的双向闭环

```
novel-master(创作全流程)
   │  产出:角色声线卡 / 偏差包 / 分卷大纲 / 整卷章节 / 伏笔 / 冲突 / NCG / Plot Bus / 文风
   ↓ 自动读取项目数据(Phase 0)
story-to-video-master(适配版)
   │  Phase 0~7 完成改编
   ↓ 可选回写(Phase 7 末)
novel-master 项目目录
   ├─ output/storyboard/  → 分镜表(JSON + Markdown)
   ├─ output/assets/      → 角色三视图 / 场景参考图提示词
   └─ tracker/ 新增《改编状态追踪.md》 → 分集×钩子×伏笔回收映射
```

---

## 二、工作流(8 个 Phase + 0b 普通模式)

```
Phase 0 : 通用书籍文件夹理解器(scan_book_folder.py → book-manifest.json)
          ├─ 疑似 novel-master 项目? → 走「适配模式」读 v2 结构化数据
          └─ 任意书籍文件夹/粘贴文本? → 走「文件夹理解模式」自动分类与关系推断
   ↓ (双源汇合,统一为「书籍理解结果」)
Phase 0b: 普通小说模式(无结构文本:粘贴→实体提取→角色圣经)
  ↓ (三种输入在 Phase 1 汇合)
Phase 1: 故事分析与钩子设计(继承伏笔 + 半结果传播链)
  ↓
Phase 2: 分集规划与三段叙事(继承分卷大纲 + 钩子金字塔)
  ↓
Phase 3: 角色/场景/道具资产锁定(角色圣经 + 三视图规范)
  ↓
Phase 4: 分镜表生成(字数→镜头数 + 景别/运镜 + 7 字段表 + BGM)
  ↓
Phase 5: 视频组提示词 / 时间轴输出(@角色 绑定 + 多平台方言)
  ↓
Phase 6: 视频生成分流(自动调用 vs 手动投喂)
  ├─ 即梦 Dreamina     → scripts/dreamina_gen.py   (自动, 异步 submit_id 轮询)
  ├─ LibTV(liblib.tv)  → scripts/libtv_gen.py      (自动, agent-im 传话层 + 8s 轮询)
  ├─ RunningHub        → scripts/runninghub_gen.py (自动, 上传→endpoint→5s轮询重试)
  ├─ 小云雀            → 仅 Phase5 产出「剧本块文本」+ 手动投喂指引(企业端走火山引擎API)
  ├─ 随变 APP          → 仅 Phase5 产出「分镜头提示词序列」+ 手动投喂指引(仅手机App)
  └─ Tapnow            → 仅 Phase5 产出「画布搭建清单」+ 手动投喂指引(仅Web画布)
  ↓
Phase 7: 质量控制与全局校验 + 回写闭环
```

> **核心改进（v2.3.0）**：Phase 0 不再是「只认 novel-master 项目」，
> 而是 **通用书籍文件夹理解器**——读取任意用户的书籍文件夹，自动理解所有文件的关系
> （正文 / 大纲 / 设定 / 角色卡 / 分镜草稿 / 图片参考 / 音频 / 视频），
> 不依赖任何固定目录结构也能改编。novel-master 项目只是「被识别出的一种更优结构」。

---

## 三、详细实现

### Phase 0:通用书籍文件夹理解器(scan_book_folder.py → book-manifest.json)

**目标**:读取任意用户的书籍文件夹，**自动理解所有文件的关系**（不再只认 novel-master 产物）。
无论文件夹是 novel-master 标准项目、还是用户随手存放的 txt/md/epub + 图片 + 分镜草稿，
都能自动分类、推断每个文件的角色、建立文件关系图。

**输入**:书籍文件夹路径(或单个文本文件)
**输出**:`output/phase0/book-manifest.json`(供后续 Phase 引用的统一「书籍理解结果」)

**核心逻辑**:
1. **统一扫描入口**(调用 `scripts/scan_book_folder.py`):
   ```bash
   python3 scripts/scan_book_folder.py <书籍文件夹> --json > output/phase0/book-manifest.json
   ```
   三层信号推断文件角色：扩展名 → 文件名关键词 → 内容指纹（读前 2KB）。
2. **自动分类**:`novel_body`(正文) / `outline`(大纲) / `character`(角色卡) / `setting_world`(世界观) /
   `geography`(地理) / `foreshadow`(伏笔) / `conflict`(冲突) / `storyboard`(分镜草稿) /
   `plot_bus`(情节总线) / `ncg`(因果) / `style_log`(文风) / 图片参考 / 音频 / 视频 / 其他。
3. **关系推断**:自动建立「正文-被大纲规划」「设定-供正文改编」「分镜-衍生自」等文件关系边。
4. **结构判别**:`has_novel_master_signature` 为真 → 走「适配模式」(用 `scripts/load_novel.py` 读 v2 结构化数据);
   否则 → 走「文件夹理解模式」(直接消费分类结果,从不强制结构中提取可用资产)。
5. **v2 模式检测**:若检测到 `tracker/plot_bus.json` + `characters/*/state.json` → 启用 v2 适配。

> 关键设计：**不污染用户书籍文件夹**。所有产物(manifest/json/md)一律写到本 SKILL 的 `output/` 工作区，
> 原书籍文件夹只读不写（除非用户显式要求回写）。

**启动协议**(对用户可见):
```markdown
## 启动协议
### Step 1:检测输入来源(三选一,自动判定)
- 【适配模式】✅ 识别为 novel-master 项目:《书名》(v2 分布式模式) → 读取其结构化产出
- 【文件夹理解模式】✅ 识别为通用书籍文件夹:{N} 个文件,自动归类为正文/大纲/角色卡/图片参考…
  (无需任何固定结构,自动理解文件关系,见 book-manifest.json)
- 【普通模式】⚠️ 未提供文件夹 → 请直接粘贴小说文本(粘贴即改,支持 .txt/.md)

### Step 2:书籍理解结果(适配模式显示 v2 数据;文件夹模式显示分类统计;普通模式显示 parse_plain_text.py 校验)
- 文件总数:{N}
- 角色卡:{N} 个  | 大纲:{卷数} 卷 | 正文:{集数} 段 | 伏笔:{N} 条 | 冲突:{N} 条
- 图片参考:{N} 张(角色图/场景图/道具图,可用于资产一致性)
- 已推断文件关系:{N} 条

### Step 3:确认适配目标
- A 短剧分镜表(每集 1-2 分钟,共 20-30 集)
- B 电影分镜脚本(120 分钟标准)
- C 漫剧分镜(动态漫画)
- D 视频组提示词(AI 视频平台用,可粘贴即梦/Seedance/可灵/Runway)

### Step 4:确认基础参数
- 视觉风格:电影写实 / 日系动漫 / 2.5D / 短视频推文 / 情感叙事(默认:继承 style-log 或电影写实)
- 剧本风格:标准叙事 / 爽文漫剧(默认:标准叙事)
- 目标集数:预计多少集
- 每集时长:1 / 2 / 3 分钟(默认:1-2 分钟)
- 生成平台(Phase 6 用):
  · 自动调用:即梦 Dreamina(默认) / LibTV(liblib.tv) / RunningHub
  · 手动投喂:小云雀(App一键成片) / 随变 APP(手机对话框) / Tapnow(Web画布)
  (详见 references/platform-adapters.md 六平台对照与适配深度)
- 执行模式:🚀全程 / 📋分步 / 🎯单阶段
```

> **普通模式输入校验**(借鉴 ark-novel-to-tuiwen + novel-to-storyboard):
> 调用 `scripts/parse_plain_text.py` 做预处理。`<200字` → 提示"内容太短,至少一章";
> 纯对话/纯描写/流水账 → 照常生成但标注"⚠️ 高光点较少";超 20000 字 → 截断并建议分章;
> 非小说文本 → 拒绝并说明。详见 `references/character-bible.md` + `references/style-presets.md` 的合规红线。

---

### Phase 0b:普通小说模式(无 novel-master 项目时)

**目标**:当用户直接粘贴小说文本(无项目结构)时,从零建立分镜所需的全部资产。

**输入**:用户粘贴的小说文本 / 本地 `.txt` 文件
**输出**:`output/phase0b/extracted-cards.json`(角色/场景/道具特征卡 + 角色圣经草稿)

**核心逻辑**:
1. **输入校验**:`python3 scripts/parse_plain_text.py <file>`(见上)。
2. **实体提取**:
   - 角色:称谓/引号前主语出现 ≥2 次 → 提取姓名 + 首次外貌描写 + 推断音色(`character-bible.md`)
   - 场景:带空间/环境描写的名词短语 → 场景卡
   - 道具:被动作反复作用的物体 → 道具卡
3. **建立角色圣经**:按 `references/character-bible.md` 的「普通模式特征卡」注册,触发「更新即确认」。
4. **分集/切段**:按 ~3000 字/集 估算,或按用户指定的章节分隔。
5. **风格预设**:默认电影写实;若检测爽点密度高 → 提示可切短视频推文预设(`style-presets.md`)。

> 普通模式与适配模式在 Phase 1 之后完全合并:钩子设计、分镜表、提示词、生成管线一致,
> 仅 Phase 0/0b 的数据来源不同(一个读项目,一个读粘贴文本)。

---

### Phase 1:故事分析与钩子设计

**输入**:`tracker/foreshadowing.json`、`tracker/conflicts.json`、`outline/*`
**输出**:`output/phase1/hook-analysis.md`

**1.1 伏笔 → 钩子映射**(继承 novel-master 伏笔系统 + 钩子科学)

| 伏笔类型(暗示层次) | 钩子类型 | 说明 |
|--------------------|---------|------|
| 轻伏笔(暗示 1 次) | 信息差钩子(INFO) | 轻描淡写,回收时揭示意义 |
| 中伏笔(暗示 2-3 次) | 真相钩子(TRUTH)/ 关系钩子(REL) | 层层铺垫,回收时引爆 |
| 重伏笔(暗示 3 次+) | 反转钩子(TWIST)/ 命运钩子(FATE) | 认知颠覆 / 重大选择 |

**六组原始心理驱力**(钩子的底层神经回路,作为 intensity 依据):
`SCARCITY`(时间稀缺/倒计时) · `TERRITORY`(专属身份被侵犯) · `HUNT`(追逐快感) ·
`TRIBAL`(怕被群体排除) · `CONTROL`(信息不对称/真相揭示) · `LOSS`(即将失去/沉没成本)
→ 单驱力可靠,双驱力更凶,三驱力叠加是"核弹"。每集按内容决定叠加层数。

**1.2 钩子传播链(半结果引擎)**
每集结尾必须是「半结果」--只解答一部分,保留更大悬念。
```
集1: 钩子A → 半结果A + 新钩子B
集2: 钩子B(承接A) → 半结果B + 新钩子C
...
```
五种半结果模式:答一半留一半 / 假答案 / 代价答案 / 视角切换 / 时间锁。

**1.3 钩子强度曲线(钩子金字塔)**
```
全书大悬念(1-2,贯穿,大结局揭晓)
   └─ 卷级悬念(每卷 1-2,卷末解决或延续)
        └─ 批次钩子(每批次 1,推动)
             └─ 章节钩子(每章结尾,让人看下一章)
```
规则:强/弱钩子交替;每 3-5 集一个强钩子集;季终集最强收尾。

**1.4 钩子道德边界(三条红线,自动对照)**
- 真实性:时限/数量限制在故事世界内是否真实成立?
- 透明性:规则清晰不暗改,"确定性承诺"是否兑现?
- 可逆性:角色关键选择是否保留回头空间?

**强制输出格式**(见 `references/hook-design.md`):

```markdown
# 钩子分析报告(基于 novel-master 数据)
## 伏笔→钩子映射表
| 伏笔编号 | 原内容 | 暗示层次 | 钩子类型 | 强度 | 建议使用集数 |
|----------|--------|---------|---------|------|------------|
| fp-002a | 墙角布包=第一块铁片初次暗示 | 轻 | 信息差钩子 | 3/5 | 第1集开场 |
| fp-002d | 两块是钥匙,找第三块 | 重 | 命运钩子 | 4/5 | 第3集中段 |

## 钩子传播链
第1集: fp-002a(半结果:知道铁片存在但不知用途) → 引出 fp-002b
第2集: 铁片交付 → 新钩子 H1(信息差:铁片与枪管同材质)

## 驱力分布
- 主要驱力: CONTROL(对应"第三块铁片"核心悬念)
- 叠加策略: 第3集使用「CONTROL+LOSS」双驱力叠加

## 钩子道德边界检查
| 检查项 | 状态 |
|--------|------|
| 真实性 | ✅ |
| 透明性 | ✅ |
| 可逆性 | ✅ |
```

---

### Phase 2:分集规划与三段叙事

**输入**:`outline/arcN-*.md`、`chapters/arcN-*.md`(已切分集)、Phase 1 钩子分析
**输出**:`output/phase2/episodes-plan.md`

**2.1 分卷 → 分集映射**(以真实章节为单位)

| novel-master 单位 | 短剧分集 |
|------------------|---------|
| 一卷(3-5 万字) | 5-10 集(每集 1-2 分钟) |
| 一章 / 一集(3000-8000 字) | 1-3 集 |
| 一场(一个场景单元) | 1 集的一部分 |

> 真实项目 `chapters/arc1-觉醒.md` 内含 `## 第1集` `### 壹·一` 等标记,脚本按此切分为可改编单元。

**2.2 三段叙事结构(严格占比)**

| 段落 | 占比 | 功能 | 钩子要求 |
|------|------|------|---------|
| 起因 | ~25% | 引入本集钩子,承接上集半结果 | 开场钩子(0-15%) |
| 经过 | ~50% | 钩子发酵、冲突升级、信息释放 | 中段升级钩子(40-60%) |
| 结果 | ~25% | 钩子部分/完全解决 + 新钩子 | 结尾钩子(85-95%),半结果强制 |

**强制输出格式**:
```markdown
# 分集规划(基于 novel-master 真实章节)
## 第1集「{从章节标题继承}」
- **源章节**:arc1-觉醒.md「第1集《觉醒之夜》」+「壹·一」
- **核心事件**:{从章节正文/大纲提取}
- **视角人物**:{从单章单视角继承}
- **三段叙事结构**:
  - 起因(~25%): 引入钩子,承接上集半结果
  - 经过(~50%): 钩子发酵、冲突升级
  - 结果(~25%): 半结果收尾 + 新钩子
- **涉及角色**: {从角色列表继承,标注 v2 实时位置}
- **主要场景**: {从 geography/world 继承}
- **情绪走向**: {从 style-log / NCG 节点 tags 继承}
- **集尾钩子**: {基于伏笔映射 + 半结果类型}
- **预计镜头数**: {基于信息密度估算}
```

---

### Phase 3:角色 / 场景 / 道具资产锁定(角色圣经 + 三视图规范)

**输入**:适配模式=`settings/characters/<名>/{voice.md,state.json,bias_pack.json}`+`geography.md`+`rules.md`;普通模式=Phase 0b 提取的特征卡
**输出**:`output/assets/` 角色卡 JSON + 场景卡 JSON + 三视图提示词 + 角色圣经(`character-bible.md`)

> **角色圣经(借鉴 storyboard-sketch-narrative 的跨镜头持续维护机制)**:
> 不论何种模式,所有角色/场景/道具统一登记进「角色圣经」(见 `references/character-bible.md`)。
> 适配模式从 voice.md 初始化(音色直接继承 speech_style);普通模式从文本自动提取并触发「更新即确认」。
> 拍摄每个镜头前扫描剧本,新出现的实体自动注册,已登记实体复用不新增版本。

**3.1 角色卡继承与三视图补全**(源自专业分镜工作站的"角色前置规划"强制方法论)

> **核心规则**:所有跨镜头复用的角色,必须先创建角色卡节点(含三视图),再写镜头节点;
> 不得跳过此步直接写"假定已锁定"的镜头 prompt。

从 `voice.md` 取身份/关系;从 `state.json` 取实时位置/情绪/关系强度;从 `bias_pack.json`
取感官锚点/禁用通用词(转译为视觉稳定性约束)。

```json
{
  "name": "林渡",
  "source": "novel-master/settings/characters/林渡/voice.md",
  "character_id": "char_lindu",
  "roleCardId": "char_lindu_v1",
  "sourceBookId": "觉醒",
  "gender": "男",
  "identity": "灰岩堡年轻教官(南线10人队)",
  "personality": {
    "core_traits": "细心谨慎的分析派",
    "speech_style": "句尾带不确定升调,用反问代替肯定",
    "decision_bias": "分析优先,谨慎推进",
    "cognitive_bias": "把『谨慎』映射为反复核验细节"
  },
  "appearance": {
    "description": "年轻教官,眼神专注",
    "distinctive_features": ["分析时微蹙眉"]
  },
  "v2_state": {
    "location": "灰岩堡",
    "emotion_value": 0.0,
    "relationships": {"铁岭":"同盟0.6","周岩":"同盟0.5"}
  },
  "visual_stability_constraints": [
    "禁用『突然』类跳变;动作须有前因",
    "同一角色全程五官清晰稳定不变形"
  ],
  "three_view": {"front":"待生成","side":"待生成","back":"待生成","status":"pending"},
  "ai_prompt_template": "年轻男性教官,电影写实风格,高质量光影,{灰岩堡制服}",
  "relationship_delta": {"铁岭":"同盟+0.6","周岩":"同盟+0.5"}
}
```

**三视图提示词模板(借鉴 chunpu/character-design 的 16:9 横版三视图)**——
用于 Phase 6 生图时锁定角色跨镜头一致性:
```
16:9 横版构图,[画风要求,如:电影写实/3D国漫CG]。
左半边区域居中展示角色面部特写(强调记忆点与辨识度特征:眉宇/眼神/口鼻线条传递善恶与性格),
右半边区域整齐排布角色三张全身设定图(正面/侧面/背面),所有角度比例严格一致。
画面不得出现任何文字、水印;背景纯白干净。
[人物具体形象描述:基础信息(身高/地域/性别/体型/外表年龄/人生经历关键词)+
面部特征(脸型/五官/妆容/表情/发型/发色/头饰)+
全身穿搭(上衣/下装/鞋子/材质/配色,每件服饰承载角色经历)+
配饰(首饰/武器/背包,每件承载故事)+
气质神态(站姿坐姿让性格自然流露)]
```
> 反模板反套路:拒绝完美比例,保留有记忆点的"不完美"特征;避免标签化(高冷≠冰山脸)。

> 强制规则:后续镜头 prompt 使用 `@角色名` 或 `@角色名-状态` 语法,例如 `@林渡` 从训练场走出。
> 若同名角色存在多张卡,在镜头约束里给出可区分证据;若证据不足以唯一绑定 → 显式失败并指出缺哪张卡。

**3.3 角色锁定闸门(冻结,不可跳过)——核心质量门(详见 `references/character-locking.md`)**

novel→video 最大翻车点是**同角色跨镜头脸/身材/服饰漂移**;小说改视频角色多、集数长,漂移被指数放大。
本 skill 把“锁定角色”做成**不可绕过的强制闸门**:

1. **角色注册表** `output/assets/character-registry.json`:每个复用角色一条,含 `canonical_identity`(权威一句话外观)、
   `three_view`(front/side/back 三视图路径)、`seed`(跨镜头同人保险)、`expressions`(情绪变体)、`negative_constraints`、`locked` 标记。
2. **锁定充要条件**:三视图三文件齐全 + `canonical_identity` 非空 + 至少 1 条负数约束 → `locked=true`
   (由 `scripts/lock_character.py validate` 计算,不以人工标记为准)。
3. **生图前硬闸门**:任何含该角色的镜头,Phase 6 生图前必须 `python3 scripts/lock_character.py validate` 全绿;
   **未锁定角色禁止进入生图**(脚本返回 `ok=false` 并列出缺失资产),不得“先生成再说”。
4. **同人保证(三视图链式)**:绝不独立生成三张——先生成 front(固定 seed),side/back 以 front 为参考图衍生(image2image/多参考绑定),
   强制“基于这张脸衍生”,杜绝三视图不是同一人。
5. **情绪变体**:为高频情绪(neutral/angry/sad/tense/excited/hesitant)以 front 为参考图生成 `exp_<state>` 变体,
   供分镜 `@角色名-状态` 直接复用,避免每镜重新描述导致漂移。
6. **分镜 @标签校验**:`scripts/lock_character.py rebind` 扫描分镜 JSON,确保每个 `@角色名/@角色名-状态`
   都能解析到锁定参考图,未注册/未锁定/缺变体一律报错指出缺哪张卡。

> Phase 3 初始化后必须先 `write-prompt`(生成 `角色/<name>*.prompt.txt` 落盘,Phase 6 直接 cat 使用,不在 Phase 6 现编),
> 再 `validate` 闸门;Phase 6 生图严格按 `references/character-locking.md` 编排(三视图链式 + 状态变体)。

**3.2 场景卡继承**

```json
{
  "name": "旧街道黄昏",
  "source": "novel-master/settings/geography.md",
  "scene_id": "scene_old_street",
  "visualRefId": "scene_old_street_v1",
  "visualRefCategory": "scene",
  "type": "室外",
  "time_of_day": "黄昏",
  "atmosphere": "神秘",
  "lighting": "暖橙逆光",
  "color_palette": "深蓝紫暗调",
  "key_elements": ["路灯","石板路","老式店铺"],
  "reference_image": "待生成",
  "ai_scene_prompt": "旧街道黄昏,橙红夕阳,石板路,老式店铺,神秘氛围,电影级光影,8K"
}
```

> 强制规则:跨场景复用的场景/道具,必须先有视觉参考资产(`visualRefId/visualRefName/visualRefCategory`)。

---

### Phase 4:分镜表生成

**输入**:Phase 0-3 全部输出 + novel-master 章节正文
**输出**:同时输出 **JSON**(下游工具链)+ **Markdown 表格**(人类阅读)

**4.1 分镜数量判断**(先问四个问题:几个视觉重点?动作有无变化?情绪有无起伏?是否需景别切换强调?)

| 章节字数(真实切分后单集估算) | 镜头数 |
|------------------------------|--------|
| ≤1200 字 | 6-8 |
| 1201-2500 字 | 8-12 |
| >2500 字 | 12-16 |

**4.2 景别 / 运镜规范**(好莱坞分镜语法,详见 `references/storyboard-spec.md`)

景别:ELS 大远景 / LS 远景 / FS 全景 / MS 中景 / MCU 近景 / CU 特写 / ECU 大特写
运镜:固定 / 推 / 拉 / 摇 / 移·跟 / 手持 / 急推·急拉

**4.3 内心戏转译规则**(继承 novel-master 出版级"展示而非告知"标准)

| 心理状态 | 外化动作 | 外化场景 |
|---------|---------|---------|
| 愤怒 | 拍桌/摔杯/咬牙 | 暴雨独行 |
| 悲伤 | 低头沉默/手握拳 | 空房间独坐 |
| 紧张 | 手指反复敲击桌面 | 黑暗走廊 |
| 恐惧 | 瞳孔放大/后退/声颤 | 阴影逼近 |
| 兴奋 | 眼神发光/小动作 | 阳光洒入 |
| 犹豫 | 来回踱步/反复握拳松拳 | 十字路口 |

> **日漫风格层(来自 style-log 的"日漫风格增强"标记)**:若某集被标注括号体独白
> (`「齿轮缺齿」` / `(陆沉的内心独白)`)或慢镜头标记(`慢镜头·X视角`),
> 在分镜中专门设计"独白穿插镜"与"高光慢镜头",但不破坏冷峻骨架。

**4.4 分镜 JSON(storyboard-director/v1.1 兼容)**

```json
{
  "schemaVersion": "storyboard-director/v1.1",
  "chapter": "第1集",
  "sourceChapter": "arc1-觉醒.md「第1集《觉醒之夜》」",
  "globalStyle": "电影写实",
  "cast": ["char_luchen", "char_linmo"],
  "relationshipGraph": "陆沉(主角)→ 陆萤(妹妹)",
  "modelingSpec": {"材质风格":"真实质感","表面磨损":"中度","纹理精度":"8K"},
  "atmosphereSpec": {"整体氛围":"崖镇晨起的安稳中带隐忧","情绪基线":"平静"},
  "referencedAssets": {
    "characterSheets": ["assets/char_luchen_front.png"],
    "sceneSheets": ["assets/scene_yazhen_dawn.png"]
  },
  "shots": [
    {
      "shotId": "1.1",
      "durationSec": 3,
      "narrativeGoal": "建立场景与情绪",
      "subjectAnchors": ["@陆沉@char_luchen"],
      "scene": "scene_yazhen_dawn",
      "rigAndPose": "蹲在工坊案台前,拆弩臂",
      "camera": "全景→中景,缓推,50mm",
      "lighting": "晨光从窗左侧,低角度",
      "actionChain": "陆沉在工坊拆弩臂,街上传来磨坊与水车声",
      "composition": "前景:陆沉剪影;中景:工坊木架;背景:崖壁长影",
      "dramaticBeat": "平静→微澜",
      "continuityLocks": ["开场帧→角色位置"],
      "dialogue": "",
      "sound": "环境音:远处水车吱呀、磨坊声响",
      "emotion": "专注、隐忧",
      "negativeConstraints": "不要过度曝光、不要人物模糊、不要现代广告牌",
      "prompt": "清晨工坊,年轻男性蹲着拆弩臂,晨光逆光拉长影子,电影写实质感,8K,全景缓推"
    }
  ]
}
```

**4.5 分镜 Markdown 表格**(可读,借鉴 storyboard-converter 的 "镜头号/景别/运镜/画面/旁白/BGM/时长" 七字段)

> 兼容双轨:普通模式用「画面描述/旁白台词/BGM」三列(短视频友好);适配模式保留
> 「动作/情绪/钩子标记/源章节」四列(项目溯源)。下方为合并推荐列序。

| 镜号 | 时长 | 景别 | 运镜 | 画面描述 | 旁白/台词 | BGM建议 | 钩子标记 | 源章节 |
|------|------|------|------|----------|-----------|----------|---------|--------|
| 1.1 | 3s | 全景→中景 | 缓推 | 陆沉蹲工坊拆弩臂,晨光逆光拉长影子,专注微蹙眉 | （无） | 轻柔环境音垫底 | - | 第1集 |
| 1.2 | 2s | 中景 | 固定 | 陆萤推门进工坊,晨光勾出轮廓 | "哥,该报名了" | 同上+渐入人声 | E1-H1 | 第1集 |

> BGM 情绪曲线模板见 `references/style-presets.md`(开场轻柔→推进渐强→高潮明快→收束渐弱)。

---

### Phase 5:视频组提示词 / 时间轴输出

**输入**:Phase 4 分镜 JSON
**输出**:`output/phase5/video-prompts.md`(可直接粘贴即梦/Seedance/可灵/Runway/海螺/Sora)

> **文字分镜强化(借鉴 chunpu/text-storyboard + generate-film-video-prompt)**:
> - **15 秒 clip 制**:每段文字分镜对应一个 15 秒视频 clip,动作/镜头/情节严格控制在 15 秒内。
> - **物理动作外化**:禁止抽象词(悲伤/紧张/高兴),改用动作+表情+光影表现(见 Phase 4.3 转译表)。
> - **镜头运动明确方向**:推/拉/摇/移/跟 有起点和终点(如「中景→近景上摇」)。
> - **色温/光向/强度具体**:如「5600K 日光从右侧打来,强度中等」「3200K 暖光左侧 45°主光」。
> - **画风前置定调**:提示词最开头写画风(3D国漫CG/真人电影感/2D漫画),再填元素细节。
> - **对白四要素**(借鉴 generate-film-video-prompt):每句对白必含【说话人+说话方式+微表情/肢体+情绪】。

**5.1 视频组提示词(@角色 绑定格式,统一内部标准)**

```markdown
## 视频组列表
### Clip 1 - 《觉醒之夜·开场》(15秒)
**画面风格**: 电影写实,自然光照,极致细节
**场景**: 工坊清晨 @scene_yazhen_dawn
**角色**: 陆沉 @char_luchen
**运镜+画面**(0-15s 时序,快节奏切分):
- [0-1s] 全景,工坊晨光,陆沉@char_luchen 剪影蹲坐拆弩臂,5600K 侧光勾边
- [1-3s] 中景缓推,陆沉手指摩挲弩臂纹理,眉头微蹙(专注+隐忧外化)
- [3-8s] 中景固定,陆萤@char_luying 推门,晨光勾轮廓,发丝镀金边
- [8-12s] 近景,陆沉抬头,瞳孔微动,目光追向妹妹
- [12-15s] 中景反打,陆萤@char_luying(轻声,指尖搭门框):"哥,觉醒测试该报名了。" 余音回荡
**台词(原文保留)**: 陆萤@char_luying:"哥,觉醒测试该报名了。"
**其他需求**: 面部五官清晰稳定不变形,同一角色全程外貌一致,动作连续不跳帧,无字幕无文字
```

**5.2 多平台方言 transpile(见 `references/platform-adapters.md`,六平台已逐一官方核实)**
Phase 5 内部用统一分镜单元,按目标平台 transpile 为平台提示词。三档分流:

**A. 可自动调用(Phase 6 走脚本)**:
- **即梦 Seedance2.0**(默认):画风前置 + 元素细节清单 + 时序 `0-1.5s:xxx` + 末尾固定 `不要BGM,不要字幕`
  + 参考图绑定(提示词内用 `图1/图2` 引用,顺序对应 `--image`)。
- **LibTV**:**不做方言美化**——原样输出原始描述 + 参考图 OSS URL,交给其后端 Agent 拆解(传话层原则)。
- **RunningHub**:按 `{endpoint}` 提交,Seedance2.0 系列用 `asset_ids` 绑定参考素材。

**B. 仅手动投喂(Phase 5 产出可直接粘贴的内容,不调脚本)**:
- **小云雀**:输出「剧本块文本」(按集组织 + 参考图说明 + 风格/时长),用户粘贴到 App 一键成片。
- **随变 APP**:输出「分镜头提示词序列」(每条一个镜头,标注【创作模式】/@IP【合拍模式】,贴合其"一次一视频"特性)。
- **Tapnow**:输出「画布搭建清单」(节点-镜头-场景 + 风格参照/IP一致性建议),用户录入 Web 画布。

**C. 其他(从 platform-adapters 旧版仍可输出英文提示词)**:
- **Runway**:英文术语优先,结构 `[camera movement]: [scene]. [details]`。
- **海螺 / Sora**:按平台约定格式输出(本 SKILL 输出统一提示词,由用户粘贴或接入)。

**5.3 时间轴(15秒,情绪节拍)**
- 0-3s:建立场景与情绪--工坊清晨,陆沉独处
- 3-9s:推进动作--陆萤登场,对话启动
- 9-12s:高潮/关键揭示--陆沉抬眼(伏笔呼应:造枪动机)
- 12-15s:落版/余韵/悬念--台词落下,钩子 E1-H1 收束

---

### Phase 6:视频生成分流(可选,三自动 + 三手动)

借鉴 T2I→I2V→ffmpeg 通用管线 + chunpu/novel-to-video 工程化约定(断点续做 + `单集制作/EPXXX/` + `*.prompt.txt` 落盘):

**6.0 项目产物目录约定(便于断点续做)**
```
<书籍名>/                      # 在 output/ 工作区下,不污染原书籍文件夹
├── 角色/   (char_X.png + char_X.prompt.txt)
├── 场景/   (scene_X.png + scene_X.prompt.txt)
├── 道具/   (prop_X.png)
└── 单集制作/
    ├── EP001/
    │   ├── 文字分镜.txt
    │   ├── 视频_Clip001.prompt.txt
    │   └── 视频_Clip001.mp4
    └── EP002/ ...
```
> **断点续做**:项目文件夹已存在时,先扫描内容判断进度,从断点处继续(不重做已完成集)。

**6.1 自动调用平台(需用户在启动协议 Step 4 显式选定并确认)**

① 即梦 Dreamina(默认,脚本 `scripts/dreamina_gen.py`):
```bash
# 生图(严格遵循 references/character-locking.md 锁定闸门:先 3.3 write-prompt 落盘 + validate 全绿)
# (1) 三视图链式:先 front(固定 seed),再 side/back 以 front 为参考图衍生 → 回填 registry.three_view
python3 scripts/dreamina_gen.py text2image --prompt "$(cat 角色/林渡.prompt.txt)" --ratio 16:9 --seed 12345 --dry-run
python3 scripts/dreamina_gen.py text2image --prompt "$(cat 角色/林渡.prompt.txt)" --ratio 16:9 --seed 12345       # 生成 front
python3 scripts/dreamina_gen.py text2image --image 角色/林渡_front.png \
  --prompt "侧面与背面三视图,…(cat 角色/林渡.prompt.txt)" --ratio 16:9   # side/back 以 front 衍生
# (2) 情绪变体(以 front 为参考图衍生)
python3 scripts/dreamina_gen.py text2image --image 角色/林渡_front.png \
  --prompt "$(cat 角色/林渡_exp_angry.prompt.txt)" --ratio 16:9
# (3) 封锁闸门校验:未锁定角色禁止进入下一步
python3 scripts/lock_character.py validate --book <书籍名>
# 多参考生视频(角色图+场景图绑定,提示词内 图1/图2 引用)
python3 scripts/dreamina_gen.py multimodal2video \
  --image 角色/林渡.png --image 场景/工坊.png \
  --prompt "林渡参考图1,工坊场景参考图2。$(cat 单集制作/EP001/视频_Clip001.prompt.txt)" \
  --ratio 16:9 --duration 15
python3 scripts/dreamina_gen.py query --submit-id <id>   # 每分钟轮询
```
> 即梦并发硬限制:**最多 3 个排队/生成中任务**;异步提交后轮询,完成用 curl 下载到语义化文件名。

② LibTV(liblib.tv,脚本 `scripts/libtv_gen.py`,传话层):
```bash
# 1) 上传本地参考图拿 OSS URL(env: LIBTV_ACCESS_KEY)
export LIBTV_ACCESS_KEY=<从 LibTV 网页「LibTV Skills → 复制 access key」获取>
python3 scripts/libtv_gen.py upload --file 角色/林渡.png
# 2) 创建会话并原样发描述(不润色/不拆镜,交给其后端 Agent)
python3 scripts/libtv_gen.py session --message "把这段小说改成分镜并生成视频: …" --image-url "https://libtv-res…/林渡.png"
# 3) 8 秒轮询查询结果(含结果URL + projectUrl)
python3 scripts/libtv_gen.py query --session-id <id> --wait
# 4) 批量下载结果到本地
python3 scripts/libtv_gen.py download --session-id <id> --output-dir output/libtv
```
> LibTV 已声明支持 OpenClaw/QClaw 等 Personal Agent;Agent 侧只做传话。超时(3min 无结果)提示去 projectUrl 画布查看。

③ RunningHub(脚本 `scripts/runninghub_gen.py`,标准 OpenAPI):
```bash
# 1) 上传本地媒体(env: RH_API_KEY)
export RH_API_KEY=<从 runninghub.cn/enterprise-api/sharedApi 获取>
python3 scripts/runninghub_gen.py upload --file 角色/林渡.png
# 2) 提交任务(Seedance2.0 系列用 --asset-ids 绑定参考素材;--wait 自动轮询)
python3 scripts/runninghub_gen.py generate \
  --endpoint seedance2.0/文生视频 --prompt "$(cat 单集制作/EP001/视频_Clip001.prompt.txt)" \
  --ratio 16:9 --duration 8 --asset-ids "<upload返回的download_url>" --wait
# 3) 或单独轮询
python3 scripts/runninghub_gen.py query --task-id <id> --wait
```
> RunningHub 消耗账户余额;提交/上传带 3 次指数退避重试(仅重试网络/429/5xx);轮询 5s,超时 30min 返回 taskId 供 call-record 自查。

**6.2 手动投喂平台(Phase 5 已产出可直接粘贴的内容,本 Phase 不再调脚本)**
- **小云雀**:在 App 内新建项目 → 粘贴 Phase5「剧本块」→ 上传对应参考图 → 选短剧 Agent 2.0(Seedance2.0 底座)一键成片(支持≤10万字剧本)。
- **随变 APP**:打开手机 App → 逐条复制 Phase5「分镜头提示词序列」到对话框(创作模式用自己形象/合拍模式 @某IP);注意"一次最好只生成一个视频"。
- **Tapnow**:登录 Web 画布 → 按 Phase5「画布搭建清单」逐节点录入(场景/镜头角度/动作/时长/风格参照/IP一致性参考图)。

**6.3 ffmpeg 合并 + 配音**(可选,本地,仅对自动调用产出的短视频 clip)
```bash
ffmpeg -f concat -safe 0 -i clips.txt -c copy output.mp4   # 合并各 Clip
```

> ⚠️ Phase 6 默认**不自动执行任何付费生成**,除非用户在启动协议 Step 4 明确选择生成平台并确认。
> 三个自动脚本缺失 CLI/Key 时一律优雅报错并给出安装方式(不崩溃)。手动平台仅产出文本,由用户自行投喂。

---

### Phase 7:质量控制与全局校验 + 回写闭环

**7.1 全局校验表**(融合诊断反馈循环)

| 校验项 | 标准 | 数据来源 |
|--------|------|---------|
| 时长偏差 | 每集 ±5 秒内 | 自检 |
| 钩子健康度 | 每集 ≥3 个钩子(开场+中段+结尾) | novel-master 伏笔 + 新钩子 |
| 驱力多样性 | ≥2 种驱力 | 自检 |
| 因果连贯性 | 钩子前后关联 | novel-master 伏笔回收计划 |
| 角色一致性 | 所有镜头角色卡已锁定 | novel-master 角色声线卡 + v2 state |
| 场景连续性 | 跨镜头场景锚点已锁定 | novel-master 世界观 + Plot Bus 位置 |
| 伏笔回收一致性 | 分镜中伏笔位置符合追踪计划 | novel-master foreshadowing.json |
| 镜头数合规 | 符合字数→镜头数规则 | 自检 |
| 源数据完整性 | novel-master 数据全部读取 | ✅/⚠️ 状态标记 |

**7.2 钩子链完整性**
- 层次数量:全书大悬念 1-2 / 卷级每卷 1-2 / 批次每批次 1 / 章节每章 1
- 连贯性:大悬念有定期"喂料";卷级合理推进;章节钩子都有承接;无"挖坑不填"
- 强度:无连续 3 章以上弱钩子;高潮前钩子足够强;卷末钩子最强

**7.3 七点结构法检查**(Dan Wells)

| 结构点 | 位置 | 内容要求 |
|--------|------|---------|
| Hook | 前 10-15% | 让读者/观众产生"然后呢" |
| Plot Turn 1 | ~15% | 给主角不能回头的原因 |
| Pinch 1 | ~25% | 反派亮一次拳 |
| Midpoint | 50% | 推翻主角和读者之前的认知 |
| Pinch 2 | ~75% | 把主角逼到墙角 |
| Plot Turn 2 | ~85% | 主角找到翻盘钥匙(非机械降神) |
| Resolution | 最后 10% | 回应物理层+情感层+意义层 |

**7.4 回写闭环(双向协作收口)**

生成完毕后,将结果回写 novel-master 项目目录:
```
<书名>/
├─ output/storyboard/   → 分镜表(storyboard-第N集.json + .md)
├─ output/assets/       → 角色三视图 / 场景参考图提示词(assets-*.json)
└─ tracker/《改编状态追踪.md》 → 分集×钩子×伏笔回收映射表
```
《改编状态追踪.md》模板见 `references/novel-master-interface.md`。

---

## 四、与 novel-master 的双向协作流程

```
┌──────────────────────────────────────────────────────────────┐
│                    novel-master                               │
│  产出:角色声线卡+偏差包、分卷大纲、整卷章节、伏笔、冲突、NCG、Plot Bus、文风 │
└──────────────────────────┬───────────────────────────────────┘
                           ↓(Phase 0 自动读取,零重复输入)
┌──────────────────────────────────────────────────────────────┐
│              story-to-video-master(适配版)                  │
│  Phase 0: 读 novel-master(真实 v2 分目录)                   │
│    ├─ settings/characters/<名>/{voice,state,bias} → 角色卡    │
│    ├─ outline/arcN-*.md → 分集规划                           │
│    ├─ chapters/arcN-*.md(按集切分)→ 分镜内容源             │
│    ├─ tracker/foreshadowing.json → 钩子系统                 │
│    ├─ tracker/conflicts.json → 高潮定位                     │
│    ├─ tracker/plot_bus.json + ncg.json → 连续性/密度         │
│    └─ tracker/style-log.md → 视觉风格                       │
│  Phase 1-7: 钩子→分集→资产→分镜→视频→质控→回写              │
└──────────────────────────────────────────────────────────────┘
                           ↓(Phase 7 回写)
┌──────────────────────────────────────────────────────────────┐
│  回写至 novel-master 项目:output/storyboard/ · output/assets/ │
│  · tracker/《改编状态追踪.md》                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 五、核心适配优势总结

| 维度 | 通用改编 SKILL | novel-master 适配版 |
|------|--------------|---------------------|
| 角色信息 | 需手动提供或从零提取 | 直接继承 voice.md+state.json+bias_pack.json |
| 情节结构 | 需 AI 分析全本 | 直接用分卷大纲 + NCG |
| 伏笔系统 | 需从头设计 | 继承 foreshadowing.json(中文键兼容) |
| 冲突定位 | 需重新识别 | 直接用 conflicts.json |
| 风格一致性 | 需额外分析文风 | 继承 style-log.md(含日漫风格层) |
| 项目切换 | 每次手动提供文本 | 只需指定项目路径,自动读取真实结构 |
| 双向闭环 | 单向输出 | 分镜结果可回写写作进度 |
| 感知写作阶段 | 无 | 读 state.json,感知当前卷/章 |
| 钩子系统 | 需独立设计 | 伏笔继承 + 半结果传播链 |
| 输出规范 | 不统一 | storyboard-director/v1.1 JSON + Markdown 双格式 |

---

## 六、参考文档速查

| 文件 | 何时使用 |
|------|---------|
| `references/hook-design.md` | Phase 1 钩子设计与类型选择 |
| `references/storyboard-spec.md` | Phase 4 景别/运镜/分镜 JSON 规范 |
| `references/seven-point-structure.md` | Phase 7 七点结构法质控 |
| `references/continuity-methods.md` | Phase 3/4 连续性收口方法 |
| `references/novel-master-interface.md` | Phase 0 读取接口 + Phase 7 回写规范 |

## 七、辅助脚本

| 脚本 | 用途 |
|------|------|
| `scripts/load_novel.py` | Phase 0 读取 novel-master 真实 v2 项目,输出 `data-summary.json` |
| `scripts/scan_book_folder.py` | Phase 0 通用书籍文件夹理解器,自动分类与关系推断,输出 `book-manifest.json` |
| `scripts/parse_plain_text.py` | Phase 0b 普通小说模式,粘贴文本 → 实体提取与校验 |
| `scripts/build_storyboard.py` | Phase 4 将数据集 + 钩子规划渲染为 storyboard JSON + Markdown |
| `scripts/dreamina_gen.py` | Phase 6 即梦 Dreamina 薄封装(CLI,异步 submit_id 轮询,参考图绑定) |
| `scripts/libtv_gen.py` | Phase 6 LibTV 传话层封装(agent-im OpenAPI,Bearer Key,8s 轮询,下载) |
| `scripts/runninghub_gen.py` | Phase 6 RunningHub 标准 OpenAPI 封装(上传→endpoint→5s 轮询重试) |
| `scripts/lock_character.py` | **Phase 3.3 角色锁定闸门**:write-prompt(落盘三视图/变体提示词)+ validate(冻结校验)+ rebind(分镜@标签解析校验) |

> 运行前需 `python3` 可用。自动生成脚本默认不主动执行付费调用;缺失 CLI/Key 时优雅报错并给出安装方式。
> 回写由 Phase 7 显式确认后执行,绝不修改源项目(除显式要求)。

---

## 八、安装与使用

**安装**(推荐软链到 skills 目录,与 novel-master 并列):
```bash
ln -s ~/Documents/龙虾/story-to-video-master ~/.qclaw/skills/story-to-video-master
# 前置:novel-master 已安装
ls -la ~/.qclaw/skills/novel-master/
```

**使用方式**:
```text
# 方式1:适配模式(推荐)- 自动读取 novel-master 项目
用 $story-to-video-master,把我的小说《觉醒》改编为 3 集短剧。
项目在 ~/.qclaw/workspace/novels/觉醒/

# 方式1b:通用书籍文件夹理解模式(新增)- 任意书籍文件夹,无需固定结构
用 $story-to-video-master,改编 ~/Documents/我的书稿/ 这个文件夹里的所有内容。
# → Phase 0 自动理解文件关系(正文/大纲/角色卡/分镜草稿/图片参考…),无需手动整理

# 方式2:独立模式 - 用户直接提供文本
用 $story-to-video-master,把下面这段小说改编为分镜:{粘贴文本}

# 方式3:仅做分镜(Phase 0-4),不生成视频
用 $story-to-video-master,仅做分镜,不生成视频

# 方式4:仅钩子分析(Phase 1)
用 $story-to-video-master,分析这个故事的核心钩子和传播链
```

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v2.5.0 | 2026-07-14 | **①角色锁定闸门(冻结,不可跳过)**——新增 `references/character-locking.md` + `scripts/lock_character.py`(write-prompt 落盘三视图/变体提示词 + validate 冻结校验 + rebind 分镜@标签解析校验)。把"锁定角色"做成不可绕过的质量门:角色注册表唯一真相源、三视图三文件齐全才 locked、未锁定禁止生图、三视图链式同人(front 固定 seed→side/back 以 front 衍生)、情绪变体供 @角色名-状态 复用。 **②角色生图规范化**——Phase 3.3 定义同人保证与状态变体生成流程,Phase 6 生图改为严格按锁定闸门编排(先 write-prompt+validate 全绿,再链式生三视图+情绪变体)。 | **①六平台官方文档逐一核实适配**(即梦/小云雀/随变APP/Tapnow/LibTV/RunningHub):
重写 `references/platform-adapters.md` 为 6 平台全量对照(可调用性/官方来源URL/端点/鉴权/限制)。
**②新增两个自动调用脚本**:`scripts/libtv_gen.py`(LibTV agent-im OpenAPI 传话层,Bearer Key+8s轮询+下载),
`scripts/runninghub_gen.py`(RunningHub 标准 OpenAPI,上传→endpoint→5s轮询带重试)。
**③Phase 6 分流逻辑**:即梦/LibTV/RunningHub 走脚本自动调用;小云雀/随变APP/Tapnow 仅产出"可粘贴"文本(剧本块/分镜头提示词序列/画布搭建清单)由用户手动投喂。
**④Phase 5 transpile 三档分流**:自动平台方言 + 手动平台专用产出格式。 |
| v2.3.0 | 2026-07-14 | **①通用书籍文件夹理解器**:新增 `scan_book_folder.py`,Phase 0 升级为读取任意书籍文件夹、自动理解所有文件关系(正文/大纲/角色卡/分镜草稿/图片参考/音频/视频),无需固定结构也能改编;novel-master 仅作为「被识别出的更优结构」之一。 **②多平台视频生成适配**:新增 `references/platform-adapters.md`(即梦 Seedance2.0/可灵/Runway/海螺/Sora 对照)+ `scripts/dreamina_gen.py`(即梦薄封装,稳定 JSON/--dry-run/参考图绑定);Phase 6 接入即梦工程化 + 断点续做 + `单集制作/EPXXX/` 目录约定。 **③吸收 chunpu/agent-skills 套件(novel-to-video/text-storyboard/character-design/storyboard-to-seedance-prompt/generate-film-video-prompt/novel-reader)+ yuyou-dev/dreamina-cli-skill 真实方法论**:15秒clip制/物理动作外化/色温光向规范/16:9横版三视图/逐条强化提示词/对白四要素。 |
| v2.2.0 | 2026-07-14 | 深度借鉴 4 个真实开源同类 skill(storyboard-sketch-narrative/novel-to-storyboard/storyboard-converter/ark-novel-to-tuiwen);新增普通小说独立模式(Phase 0b)与角色圣经/风格预设;7 字段分镜表升级 |
| v2.1.0 | 2026-07-14 | 基于 IMA 笔记《story-to-video-master 完整改编SKILL》深度改编;对齐 novel-master 真实 v2 项目结构(中文键名/整卷章节/角色子目录);用可验证方法论替代无法核实的私有命名 skill;强化双向闭环与回写 |
| v2.0.0 | 2026-06-01 | 基础融合版本(故事板 v1.1 格式) |
| v1.0.0 | 2026-05-01 | 初始版本,基础分镜生成 |

---

## 核心改进说明

### 1. 融合五项可验证方法论
- Hollywood 分镜语法(景别/运镜/三视图前置锁定)
- Dan Wells 七点结构法(质量闸门)
- 钩子科学 / 半结果传播链(停不下来的连载引擎)
- T2I→I2V→ffmpeg 视频管线
- 诊断反馈循环质控

### 2. 深度适配 novel-master 真实项目(而非笔记假设结构)
- 自动读取 `settings/characters/<名>/{voice.md,state.json,bias_pack.json}`
- 解析 `chapters/arcN-*.md` 整卷文件并按 `## 第N集`/`### 壹·一` 切分
- 兼容 `foreshadowing.json` / `conflicts.json` 的**中文键名**
- 支持 v2 `plot_bus.json` / `ncg.json` 的地理与密度校验
- 继承 `style-log.md` 的**日漫风格增强层**(括号体独白/慢镜头→专属分镜设计)

### 3. 双向闭环设计
- novel-master → 改编:数据自动流转,零重复输入
- 改编 → novel-master:分镜结果可回写 `output/`,形成创作闭环

### 4. 七点结构法加持
- Phase 7 引入 Dan Wells 七点结构法,确保短剧结构符合经典叙事框架
