import os from "node:os"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { existsSync } from "node:fs"
import { cp, mkdir, readFile, rm, stat } from "node:fs/promises"

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const skillName = "hellosearch"
const includePaths = ["SKILL.md", "agents", "references", "evals", "LICENSE"]
const supportedHosts = ["auto", "claude-code", "codex", "agents", "openclaw"]
const supportedScopes = ["user", "project"]
const maxDescriptionLength = 1024
const maxSkillLines = 500

function assertSupported(value, supported, field) {
  if (!supported.includes(value)) {
    throw new Error(`Unsupported ${field}: ${value}. Expected one of: ${supported.join(", ")}`)
  }
}

async function pathExists(targetPath) {
  try {
    await stat(targetPath)
    return true
  } catch {
    return false
  }
}

export function detectPreferredHost({ cwd = process.cwd(), env = process.env, homeDir = os.homedir() } = {}) {
  const workspaceRoot = path.resolve(cwd)
  if (existsSync(path.join(workspaceRoot, ".claude"))) {
    return "claude-code"
  }
  if (existsSync(path.join(workspaceRoot, ".agents"))) {
    return "agents"
  }
  if (existsSync(path.join(workspaceRoot, ".openclaw"))) {
    return "openclaw"
  }
  if (existsSync(path.join(workspaceRoot, ".codex"))) {
    return "codex"
  }
  if (existsSync(path.join(homeDir, ".claude"))) {
    return "claude-code"
  }
  if (existsSync(path.join(homeDir, ".agents"))) {
    return "agents"
  }
  if (env.CODEX_HOME || existsSync(path.join(homeDir, ".codex"))) {
    return "codex"
  }
  if (existsSync(path.join(homeDir, ".openclaw"))) {
    return "openclaw"
  }
  // `.agents/skills` is the cross-vendor default location, so it is the safest fallback.
  return "agents"
}

function resolvePresetTargetRoot(host, scope, { cwd, homeDir }) {
  if (host === "claude-code") {
    return scope === "project"
      ? path.join(cwd, ".claude", "skills")
      : path.join(homeDir, ".claude", "skills")
  }
  if (host === "codex" || host === "agents") {
    // Codex discovers skills in `.agents/skills` (workspace) and `~/.agents/skills` (user),
    // the same cross-vendor location used by OpenClaw and Gemini CLI.
    return scope === "project"
      ? path.join(cwd, ".agents", "skills")
      : path.join(homeDir, ".agents", "skills")
  }
  if (host === "openclaw") {
    return scope === "project"
      ? path.join(cwd, "skills")
      : path.join(homeDir, ".openclaw", "skills")
  }
  throw new Error(`Unsupported host preset: ${host}`)
}

export function planInstall({
  host = "auto",
  scope = "user",
  targetRoot,
  cwd = process.cwd(),
  env = process.env,
  homeDir = os.homedir(),
} = {}) {
  assertSupported(host, supportedHosts, "host")
  assertSupported(scope, supportedScopes, "scope")

  const resolvedCwd = path.resolve(cwd)
  const resolvedHost = host === "auto" ? detectPreferredHost({ cwd: resolvedCwd, env, homeDir }) : host
  const resolvedTargetRoot = path.resolve(
    targetRoot || resolvePresetTargetRoot(resolvedHost, scope, { cwd: resolvedCwd, homeDir }),
  )
  const destination = path.join(resolvedTargetRoot, skillName)

  return {
    packageRoot,
    skillName,
    includePaths,
    supportedHosts,
    supportedScopes,
    cwd: resolvedCwd,
    host: resolvedHost,
    requestedHost: host,
    scope,
    targetRoot: resolvedTargetRoot,
    destination,
  }
}

export function detectInstallTargets({ cwd = process.cwd(), env = process.env, homeDir = os.homedir() } = {}) {
  const candidates = []
  if (existsSync(path.join(homeDir, ".claude"))) {
    candidates.push("claude-code")
  }
  if (
    existsSync(path.join(homeDir, ".agents")) ||
    existsSync(path.join(homeDir, ".codex")) ||
    env.CODEX_HOME
  ) {
    candidates.push("agents")
  }
  if (existsSync(path.join(homeDir, ".openclaw"))) {
    candidates.push("openclaw")
  }
  if (candidates.length === 0) {
    candidates.push("agents")
  }

  const plans = []
  const seenRoots = new Set()
  for (const host of candidates) {
    const plan = planInstall({ host, scope: "user", cwd, env, homeDir })
    if (seenRoots.has(plan.targetRoot)) {
      continue
    }
    seenRoots.add(plan.targetRoot)
    plans.push(plan)
  }
  return plans
}

