# 视频生成平台适配参考（6 平台 · 官方文档核实版）

> **核实方式**：本表所有"可调用性/命令/端点/限制"均来自各平台**官方文档 / 官方 Skill 仓库 / 官方 CLI** 的
> 真实抓取（2026-07-14 核查），不臆造。来源 URL 见各节「官方来源」。
> 本 SKILL 的 Phase 5（提示词 transpile）与 Phase 6（视频生成）据此把统一分镜转写为各平台可执行内容。

---

## 0. 统一抽象（本 SKILL 内部标准）

无论哪个平台，内部先流转「统一分镜单元」，Phase 5 再 transpile 到平台方言：

```
统一分镜单元 = {
  shot_id, duration_sec(4-15), style,
  subject(角色@绑定), scene, camera(景别+运镜),
  action_chain(物理动作链, 不含抽象词),
  lighting(方向+色温+强度), audio(对白/BGM/SFX),
  reference_assets(角色图/场景图/道具图路径)
}
```

## 1. 六平台分类总览（决定本 SKILL 的适配深度）

| 平台 | 可程序化调用 | 本 SKILL 适配方式 | 调用脚本 |
|------|------------|----------------|---------|
| **即梦 Dreamina**（Seedance 2.0） | ✅ 官方 CLI + 火山引擎 API | 脚本自动生成（异步 submit_id 轮询） | `dreamina_gen.py` |
| **LibTV**（liblib.tv，Seedance 2.0/Star Video 2.0） | ✅ 官方 OpenClaw Skill 包 + agent-im OpenAPI | 脚本"传话层"（Bearer Key + 会话轮询） | `libtv_gen.py` |
| **RunningHub**（runninghub.cn） | ✅ 标准 OpenAPI + ComfyUI 工作流 | 脚本（上传→endpoint→轮询，含重试） | `runninghub_gen.py` |
| **小云雀**（字节剪映） | ⚠️ 消费端仅手动；企业端走火山引擎 API | 输出"可粘贴"剧本块 + 参考图清单 | 无（Phase 5 产出文本） |
| **随变 APP**（抖音/字节） | ❌ 仅手机 App 手动（Seedance 2.0 底座） | 输出"可粘贴"单句/多幕提示词序列 | 无（Phase 5 产出文本） |
| **Tapnow**（app.tapnow.ai） | ❌ 仅 Web 画布手动（无官方 API） | 输出"可粘贴"画布搭建清单 | 无（Phase 5 产出文本） |

> **分流原则**：Phase 6 若用户选「即梦 / LibTV / RunningHub」→ 走脚本自动调用；
> 选「小云雀 / 随变 / Tapnow」→ **不调脚本**，由 Phase 5 产出"可直接粘贴到 App/Web"的内容，
> 并在回复中明确"该平台目前仅支持手动使用，请复制以下文本到对应界面"。

---

## 2. 即梦 Dreamina（Seedance 2.0）✅ 可自动调用

**官方来源**：
- 官方 CLI 安装页：`https://jimeng.jianying.com/cli`（安装脚本当前版本 1.4.11，已核实）
- CLI wrapper 参考：`https://github.com/yuyou-dev/dreamina-cli-skill`
- 企业端：火山引擎即梦 API（文生图 3.x / 视频生成 3.0 Pro，AK/SK 接入）

**安装与鉴权**：
```bash
curl -fsSL https://jimeng.jianying.com/cli | bash   # 安装 dreamina CLI
dreamina login                                       # 交互登录
dreamina user_credit                                 # 查积分
```

**真实子命令与参数**（来自 CLI 文档，已核实）：
| 子命令 | 用途 |
|--------|------|
| `text2image` | 文生图 |
| `image2image` | 图生图 |
| `image_upscale` | 图像放大 |
| `text2video` | 文生视频 |
| `image2video` | 单图生视频 |
| `frames2video` / `multiframe2video` | 多帧故事（2-20 张） |
| `multimodal2video` | **全能参考**（文本+图+可选视频+音频，最多 9 图 / 3 视频 / 3 音频） |

