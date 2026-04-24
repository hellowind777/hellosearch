import path from "node:path"
import os from "node:os"
import { mkdtemp, readFile, rm } from "node:fs/promises"
import test from "node:test"
import assert from "node:assert/strict"

import { getInstallInfo, installSkill } from "../lib/install-skill.mjs"

test("installSkill copies the skill payload into the target directory", async () => {
  const tempRoot = await mkdtemp(path.join(os.tmpdir(), "hellosearch-"))

  try {
    const result = await installSkill({ targetRoot: tempRoot })
    const skillRoot = path.join(tempRoot, "hellosearch")
    const skillMd = await readFile(path.join(skillRoot, "SKILL.md"), "utf-8")

    assert.equal(result.destination, skillRoot)
    assert.match(skillMd, /name: hellosearch/)
  } finally {
    await rm(tempRoot, { recursive: true, force: true })
  }
})

test("getInstallInfo resolves claude-code user scope target", () => {
  const info = getInstallInfo({
    host: "claude-code",
    scope: "user",
    homeDir: "/tmp/example-home",
    cwd: "/workspace/project",
  })

  assert.equal(info.targetRoot, path.resolve("/tmp/example-home/.claude/skills"))
  assert.equal(info.host, "claude-code")
})

test("getInstallInfo resolves openclaw project scope target", () => {
  const info = getInstallInfo({
    host: "openclaw",
    scope: "project",
    homeDir: "/tmp/example-home",
    cwd: "/workspace/project",
  })

  assert.equal(info.targetRoot, path.resolve("/workspace/project/skills"))
  assert.equal(info.host, "openclaw")
})
