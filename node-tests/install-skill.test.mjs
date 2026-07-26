import test from "node:test"
import assert from "node:assert/strict"
import { existsSync } from "node:fs"
import { mkdir, mkdtemp, rm } from "node:fs/promises"
import os from "node:os"
import path from "node:path"

import {
  detectInstallTargets,
  detectPreferredHost,
  installSkill,
  installSkillEverywhere,
  planInstall,
} from "../lib/install-skill.mjs"

async function makeTempDir(prefix) {
  return mkdtemp(path.join(os.tmpdir(), prefix))
}

test("planInstall resolves preset directories per host and scope", () => {
  const context = { cwd: "/work/project", env: {}, homeDir: "/home/user" }

  assert.equal(
    planInstall({ host: "claude-code", scope: "user", ...context }).targetRoot,
    path.resolve("/home/user/.claude/skills"),
  )
  assert.equal(
    planInstall({ host: "claude-code", scope: "project", ...context }).targetRoot,
    path.resolve("/work/project/.claude/skills"),
  )
  assert.equal(
    planInstall({ host: "codex", scope: "user", ...context }).targetRoot,
    path.resolve("/home/user/.agents/skills"),
  )
  assert.equal(
    planInstall({ host: "agents", scope: "project", ...context }).targetRoot,
    path.resolve("/work/project/.agents/skills"),
  )
  assert.equal(
    planInstall({ host: "openclaw", scope: "user", ...context }).targetRoot,
    path.resolve("/home/user/.openclaw/skills"),
  )
  assert.equal(
    planInstall({ host: "openclaw", scope: "project", ...context }).targetRoot,
    path.resolve("/work/project/skills"),
  )
})

test("planInstall honors an explicit target root", () => {
  const plan = planInstall({ targetRoot: "/custom/skills", cwd: "/work", env: {}, homeDir: "/home/user" })
  assert.equal(plan.targetRoot, path.resolve("/custom/skills"))
  assert.equal(plan.destination, path.join(path.resolve("/custom/skills"), "hellosearch"))
})

test("planInstall rejects unsupported hosts and scopes", () => {
  assert.throws(() => planInstall({ host: "unknown" }), /Unsupported host/)
  assert.throws(() => planInstall({ scope: "global" }), /Unsupported scope/)
})

test("detectPreferredHost prefers workspace markers, then home markers, then the cross-vendor default", async () => {
  const workspace = await makeTempDir("hellosearch-ws-")
  const home = await makeTempDir("hellosearch-home-")
  try {
    assert.equal(detectPreferredHost({ cwd: workspace, env: {}, homeDir: home }), "agents")

    await mkdir(path.join(home, ".agents"))
    assert.equal(detectPreferredHost({ cwd: workspace, env: {}, homeDir: home }), "agents")

    await mkdir(path.join(home, ".claude"))
    assert.equal(detectPreferredHost({ cwd: workspace, env: {}, homeDir: home }), "claude-code")

    await mkdir(path.join(workspace, ".openclaw"))
    assert.equal(detectPreferredHost({ cwd: workspace, env: {}, homeDir: home }), "openclaw")
  } finally {
    await rm(workspace, { recursive: true, force: true })
    await rm(home, { recursive: true, force: true })
  }
})

test("detectInstallTargets lists one plan per detected host and falls back to the cross-vendor default", async () => {
  const workspace = await makeTempDir("hellosearch-ws-")
  const home = await makeTempDir("hellosearch-home-")
  try {
    const fallback = detectInstallTargets({ cwd: workspace, env: {}, homeDir: home })
    assert.equal(fallback.length, 1)
    assert.equal(fallback[0].host, "agents")

    await mkdir(path.join(home, ".claude"))
    await mkdir(path.join(home, ".openclaw"))
    const detected = detectInstallTargets({ cwd: workspace, env: {}, homeDir: home })
    assert.deepEqual(
      detected.map((plan) => plan.host).sort(),
      ["claude-code", "openclaw"],
    )
  } finally {
    await rm(workspace, { recursive: true, force: true })
    await rm(home, { recursive: true, force: true })
  }
})

test("installSkill copies the skill payload and respects the force flag", async () => {
  const targetRoot = await makeTempDir("hellosearch-target-")
  try {
    const plan = await installSkill({ targetRoot })
    for (const relative of ["SKILL.md", "references/verification.md", "references/scenarios.md", "references/delivery.md", "evals/evals.json", "LICENSE"]) {
      assert.ok(existsSync(path.join(plan.destination, relative)), `missing ${relative}`)
    }
    assert.ok(!existsSync(path.join(plan.destination, "scripts")), "runtime scripts must not be shipped")

    await assert.rejects(installSkill({ targetRoot }), /already exists/)
    await installSkill({ targetRoot, force: true })
  } finally {
    await rm(targetRoot, { recursive: true, force: true })
  }
})

test("installSkillEverywhere installs into every detected host directory", async () => {
  const workspace = await makeTempDir("hellosearch-ws-")
  const home = await makeTempDir("hellosearch-home-")
  try {
    await mkdir(path.join(home, ".claude"))
    await mkdir(path.join(home, ".agents"))

    const results = await installSkillEverywhere({ cwd: workspace, env: {}, homeDir: home })
    assert.equal(results.length, 2)
    for (const result of results) {
      assert.equal(result.status, "installed")
      assert.ok(existsSync(path.join(result.destination, "SKILL.md")))
    }
  } finally {
    await rm(workspace, { recursive: true, force: true })
    await rm(home, { recursive: true, force: true })
  }
})