- 比例 `--ratio`：16:9 / 9:16 / 1:1；时长 `--duration`（整数秒）。
- `1080p` 须绑定 `seedance2.0_vip` 模型。
- **异步工作流**：提交后返回 `submit_id` → `query_result --submit_id <id> [--poll]` 轮询（建议每分钟一次）→ 完成取 URL → `curl` 下载。

**本 SKILL 封装**：`scripts/dreamina_gen.py`（稳定 JSON 返回、`--dry-run` 预览、参考图绑定、缺失 CLI 优雅报错）。

**提示词方言（Seedance 2.0）**：
- 画风前置定调（放开头）：「3D 国漫 CG」「真人电影感」「2D 漫画」。
- 人物元素必含：身高/体型/年龄/发型/头饰/五官/妆容/服饰材质配色/配饰/神态动作。
- 时序强约束：`0-1.5s：xxx；1.5-2s：xxx`，每 clip 4-15 整数秒。
- 末尾固定追加：`不要BGM，不要字幕`（另行配音轨时去掉）。
- 参考图绑定：提示词内用 `图1/图2/图3` 引用，顺序对应传入的 `--image` 清单。
- 并发硬限制：**最多 3 个排队/生成中任务**（超额需排队）。

---

## 3. LibTV（liblib.tv，Seedance 2.0 / Star Video 2.0）✅ 可自动调用

**官方来源**：
- 官方 Skill 仓库（OpenClaw 规范）：`https://github.com/libtv-labs/libtv-skills`
- 安装：`npx skills add libtv-labs/libtv-skills --skill libtv-skill`
- 官网画布：`https://www.liblib.tv/canvas`
- 适配说明：官方 README 明确"遵循 OpenClaw 技能规范，可被支持该规范的 AI Agent 平台直接识别和调用"；新闻稿确认"小龙虾(OpenClaw)/QClaw 等 Personal Agent 可直接调用 LibTV 创作能力"。

**调用模型**：**会话式（agent-im OpenAPI）**，而非参数化节点 API。Agent 侧只负责"传话"（发自然语言消息），分镜拆解/工作流编排/模型选择由 LibTV 后端 Agent 完成。**不要自己编排分镜或润色 prompt**。

**鉴权**：
```
Authorization: Bearer <LIBTV_ACCESS_KEY>
```
密钥获取：LibTV 网页「开始创作 → LibTV Skills → 复制 access key」→ 写入环境变量 `LIBTV_ACCESS_KEY`（或 `.env`）。
IM 服务地址默认 `https://im.liblib.tv`（可用 `OPENAPI_IM_BASE` / `IM_BASE_URL` 覆盖）。

**官方端点（来自 README API 参考）**：
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/openapi/session` | 创建会话 / 发送消息。Body：`{"sessionId":可选,"message":可选}` |
| GET | `/openapi/session/:sessionId` | 查询会话消息列表 |
| POST | `/openapi/session/change-project` | 切换绑定项目 |
| POST | `/openapi/file/upload` | 上传图片/视频到 OSS（multipart `file`，仅 image/* video/*，≤200MB） |

- 创建会话返回：`{"data":{"projectUuid":"…","sessionId":"…","projectUrl":"https://www.liblib.tv/canvas?projectId=…"}}`
- 上传返回 OSS URL：`https://libtv-res.liblib.art/claw/{projectUuid}/{uuid}.png`

**结果获取（轮询，无回调）**：
```
python3 query_session.py <SESSION_ID> --after-seq 0   # 每 8 秒轮询
```
完成判定：messages 中出现 `role: assistant` 且 content 含图片/视频 URL。
超时策略：连续轮询 3 分钟无结果 → 告知用户去 `projectUrl` 画布查看。
下载：`download_results.py <SESSION_ID> --output-dir … --prefix …` 批量下载。

