#!/usr/bin/env python3
"""Checks that every skills/*/SKILL.md has portable Agent Skills frontmatter.

The frontmatter must be plain `key: value` lines between `---` fences, with a
`name` that matches the skill's directory and a non-empty `description`.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(text):
    lines = text.split("\n")
    if lines[0] != "---":
        raise ValueError("must start with a `---` line")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("has no closing `---` line")
    fields = {}
    for line in lines[1:end]:
        key, sep, value = line.partition(":")
        if not sep or not key or key != key.strip():
            raise ValueError(f"line is not `key: value`: {line!r}")
        if key in fields:
            raise ValueError(f"repeats `{key}`")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key] = value
    return fields


def check(path):
    fields = frontmatter(path.read_text(encoding="utf-8"))
    problems = [f"unknown field `{k}`" for k in fields if k not in ALLOWED]
    name = fields.get("name", "")
    if not NAME.match(name) or len(name) > 64:
        problems.append("`name` must be 1-64 lowercase letters, digits and single hyphens")
    if name != path.parent.name:
        problems.append(f"`name` must match the directory `{path.parent.name}`")
    description = fields.get("description", "")
    if not description or len(description) > 1024:
        problems.append("`description` must be 1-1024 characters")
    return problems


def main():
    failed = False
    skills = sorted(ROOT.glob("skills/*/SKILL.md"))
    if not skills:
        print("no skills/*/SKILL.md files found")
        failed = True
    for path in skills:
        rel = path.relative_to(ROOT)
        try:
            problems = check(path)
        except ValueError as e:
            problems = [f"frontmatter {e}"]
        for p in problems:
            print(f"{rel}: {p}")
        failed |= bool(problems)
        if not problems:
            print(f"{rel}: ok")
    for path in sorted(ROOT.glob(".claude-plugin/*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except ValueError as e:
            print(f"{path.relative_to(ROOT)}: invalid JSON: {e}")
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
