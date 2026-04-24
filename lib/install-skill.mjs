import os from "node:os"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { cp, mkdir, rm, stat } from "node:fs/promises"

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const skillName = "hellosearch"
const includePaths = ["SKILL.md", "agents", "references", "scripts"]

export function getDefaultTargetRoot() {
  if (process.env.CODEX_HOME) {
    return path.join(process.env.CODEX_HOME, "skills")
  }
  return path.join(os.homedir(), ".codex", "skills")
}

export function getInstallInfo() {
  return {
    packageRoot,
    skillName,
    targetRoot: getDefaultTargetRoot(),
    includePaths,
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

export async function installSkill({ targetRoot = getDefaultTargetRoot(), force = false } = {}) {
  const resolvedTargetRoot = path.resolve(targetRoot)
  const destination = path.join(resolvedTargetRoot, skillName)

  await mkdir(resolvedTargetRoot, { recursive: true })

  if (await pathExists(destination)) {
    if (!force) {
      throw new Error(`Target already exists: ${destination}. Re-run with --force to overwrite.`)
    }
    await rm(destination, { recursive: true, force: true })
  }

  await mkdir(destination, { recursive: true })

  for (const relativePath of includePaths) {
    await cp(
      path.join(packageRoot, relativePath),
      path.join(destination, relativePath),
      { recursive: true, force: true },
    )
  }

  return { destination }
}
