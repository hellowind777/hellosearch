import path from "node:path"
import os from "node:os"
import { mkdtemp, readFile, rm } from "node:fs/promises"
import test from "node:test"
import assert from "node:assert/strict"

import { installSkill } from "../lib/install-skill.mjs"

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
