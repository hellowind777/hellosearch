import os from "node:os"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { existsSync } from "node:fs"
import { cp, mkdir, rm, stat } from "node:fs/promises"

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const skillName = "hellosearch"
const includePaths = ["SKILL.md", "agents", "references", "scripts", "LICENSE"]
const supportedHosts = ["auto", "codex", "claude-code", "openclaw"]
const supportedScopes = ["user", "project"]

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
  if (existsSync(path.join(workspaceRoot, ".openclaw"))) {
    return "openclaw"
  }
  if (existsSync(path.join(workspaceRoot, ".codex"))) {
    return "codex"
  }
  if (env.CODEX_HOME || existsSync(path.join(homeDir, ".codex"))) {
    return "codex"
  }
  if (existsSync(path.join(homeDir, ".claude"))) {
    return "claude-code"
  }
  if (existsSync(path.join(homeDir, ".openclaw"))) {
    return "openclaw"
  }
  return "codex"
}

function resolvePresetTargetRoot(host, scope, { cwd, env, homeDir }) {
  if (host === "codex") {
    if (scope === "project") {
      return path.join(cwd, ".codex", "skills")
    }
    if (env.CODEX_HOME) {
      return path.join(env.CODEX_HOME, "skills")
    }
    return path.join(homeDir, ".codex", "skills")
  }
  if (host === "claude-code") {
    return scope === "project"
      ? path.join(cwd, ".claude", "skills")
      : path.join(homeDir, ".claude", "skills")
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
    targetRoot || resolvePresetTargetRoot(resolvedHost, scope, { cwd: resolvedCwd, env, homeDir }),
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

export function getInstallInfo(options = {}) {
  return planInstall(options)
}

export async function runDoctor(options = {}) {
  const plan = planInstall(options)
  const checks = await Promise.all(
    plan.includePaths.map(async (relativePath) => ({
      path: relativePath,
      exists: await pathExists(path.join(plan.packageRoot, relativePath)),
    })),
  )

  return {
    ...plan,
    destinationExists: await pathExists(plan.destination),
    checks,
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
  for (const relativePath of plan.includePaths) {
    await cp(
      path.join(plan.packageRoot, relativePath),
      path.join(plan.destination, relativePath),
      { recursive: true, force: true },
    )
  }

  return plan
}