**模型与限制**：内置 Seedance 2.0、Kling 3.0/O3、Wan 2.6、NanoBanana、Midjourney、Seedream 5.0 等。
Seedance 2.0 多模态支持图像/视频/音频/文本四模态自由组合，最多 12 个参考文件（图≤9、视频≤3、音频≤3），生成时长 **4–15 秒**，自带原生音效与配乐。
> 注：「Star Video 2.0」即 LibTV 对 Seedance 2.0 的命名。

**本 SKILL 封装**：`scripts/libtv_gen.py`（传话层：upload → session 发原始描述 → 8s 轮询 → 下载 + 返回 projectUrl）。

---

## 4. RunningHub（runninghub.cn）✅ 可自动调用

**官方来源**：
- 标准模型 API 文档页：`https://www.runninghub.cn/call-api/standard-api`
- API 控制台（获取 Key）：`https://www.runninghub.cn/enterprise-api/sharedApi`
- 调用记录：`https://www.runninghub.cn/call-api/call-record`
- 官方契约文档：`https://github.com/HM-RunningHub/ComfyUI_RH_OpenAPI/blob/main/developer-kit/rh-api-contract.md`
- 无依赖 Python 客户端：`https://github.com/HM-RunningHub/ComfyUI_RH_OpenAPI/blob/main/developer-kit/examples/python/client.py`
- 模型注册表：`https://github.com/HM-RunningHub/ComfyUI_RH_OpenAPI/blob/main/developer-kit/model-registry.public.json`

**Base URL**：`https://www.runninghub.cn/openapi/v2`（境外用 `https://www.runninghub.ai/openapi/v2`）。
**鉴权**：所有请求 `Authorization: Bearer <RH_API_KEY>` + `Content-Type: application/json`。Key 在控制台获取，写入 `RH_API_KEY` / `RH_API_BASE_URL`。

**三步调用流程**：
1. 上传本地媒体（如需）：
   `POST {base}/media/upload/binary`（multipart `file`）→ `{"code":0,"data":{"download_url":"https://…"}}`
2. 提交任务：
   `POST {base}/{endpoint}`，Body 如 `{"prompt":"…","aspectRatio":"16:9", …}` → `{"taskId":"…"}`
3. 轮询：
   `POST {base}/query`，Body `{"taskId":"…"}`。

**真实端点（模型注册表路径）**：
- 文生图：`rhart-image-v1/text-to-image`
- 图生图：`rhart-image-v1/edit`
- 图生视频（Sora2 官方支持真人）：`rhart-video-s-official/image-to-video-realistic`
- Seedance 2.0 系列：`seedance2.0/…`、`seedance2.0-fast/…`、`seedance2.0-mini/…`（文生视频/图生视频/多模态视频）

**返回格式（SUCCESS 终态）**：
```json
{"status":"SUCCESS","results":[{"url":"https://…","outputType":"video"}]}
```
健壮性：URL 取 `url`/`outputUrl`；文本取 `text`/`content`/`output`。
轮询状态：`CREATE/QUEUED/RUNNING`（非终态）→ `SUCCESS/FAILED/CANCEL`（终态）。间隔建议 5 秒，最长 10–30 分钟。

**参数规则（契约明确）**：`STRING`→字符串；`LIST`→取声明枚举之一（如 duration 仅 `4/8/12`）；`BOOLEAN`→JSON 布尔；`IMAGE/VIDEO/AUDIO`→先上传取 URL 再传；必填项必须存在；**禁止臆造枚举/默认值**。

**Seedance 2.0 的 asset_ids / real_person_mode（确切）**：
- 图生视频、多模态视频节点统一输入 `asset_ids`，外加 `real_person_mode`、`conversion_slots`。
- `asset_ids` 接受：单个素材 ID、`asset://<id>`、逗号/换行分隔、JSON 数组字符串。
- 图生视频槽位：`first_frame,last_frame`；多模态槽位：`image1..image9, video1..video3`。
- `real_person_mode=false`：保持原始本地上传；`=true`：先转成 Seedance 素材再写入（受真人内容拦截，错误码 `1505`）。

**重试策略**（来自官方 client.py）：提交/上传最多 3 次指数退避；仅重试网络错误/429/5xx，不重试 400/401/403/余额不足/内容审核类错误。超时返回 `taskId` 供用户到 call-record 自查。

