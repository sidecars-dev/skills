---
name: api-design-review
description: Put an API design before the human on sidecars.dev as concise design files on a pushed branch, and iterate on their comments until they approve. Use before implementing a design, or when asked for an API Design Review.
---

An API Design Review shows the human the shape of the work before you build it: the smallest amount of code that conveys the design, in whatever language the work is in. The human reads it on sidecars.dev, often hours later and on their phone, and hands it back with a Verdict: Approve or Request Changes. You drive it with the `sidecars` CLI. You push ordinary branches to GitHub and never open a pull request.

This skill names six commands: `sidecars whoami`, `sidecars login`, `sidecars review schema`, `sidecars review submit`, `sidecars review wait` and `sidecars review handback`. Every flag and manifest field is in `sidecars <command> --help` and `sidecars review schema design`. Read them there, since they track the CLI.

## 1. Check the CLI

Run `sidecars whoami` first in every session.

- **Command not found:** tell the human the CLI is missing and give them the install command, then stop. Installing software is their decision, so leave running it to them:

  ```sh
  curl -fsSL https://sidecars.dev/install.sh | sh
  ```

- **Auth error** (its `next:` line names `sidecars login`): follow [Auth](#auth), then run `sidecars whoami` again.

Before the first manifest of the session, run `sidecars review schema design --example`. It prints a valid manifest from the same source the server validates against.

## 2. Write the design files

Submit at spec time: once the plan is settled, and before you write any implementation.

Write the design as code a reviewer can read in one sitting: interfaces, types, enums, function signatures, and a few call sites that show how it's used. Any language works, and pseudo-code is fine. Leave out bodies, plumbing, error handling and tests unless the design is about them. If a file wouldn't change the human's mind about the design, drop it.

Choose the branch first, because it decides what happens after approval:

- **Throwaway:** pseudo-code on its own branch, for example `design/<topic>` with the files in a `design/` folder. You'll delete it once the design is carried forward.
- **Real code:** the stubs live in the real codebase, on the branch you'll go on to implement on.

Each Design Part is one branch in one repo. When the design spans repos, give each repo a Design Part, ordered the way the work would deploy.

In the manifest, list the files in the order the human should read them. Label files or lines `new`, `changed` or `removed` where the design touches existing code. Put your reasons in Agent Notes on the lines they explain, so the human sees why each part is shaped that way. Write a note for a choice the human would otherwise ask about, not to restate the code.

Commit and push. From now on, keep every file's path stable (see [Iterate](#5-iterate-on-request-changes)).

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

The Handback groups open threads by Design Part. A line anchor reads `` `path`, lines a–b `` and quotes the design file. Each thread carries its thread id. A thread from an earlier Round also shows your last reply's status and whether the human responded this Round.

1. Address every open thread by editing the design files on the same branch. Then push.
2. Write one reply per open thread in the manifest's top-level `replies`: `{"thread": "<thread id>", "status": "...", "body": "..."}`.
   - `addressed`: you made the change. Say what changed.
   - `declined`: you won't make it. Say why.
   - `discuss`: you need the human's answer. Ask the question.
3. Put the whole design in the manifest again, as it is now, alongside the replies. Dry-run it, then submit the next Round with `sidecars review submit --review KEY-n -f manifest.json`. The submit warns about any open thread you didn't reply to. Treat that warning as a miss to fix in the next Round.
4. Go back to [waiting](#4-wait-for-the-handback).

Only the human resolves a thread, and every thread follows its text across Rounds:

- A thread stays on its lines when the text is identical at the same repo and path.
- Changing the commented lines outdates the thread to the file.
- Renaming or dropping a file outdates its threads to the whole Review.
- Only an unchanged file keeps the human's Sign-off.

So keep paths stable, and change only what the threads ask for. Then the human re-reads only what moved.

## 6. Finish on Approve

1. Apply any comments that came with the Approve. Make no further Round.
2. Settle the branch:
   - **Throwaway:** delete it locally and on GitHub once the design is carried forward, for example into a spec. sidecars keeps the files at their SHAs, so `KEY-n` stays the record.
   - **Real code:** keep it and build the implementation on it.
3. Tell the human the approved design: `KEY-n`, each Design Part's repo and branch, anything you changed after approval, and what you did with the branch. Anything that follows, such as a spec, cites `KEY-n` and the design branch.

## Auth

When a command fails and its `next:` line names `sidecars login`:

1. Run `sidecars login` in the background. It prints a URL and a code at once.
2. Show the human the URL and the code, and ask them to approve on any device where they're signed in to sidecars.dev.
3. When `login` exits successfully, run the failed command again.

Make one login attempt per failure. If the login expires or fails, tell the human what its error says and stop. The human approves on their own device, so the token never passes through the chat: logging in is always `sidecars login`.
