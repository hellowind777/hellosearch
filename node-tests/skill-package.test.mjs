import test from "node:test"
import assert from "node:assert/strict"
import { existsSync } from "node:fs"
import { readFile } from "node:fs/promises"
import path from "node:path"
import { fileURLToPath } from "node:url"

import { parseFrontmatter, validateSkillPackage } from "../lib/install-skill.mjs"

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")

test("the packaged skill passes every validation check", async () => {
  const result = await validateSkillPackage(packageRoot)
  const failed = result.checks.filter((check) => !check.passed)
  assert.ok(result.ok, `failed checks: ${JSON.stringify(failed, null, 2)}`)
})

test("SKILL.md frontmatter satisfies the Agent Skills specification", async () => {
  const text = await readFile(path.join(packageRoot, "SKILL.md"), "utf8")
  const frontmatter = parseFrontmatter(text)

  assert.ok(frontmatter, "frontmatter must parse")
  assert.equal(frontmatter.name, "hellosearch", "name must match the skill directory name")
  assert.ok(frontmatter.description.length > 0 && frontmatter.description.length <= 1024)
  assert.match(frontmatter.description, /hellosearch/, "description should include the invocation keyword")
  assert.match(frontmatter.description, /Do not use/, "description should state explicit non-triggers")
})

test("SKILL.md stays within the recommended size and references only files that exist", async () => {
  const text = await readFile(path.join(packageRoot, "SKILL.md"), "utf8")
  assert.ok(text.split("\n").length <= 500, "SKILL.md must stay under 500 lines")

  const referenced = new Set([...text.matchAll(/references\/[a-z0-9-]+\.md/g)].map((match) => match[0]))
  assert.ok(referenced.size >= 3, "SKILL.md should point to the reference files")
  for (const relative of referenced) {
    assert.ok(existsSync(path.join(packageRoot, relative)), `missing ${relative}`)
  }
})

test("behavior evals follow the expected schema", async () => {
  const evals = JSON.parse(await readFile(path.join(packageRoot, "evals", "evals.json"), "utf8"))
  assert.equal(evals.skill_name, "hellosearch")
  assert.ok(Array.isArray(evals.evals) && evals.evals.length >= 5)
  for (const entry of evals.evals) {
    assert.ok(Number.isInteger(entry.id))
    assert.ok(entry.prompt.length > 0)
    assert.ok(entry.expected_output.length > 0)
    assert.ok(Array.isArray(entry.expectations) && entry.expectations.length >= 3)
  }
})

test("trigger evals cover both positive and negative cases", async () => {
  const triggers = JSON.parse(await readFile(path.join(packageRoot, "evals", "triggers.json"), "utf8"))
  assert.ok(Array.isArray(triggers) && triggers.length >= 16)
  for (const entry of triggers) {
    assert.ok(typeof entry.query === "string" && entry.query.length > 0)
    assert.ok(typeof entry.should_trigger === "boolean")
  }
  const positive = triggers.filter((entry) => entry.should_trigger).length
  const negative = triggers.length - positive
  assert.ok(positive >= 8, `need at least 8 should-trigger cases, found ${positive}`)
  assert.ok(negative >= 8, `need at least 8 should-not-trigger cases, found ${negative}`)
})

test("package.json ships the skill payload and no Python tooling", async () => {
  const pkg = JSON.parse(await readFile(path.join(packageRoot, "package.json"), "utf8"))
  for (const required of ["SKILL.md", "agents", "references", "evals", "bin", "lib"]) {
    assert.ok(pkg.files.includes(required), `package.json files must include ${required}`)
  }
  assert.ok(pkg.engines && pkg.engines.node, "engines.node must be declared")
  assert.ok(!/python/i.test(JSON.stringify(pkg.scripts)), "npm scripts must not depend on Python")
})

test("legacy runtime directories are gone", () => {
  assert.ok(!existsSync(path.join(packageRoot, "scripts")), "scripts/ must not exist")
  assert.ok(!existsSync(path.join(packageRoot, "tests")), "tests/ must not exist")
})