**模型与限制**：视频生成含 234 个节点（Sora2/Veo3.1/Kling2.5–3.0-4k/Vidu/Wan2.5–2.7/MiniMax Hailuo/Seedance v1.5/2.0/Runway/PixVerse/SkyReels/LTX-2/Hunyuan 视频等）。调用消耗账户余额。

**本 SKILL 封装**：`scripts/runninghub_gen.py`（upload → generate(endpoint+参数) → 轮询含重试 → 返回 results）。

---

## 5. 小云雀（字节剪映）⚠️ 消费端仅手动

**官方来源**：官网 `https://xiaoyunque.jianying.com`；企业端接口在火山引擎文档树（"小云雀-智能生视频 Agent / 短剧漫剧 Agent / 营销成片 Agent"，需自助下单开通）。

**能力定性**：字节剪映旗下 AI 短剧/短片创作平台；消费端（App/Web）**纯手动，无个人 API/CLI**，需人工粘贴"文本需求 + 参考图"。短剧 Agent 2.0 基于 Seedance 2.0，支持 **≤10 万字剧本一键成片**。

**本 SKILL 适配（仅文本产出）**：
- Phase 5 输出「**可直接粘贴的剧本块**」：按集组织，每集含【剧本正文段落】+【参考图说明（角色图/场景图路径或描述）】+【风格/时长】。
- 提示用户：在 App 内新建项目 → 粘贴剧本 → 上传对应参考图 → 选择短剧 Agent 2.0 一键成片。
- 企业用户若已开通火山引擎"小云雀 Agent"接口，可另接火山引擎 API（不在本 SKILL 免费封装范围）。

---

## 6. 随变 APP（抖音/字节）❌ 仅手机 App 手动

**官方来源**：抖音官方协议 `https://www.douyin.com/agreements/?id=6773901168964798477`（列明"随变"为抖音旗下 AI 创作独立版本）；应用商店描述确认默认模型 **Seedance 2.0**。

**能力定性**：抖音旗下面向年轻人的潮流娱乐 + AI 创作社区。**无开放 API/CLI/Agent 接口**，仅手机 App 对话框手动使用。当前 App 内用 Seedance 2.0 **免费不限次**（偶发生成失败，建议一次只生成一个视频）。
两种模式：
- **创作模式**：用自己的 AI 数字形象（需拍真人头像"创建形象"）+ 文本提示词生成视频。
- **合拍模式**：与热门 IP（如"奶龙"）或好友授权数字形象 @ 同框共创，对话框中 @ 选择对象 + 提示词。

**本 SKILL 适配（仅文本产出）**：
- Phase 5 输出「**分镜头提示词序列**」：每条聚焦一个镜头/主题（因为"一次最好只生成一个视频"），把长故事拆成多条独立可发送的分镜提示词。
- 明确标注每条的模式：`【创作模式】`（用自己形象）或 `【合拍模式】@某IP`（如 @奶龙）。
- 控制单条长度在对话框可直接粘贴。提醒：建形象时背景整洁、光线良好（否则会代入建形象时的背景）。
- 示例输出形态：
  ```
  【创作模式】一个穿灰外套的年轻男生站在旧街道黄昏里，风掀起衣角，镜头从中景缓缓推近到面部特写，氛围孤独带隐忧，电影写实风格，4秒。
  【合拍模式 @奶龙】男生把铁片递给奶龙，奶龙好奇地翻转查看，暖光，俏皮节奏，5秒。
  ```

---

## 7. Tapnow（app.tapnow.ai）❌ 仅 Web 画布手动

**官方来源**：官网 `https://app.tapnow.ai`（定位 "Your Agentic Creative Canvas / 最像导演的 AI"）；案例 `https://news.qq.com/rain/a/20251113A00CYC00`。
> ⚠️ 排除项：`app.tapnow.top` 当前 DNS 不可解析；GitHub 上的 `Tapnow-Studio-PP` 等均为第三方逆向仿制项目，**非官方 API**，不可作为程序化接口。

