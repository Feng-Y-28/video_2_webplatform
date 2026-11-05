# video_2_webplatform (v2w) — Codex

[中文](#中文) · [English](#english)

---

## 中文

输入一篇论文或一个 idea，输出一条 30–60 秒的竖屏科普短视频和发布文案。**全自动运行，只有最后的样片需要人看。**

v2w 是一组给 Codex 用的 **skill**，组织方式参考 [PaperOrchestra](https://github.com/Ar9av/PaperOrchestra)：一个总入口，加上七个阶段 skill，再加一个独立评审 skill。每个 skill 由三部分组成：

- `SKILL.md`：agent 读取并执行的指令
- `references/`：规则、rubric、模板
- `scripts/`：只做确定性操作的辅助脚本（Python 标准库 + ffmpeg，不联网，不调用 LLM）

### 流水线

```
论文 / idea
 1 拆原理   v2w-distill    → principle.md      ⟶ 评审 A（内容）
 2 参考学习 v2w-reference  → 同话题视频拆解
 3 脚本     v2w-script     → brief.md          ⟶ 评审 B（讲解顺序）
 4 制作     v2w-production → 样帧 look / 分镜 board ⟶ 评审 C（画面，完整成片之前）
 5 配乐     v2w-score      → 混音              ⟶ 音乐指标（机器）
 6 审核     v2w-review     → 机器检查           ⟶ 评审 D（成片）
   ── 样片：唯一的人工环节（通过 / 打回）──
 7 发布     v2w-publish    → 文案，按配置上传
```

- **评审 A–D** 由 `v2w-critique` 执行：新开一个 subagent，只给它产物和固定的 rubric，按 rubric 打分；是否通过由脚本判定。`max_retries`（默认 2）指首轮之外的自动重试次数，共 `1 + max_retries` 轮；预算用尽后允许一次修复加一轮验证评审，只有那轮通过才算通过，否则把问题带到样片审核。
- **评审 C 在完整成片之前**：它看样帧 look 和分镜 board，不是先做成片再补评审；成片阶段的改动必须另有复核记录（见评审 D）。
- **穿插现成的 skill**：读论文用 nature-reader，核实事实用 deep-research，搜参考视频用 Codex 搜索、已连接的插件或浏览器工具，扒字幕用转写类 skill，做画面用 animate / anatomy。没装的 skill 会走降级方案。
- **授权写在项目配置里**：`v2w.config.json` 里一次写好"能否搜参考视频、能否调用托管音乐 API、审核通过后是只填表还是直接发布"，运行中途不会停下来询问。

### 快速开始

在包含 `codex/port` 的本地仓库中运行（远端使用前需先发布该分支）：

```bash
cd video_2_webplatform
git switch codex/port
bash setup.sh ~/my-videos     # 建项目目录（本地 git），skill 只链接到这个项目
python3 skills/v2w-orchestra/scripts/new_piece.py ~/my-videos my-first-piece --input paper.pdf
```

然后运行 `codex -C ~/my-videos`，输入 `$v2w-orchestra 把 my-first-piece 做完`。
安装会创建 `AGENTS.md`，并将 9 个 skills 和共享规则链接到项目的 `.agents/skills/`。
已有配置和项目指令不会被覆盖。Codex 接入与旧项目迁移见 [docs/codex.md](docs/codex.md)，依赖见 [docs/dependencies.md](docs/dependencies.md)。

### 建议的使用方式：作品私有，skill 公开

```
~/my-videos/              私有：作品、debug 日志（本地 git）
video_2_webplatform/      公开：只放 skill
```

两个目录平级放置，不要嵌套。可复用的经验经过"提炼"再写进 skill，原始日志留在私有目录里。具体做法见 [docs/maintaining.md](docs/maintaining.md)。

### 原则

- 屏幕上的每个数字都要有出处，否则就标明是"简化示例"
- agent 听不到声音：配乐靠测量把关，样片审核是唯一的试听
- 评审独立：评审 agent 看不到作者的推理
- 对外的动作（API、上传、发布）只在配置允许时执行，发布一定在样片通过之后

---

## English

Input: a paper or an idea. Output: a 30–60 s vertical explainer video and
post copy. **Runs autonomously; the only human step is approving the final sample.**

v2w is a pack of **skills** for Codex,
organised like [PaperOrchestra](https://github.com/Ar9av/PaperOrchestra): one
orchestrator, seven stage skills and an independent critique skill. Each skill is a `SKILL.md`
(instructions), `references/` (rules, rubrics, templates) and `scripts/`
(deterministic helpers: Python standard library + ffmpeg; no network, no LLM).

### Pipeline

```
paper / idea
 1 distill     v2w-distill     → principle.md        ⟶ critique A (content)
 2 reference   v2w-reference   → same-topic videos broken down
 3 script      v2w-script      → brief.md            ⟶ critique B (explanation order)
 4 production  v2w-production  → look / board    ⟶ critique C (visual, before the full build)
 5 score       v2w-score       → mix                 ⟶ music checks (machine)
 6 review      v2w-review      → machine checks      ⟶ critique D (final)
   ── sample: the only human step (approve / revise) ──
 7 publish     v2w-publish     → post copy, upload per config
```

- **Critiques A–D** (`v2w-critique`): a fresh subagent scores the artefact
  against a fixed rubric without seeing the author's reasoning; a script
  decides pass/fail. `max_retries` (default 2) counts automatic retries
  *after* the first round, so a gate gets `1 + max_retries` rounds; when the
  budget is spent, one repair plus a single verification round is allowed, and
  only a PASS there ticks the gate. Otherwise the issues go to the sample review.
- **Critique C runs before the full build** on the look and the storyboard,
  not on a finished cut. A visual change made after C needs its own check and
  a note in `LOG.md` (critique D holds it).
- **Composes existing skills**: nature-reader (papers), deep-research (fact
  check), available search / plugin / browser tools (references, upload), a transcript skill,
  animate / anatomy (picture). Each has a fallback when missing.
- **Standing consent** in `v2w.config.json`: browsing, hosted music APIs, and
  whether approval means fill-the-form or publish. Nothing is asked mid-run.

### Quick start

Use a local checkout containing `codex/port`; publish the branch before
expecting a fresh remote clone to contain it:

```bash
cd video_2_webplatform
git switch codex/port
bash setup.sh ~/my-videos     # project scaffold (local git), skills linked into it only
python3 skills/v2w-orchestra/scripts/new_piece.py ~/my-videos my-first-piece --input paper.pdf
```

Run `codex -C ~/my-videos` and enter `$v2w-orchestra run my-first-piece`.
Setup creates `AGENTS.md` and links nine skills plus shared resources into
`.agents/skills/`, preserving existing configuration and instructions.
Codex setup and migration: [docs/codex.md](docs/codex.md).
Dependencies: [docs/dependencies.md](docs/dependencies.md).

### Recommended setup: private work, public skills

Keep your project (pieces, debug logs; local git) and this repo side by side,
never nested. Reusable lessons are distilled into the skills; the raw logs
stay private. See [docs/maintaining.md](docs/maintaining.md).

### Principles

- Every number on screen has a source, or is labelled a simplified example.
- The agent cannot hear: music is gated by measurements; the sample review is the only listen.
- Critiques are independent: the critic never sees the author's reasoning.
- Outward actions (APIs, upload, publish) only as the config allows, and publishing only after the sample is approved.

## License

MIT — see [LICENSE](LICENSE).
