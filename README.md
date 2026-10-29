# video_2_webplatform (v2w)

[中文](#中文) · [English](#english)

---

## 中文

输入一篇论文或一个 idea，输出一条 30–60 秒的竖屏科普短视频和发布文案。**全自动运行，只有最后的样片需要人看。**

v2w 是一组给 coding agent（Claude Code 等）用的 **skill**，组织方式参考 [PaperOrchestra](https://github.com/Ar9av/PaperOrchestra)：一个总入口，加上七个阶段 skill，再加一个独立评审 skill。每个 skill 由三部分组成：

- `SKILL.md`：agent 读取并执行的指令
- `references/`：规则、rubric、模板
- `scripts/`：只做确定性操作的辅助脚本（Python 标准库 + ffmpeg，不联网，不调用 LLM）

### 流水线

```
论文 / idea
 1 拆原理   v2w-distill    → principle.md      ⟶ 评审 A（内容）
 2 参考学习 v2w-reference  → 同话题视频拆解
 3 脚本     v2w-script     → brief.md          ⟶ 评审 B（讲解顺序）
 4 制作     v2w-production → 样帧 / 分镜 / 成片 ⟶ 评审 C（画面）
 5 配乐     v2w-score      → 混音              ⟶ 音乐指标（机器）
 6 审核     v2w-review     → 机器检查           ⟶ 评审 D（成片）
   ── 样片：唯一的人工环节（通过 / 打回）──
 7 发布     v2w-publish    → 文案，按配置上传
```

- **评审 A–D** 由 `v2w-critique` 执行：新开一个 subagent，只给它产物和固定的 rubric，按 rubric 打分；是否通过由脚本判定。不通过就自动修改，最多重试 2 次，仍不通过则把问题带到样片审核。
- **穿插现成的 skill**：读论文用 nature-reader，核实事实用 deep-research，搜参考视频用 claude-in-chrome，扒字幕用转写类 skill，做画面用 animate / anatomy。没装的 skill 会走降级方案。
- **授权写在项目配置里**：`v2w.config.json` 里一次写好"能否搜参考视频、能否调用托管音乐 API、审核通过后是只填表还是直接发布"，运行中途不会停下来询问。

### 快速开始

```bash
git clone https://github.com/Feng-Y-28/video_2_webplatform.git
bash video_2_webplatform/setup.sh ~/my-videos     # 建项目目录（本地 git），skill 只链接到这个项目
python3 video_2_webplatform/skills/v2w-orchestra/scripts/new_piece.py ~/my-videos my-first-piece --input paper.pdf
```

然后在 `~/my-videos` 里打开 Claude Code，说"用 v2w 把 my-first-piece 做完"。依赖见 [docs/dependencies.md](docs/dependencies.md)。

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

v2w is a pack of **skills** for coding agents (Claude Code and others),
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
 4 production  v2w-production  → look / board / cut  ⟶ critique C (visual)
 5 score       v2w-score       → mix                 ⟶ music checks (machine)
 6 review      v2w-review      → machine checks      ⟶ critique D (final)
   ── sample: the only human step (approve / revise) ──
 7 publish     v2w-publish     → post copy, upload per config
```

- **Critiques A–D** (`v2w-critique`): a fresh subagent scores the artefact
  against a fixed rubric without seeing the author's reasoning; a script
  decides pass/fail. Failures are fixed automatically (≤ 2 retries), then
  carried into the sample review.
- **Composes existing skills**: nature-reader (papers), deep-research (fact
  check), claude-in-chrome (reference search, upload), a transcript skill,
  animate / anatomy (picture). Each has a fallback when missing.
- **Standing consent** in `v2w.config.json`: browsing, hosted music APIs, and
  whether approval means fill-the-form or publish. Nothing is asked mid-run.

### Quick start

```bash
git clone https://github.com/Feng-Y-28/video_2_webplatform.git
bash video_2_webplatform/setup.sh ~/my-videos     # project scaffold (local git), skills linked into it only
python3 video_2_webplatform/skills/v2w-orchestra/scripts/new_piece.py ~/my-videos my-first-piece --input paper.pdf
```

Open Claude Code in `~/my-videos` and say "run v2w on my-first-piece".
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
