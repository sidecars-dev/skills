---
name: change-review
description: Put finished work before the human on sidecars.dev as a Stack of Change Sets, before any pull request, and iterate on their comments until they approve. Use when implementation is done, or when asked for a Change Review.
---

A Change Review shows the human the code you implemented, split into reviewable pieces, before it becomes pull requests. The human reads it on sidecars.dev, often hours later and on their phone, and hands it back with a Verdict: Approve or Request Changes. You drive it with the `sidecars` CLI. You push ordinary branches to GitHub and never open a pull request.

This skill names six commands: `sidecars whoami`, `sidecars login`, `sidecars review schema`, `sidecars review submit`, `sidecars review wait` and `sidecars review handback`. Every flag and manifest field is in `sidecars <command> --help` and `sidecars review schema change`. Read them there, since they track the CLI.

## 1. Check the CLI

Run `sidecars whoami` first in every session.

- **Command not found:** tell the human the CLI is missing and give them the install command, then stop. Installing software is their decision, so leave running it to them:

  ```sh
  curl -fsSL https://sidecars.dev/install.sh | sh
  ```

- **Auth error** (its `next:` line names `sidecars login`): follow [Auth](#auth), then run `sidecars whoami` again.

Before the first manifest of the session, run `sidecars review schema change --example`. It prints a valid manifest from the same source the server validates against.

## 2. Split the work into a Stack

Submit when the work is finished and its tests pass, at the point where you'd otherwise open pull requests.

A **Change Set** is one branch that stands in for one pull request: one purpose, small enough to review in one sitting, and building and passing tests on its own. Split by your own judgement of what the human can follow. A refactor the feature needs usually comes before the feature, and a mechanical rename goes in its own Change Set so it doesn't bury the real change.

A **Sub-stack** is an ordered run of Change Sets in one repo, all deployed before the next Sub-stack. Its first Change Set compares the Sub-stack's base with its branch, and each later one compares the branch before it with its own. So each branch builds on the one before it. The **Stack** lists the Sub-stacks in deployment order. Two Sub-stacks can share a repo when deploys interleave, for example API part 1, then the frontend, then API part 2.

Give every Sub-stack and Change Set a title that says what it's for. Add a description when the title can't carry the context. Where reading order matters, list the key files with a `why` each; the rest follow in path order. Add Agent Notes to new-side lines whose reasons aren't visible in the code. Write a note for a choice the human would otherwise ask about, not to restate the code.

Push every branch. From now on, keep every branch name stable (see [Iterate](#5-iterate-on-request-changes)).

## 3. Submit

1. Run `sidecars review submit --dry-run -f manifest.json`. It runs every server check and creates nothing. Fix each error at the JSON path on its `path:` line, and repeat until it passes.
2. Run `sidecars review submit -f manifest.json`. Compare each branch's SHA in the output with `git rev-parse <branch>`. Those SHAs are exactly what the human reviews.
3. Show the human the `KEY-n` and the link.

## 4. Wait for the Handback

Start `sidecars review wait KEY-n` in the background and end your turn. Waiting costs nothing, and your harness resumes you when it exits. Its output is the Handback.

Without background commands, end your turn after showing the link. When the human says they're done, run `sidecars review handback KEY-n` once.

The Handback opens with a `state:` line and ends with a `next:` line. Do what the `next:` line says:

- `changes_requested`: [iterate](#5-iterate-on-request-changes).
- `approved`: [finish](#6-finish-on-approve). Approve is final.
- `closed`: the human set the Review aside. Stop work on it.
- `waiting`, after a `--timeout`: wait again.

When `wait` fails instead, run its `next:` line, which waits again.

`sidecars review handback KEY-n` prints the same Handback again at any time and never consumes it. Re-read it after your context is compacted.

## 5. Iterate on Request Changes

The Handback groups open threads by Change Set. Each anchor names the Change Set title, repo, branch, path, side and line range, and quotes the code. Each thread carries its thread id. A thread from an earlier Round also shows your last reply's status and whether the human responded this Round.

1. Address every open thread on the branch of the Change Set it's anchored to. Rebase every later branch in its Sub-stack onto the change, and push them all.
2. Write one reply per open thread in the manifest's top-level `replies`: `{"thread": "<thread id>", "status": "...", "body": "..."}`.
   - `addressed`: you made the change. Say what changed.
   - `declined`: you won't make it. Say why.
   - `discuss`: you need the human's answer. Ask the question.
3. Put the whole Stack in the manifest again, as it is now, alongside the replies. Dry-run it, then submit the next Round with `sidecars review submit --review KEY-n -f manifest.json`. The submit warns about any open thread you didn't reply to. Treat that warning as a miss to fix in the next Round.
4. Go back to [waiting](#4-wait-for-the-handback).

Only the human resolves a thread, and every thread follows its code across Rounds:

- A thread stays on its lines when the exact lines still exist on the same side of the same file.
- Changing the commented lines outdates the thread to the file.
- Dropping the Change Set or file outdates its threads to the whole Review.
- A file keeps the human's Sign-off only when its patch in that Change Set is identical, matched by branch and path.

So keep branch names stable, and change only what the threads ask for. Then the human re-reads only what moved.

## 6. Finish on Approve

1. Apply any comments that came with the Approve, on the branches they belong to. Make no further Round.
2. Tell the human the approved Stack: `KEY-n`, each Sub-stack's repo and its branches in order, and every Change Set you changed after approval.

Then stop. Turning the Stack into pull requests is the human's next step.

## Auth

When a command fails and its `next:` line names `sidecars login`:

1. Run `sidecars login` in the background. It prints a URL and a code at once.
2. Show the human the URL and the code, and ask them to approve on any device where they're signed in to sidecars.dev.
3. When `login` exits successfully, run the failed command again.

Make one login attempt per failure. If the login expires or fails, tell the human what its error says and stop. The human approves on their own device, so the token never passes through the chat: logging in is always `sidecars login`.
