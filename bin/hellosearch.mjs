#!/usr/bin/env node

import process from "node:process"

import { getInstallInfo, installSkill, runDoctor } from "../lib/install-skill.mjs"

function printUsage() {
  console.log(
    [
      "Usage:",
      "  hellosearch install [--host <auto|codex|claude-code|openclaw>] [--scope <user|project>] [--target <path>] [--force]",
      "  hellosearch info [--host <auto|codex|claude-code|openclaw>] [--scope <user|project>] [--target <path>]",
      "  hellosearch doctor [--host <auto|codex|claude-code|openclaw>] [--scope <user|project>] [--target <path>]",
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
    console.log(JSON.stringify(await runDoctor(options), null, 2))
    return
  }

  if (command === "install") {
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
