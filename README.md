# sidecars skills

Two Agent Skills that teach an agent the [sidecars.dev](https://sidecars.dev) review loop, where a human reviews the agent's work before any pull request exists:

- `api-design-review`: the design as concise code on a pushed branch, before implementation starts.
- `change-review`: the finished work, split into a Stack of Change Sets, before it becomes pull requests.

The agent submits with the `sidecars` CLI, waits in the background while the human reviews, then replies to every comment and submits the next Round until the human approves. The skills name only six stable commands and leave every flag and manifest field to the CLI's `--help` and `sidecars review schema`.

## Install

The agent needs the CLI on its machine:

```sh
curl -fsSL https://sidecars.dev/install.sh | sh
sidecars login
```

Then add the skills, either with [`skills`](https://github.com/vercel-labs/skills):

```sh
npx skills add sidecars-dev/skills
```

or as a Claude Code plugin:

```
/plugin marketplace add sidecars-dev/skills
/plugin install sidecars@sidecars
```

## Choose when they run

The skills don't wire themselves into any other workflow. Say when to use them in your own `CLAUDE.md` or `AGENTS.md`, for example:

```md
- After grilling a plan, run /api-design-review before /to-spec. The spec cites the Review's KEY-n and the design branch.
- When implementation is finished, run /change-review instead of opening pull requests.
```

## Development

Each skill is `skills/<name>/SKILL.md` with portable frontmatter (`name` and `description`) and no hooks. CI runs `python3 scripts/check-skills.py`, which checks every `SKILL.md`'s frontmatter and the `.claude-plugin/` JSON.

When the CLI changes a command these skills name, or its `next:` lines, check the skills still match `sidecars <command> --help`.