export function getInstallInfo(options = {}) {
  return planInstall(options)
}

export function parseFrontmatter(markdown) {
  if (!markdown.startsWith("---")) {
    return null
  }
  const end = markdown.indexOf("\n---", 3)
  if (end === -1) {
    return null
  }
  const block = markdown.slice(markdown.indexOf("\n") + 1, end)
  const fields = {}
  for (const line of block.split("\n")) {
    if (!line.trim() || /^\s/.test(line)) {
      continue
    }
    const separator = line.indexOf(":")
    if (separator === -1) {
      continue
    }
    fields[line.slice(0, separator).trim()] = line.slice(separator + 1).trim()
  }
  return fields
}

export async function validateSkillPackage(root = packageRoot) {
  const checks = []
  const add = (id, passed, detail) => checks.push({ id, passed, detail })

  const skillPath = path.join(root, "SKILL.md")
  const skillExists = await pathExists(skillPath)
  add("skill-file-exists", skillExists, skillPath)

  if (skillExists) {
    const text = await readFile(skillPath, "utf8")
    const frontmatter = parseFrontmatter(text)

    add("frontmatter-parses", frontmatter !== null, "SKILL.md must start with a YAML frontmatter block")
    if (frontmatter) {
      add(
        "frontmatter-name-matches",
        frontmatter.name === skillName,
        `name is "${frontmatter.name}", expected "${skillName}"`,
      )
      const description = frontmatter.description || ""
      add(
        "description-length",
        description.length > 0 && description.length <= maxDescriptionLength,
        `description length is ${description.length} (limit ${maxDescriptionLength})`,
      )
    }

    const lineCount = text.split("\n").length
    add("skill-line-count", lineCount <= maxSkillLines, `SKILL.md has ${lineCount} lines (limit ${maxSkillLines})`)

    const referenced = [...text.matchAll(/references\/[a-z0-9-]+\.md/g)].map((match) => match[0])
    for (const relative of new Set(referenced)) {
      add(`reference-exists:${relative}`, await pathExists(path.join(root, relative)), relative)
    }
  }

  for (const relative of includePaths) {
    add(`package-path-exists:${relative}`, await pathExists(path.join(root, relative)), relative)
  }

  for (const relative of ["evals/evals.json", "evals/triggers.json"]) {
    const filePath = path.join(root, relative)
    if (!(await pathExists(filePath))) {
      add(`eval-file-valid:${relative}`, false, "file is missing")
      continue
    }
    try {
      JSON.parse(await readFile(filePath, "utf8"))
      add(`eval-file-valid:${relative}`, true, relative)
    } catch (error) {
      add(`eval-file-valid:${relative}`, false, `invalid JSON: ${error.message}`)
    }
  }

  return {
    ok: checks.every((check) => check.passed),
    checks,
  }
}

export async function runDoctor(options = {}) {
  const plan = planInstall(options)
  const validation = await validateSkillPackage(plan.packageRoot)

  return {
    ...plan,
    destinationExists: await pathExists(plan.destination),
    validation,
  }
}

export async function installSkill({
  host = "auto",
  scope = "user",
  targetRoot,
  force = false,
  cwd = process.cwd(),
  env = process.env,
  homeDir = os.homedir(),
} = {}) {
  const plan = planInstall({ host, scope, targetRoot, cwd, env, homeDir })

  await mkdir(plan.targetRoot, { recursive: true })
  if (await pathExists(plan.destination)) {
    if (!force) {
      throw new Error(`Target already exists: ${plan.destination}. Re-run with --force to overwrite.`)
    }
    await rm(plan.destination, { recursive: true, force: true })
  }

  await mkdir(plan.destination, { recursive: true })
  for (const relative of plan.includePaths) {
    await cp(path.join(plan.packageRoot, relative), path.join(plan.destination, relative), {
      recursive: true,
      force: true,
    })
  }

  return plan
}

export async function installSkillEverywhere({
  force = false,
  cwd = process.cwd(),
  env = process.env,
  homeDir = os.homedir(),
} = {}) {
  const results = []
  for (const plan of detectInstallTargets({ cwd, env, homeDir })) {
    try {
      const installed = await installSkill({
        host: plan.host,
        scope: plan.scope,
        force,
        cwd,
        env,
        homeDir,
      })
      results.push({ ...installed, status: "installed" })
    } catch (error) {
      results.push({ ...plan, status: "failed", error: error.message })
    }
  }
  return results
}
