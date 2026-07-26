#!/usr/bin/env node

import process from "node:process"

import { getInstallInfo, installSkill, installSkillEverywhere, runDoctor } from "../lib/install-skill.mjs"

function printUsage() {
  console.log(
    [
      "Usage:",
      "  hellosearch install [--host <auto|claude-code|codex|agents|openclaw|all>] [--scope <user|project>] [--target <path>] [--force]",
      "  hellosearch info    [--host <host>] [--scope <scope>] [--target <path>]",
      "  hellosearch doctor  [--host <host>] [--scope <scope>] [--target <path>]",
      "",
      "Hosts:",
      "  auto         Detect the most likely host from the workspace and home directory (default).",
      "  claude-code  Install to .claude/skills (project) or ~/.claude/skills (user).",
      "  codex        Install to .agents/skills (project) or ~/.agents/skills (user).",
      "  agents       Same cross-vendor location as codex; also read by OpenClaw and Gemini CLI.",
      "  openclaw     Install to <workspace>/skills (project) or ~/.openclaw/skills (user).",
      "  all          Install to every host detected on this machine (install command only).",
    ].join("\n"),
  )
}

function parseSharedArgs(argv) {
  const options = {
    host: "auto",
    scope: "user",
  }

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === "--target") {
      options.targetRoot = argv[index + 1]
      index += 1
      continue
    }
    if (arg === "--host") {
      options.host = argv[index + 1]
      index += 1
      continue
    }
    if (arg === "--scope") {
      options.scope = argv[index + 1]
      index += 1
      continue
    }
    if (arg === "--force") {
      options.force = true
      continue
    }
    throw new Error(`Unknown argument: ${arg}`)
  }

  return options
}

async function main() {
  const [command, ...args] = process.argv.slice(2)

  if (!command || command === "--help" || command === "-h") {
    printUsage()
    return
  }

  const options = parseSharedArgs(args)

  if (command === "info") {
    console.log(JSON.stringify(getInstallInfo(options), null, 2))
    return
  }

  if (command === "doctor") {
    const report = await runDoctor(options)
    console.log(JSON.stringify(report, null, 2))
    if (!report.validation.ok) {
      process.exitCode = 1
    }
    return
  }

  if (command === "install") {
    if (options.host === "all") {
      const results = await installSkillEverywhere({ force: options.force })
      for (const result of results) {
        if (result.status === "installed") {
          console.log(`Installed hellosearch skill to: ${result.destination}`)
        } else {
          console.error(`Failed for ${result.destination}: ${result.error}`)
          process.exitCode = 1
        }
      }
      return
    }
    const result = await installSkill(options)
    console.log(`Installed hellosearch skill to: ${result.destination}`)
    return
  }

  throw new Error(`Unknown command: ${command}`)
}

main().catch((error) => {
  console.error(error.message || String(error))
  process.exitCode = 1
})