**能力定性**：面向专业视频生产的「Agentic 创意画布」，可做商业 TVC / 多镜头叙事 / IP 形象一致性 / 电商广告 / 短剧 / ACG。核心是 **Web 端无限画布节点系统**：为每个镜头建立"节点—镜头—场景"结构，指定场景、镜头角度、动作轨迹、时长（模块化分镜）。支持文生视频 + 图生视频 + 节点控制生视频，多模型接入（Nano Banana Pro、VEO3、Seedance 2.0 等）。**无官方开放 API/CLI**，仅 Web 手动拖拽节点。

**本 SKILL 适配（仅文本产出）**：
- Phase 5 输出「**画布搭建清单**」：按"节点—镜头—场景"组织，每个镜头给出：场景描述、镜头角度/运动、动作、时长、光影/色调、风格参照影片、配音/音效提示、IP 一致性参考图说明。
- 额外产出「**风格参照建议**」（如"参考《沙丘》构图 / 《孤注一掷》色调"），契合其"找影片参照"功能。
- 强调 **IP 一致性**：为跨镜头角色统一提供参考图/形象描述，方便用户在各节点手动指定。
- 用户按节点逐一录入画布即可。

---

## 8. 平台能力对照速查

| 平台 | 可调用 | 文生视频 | 图生视频 | 多参考 | 中文友好 | 音频直出 | 关键限制 |
|------|--------|---------|---------|--------|---------|---------|---------|
| 即梦 Seedance2.0 | ✅ CLI | ✅ | ✅ | ✅(图1/图2) | ⭐⭐⭐ | ✅ | 并发≤3；轮询 |
| LibTV | ✅ OpenAPI | ✅ | ✅ | ✅(≤12参考) | ⭐⭐⭐ | ✅ | 会话式传话；4-15s |
| RunningHub | ✅ OpenAPI | ✅ | ✅ | ✅(asset_ids) | ⭐⭐ | ❌ | 消耗余额；重试策略 |
| 小云雀 | ⚠️企业API | ✅ | ✅ | 部分 | ⭐⭐⭐ | — | 消费端手动；≤10万字剧本 |
| 随变 APP | ❌ | ✅(底座) | ✅ | 部分 | ⭐⭐⭐ | — | 仅App；免费不限次；一次一视频 |
| Tapnow | ❌ | ✅ | ✅ | ✅ | ⭐⭐ | — | 仅Web画布；专业向 |

> **默认主力**：即梦 Seedance2.0（自动 + 中文友好 + 参考图绑定成熟）。
> **需要 Agent 直连 OpenClaw（强集成）**：LibTV（声明支持 QClaw）/ RunningHub（标准 OpenAPI）。
> **需要电影级运镜**：转 Runway（见上版 adapter，仍可在 Phase 5 输出英文提示词）。
> **仅手动投喂**：小云雀 / 随变 / Tapnow，本 SKILL 只产"可粘贴内容"。

---

## 9. 本 SKILL Phase 6 分流逻辑（实现要点）

```
用户选平台
  ├─ 即梦        → scripts/dreamina_gen.py（自动，异步轮询）
  ├─ LibTV       → scripts/libtv_gen.py（自动，传话层+8s轮询）
  ├─ RunningHub  → scripts/runninghub_gen.py（自动，上传+endpoint+5s轮询重试）
  ├─ 小云雀      → 仅 Phase5 产出「剧本块文本」+ 手动投喂指引（不调脚本）
  ├─ 随变 APP    → 仅 Phase5 产出「分镜头提示词序列」+ 手动投喂指引
  └─ Tapnow      → 仅 Phase5 产出「画布搭建清单」+ 手动投喂指引
```

> ⚠️ 所有"自动调用"脚本默认**不主动执行付费生成**：需用户在启动协议 Step 4 显式选定平台并确认后调用；
> 否则 Phase 5 只产出可粘贴提示词。脚本缺失 CLI/Key 时一律优雅报错并给出安装方式（不崩溃）。
