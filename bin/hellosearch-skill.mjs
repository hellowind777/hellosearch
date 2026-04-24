#!/usr/bin/env node

import process from "node:process"

import { getInstallInfo, installSkill } from "../lib/install-skill.mjs"

function printUsage() {
  console.log(
    [
      "Usage:",
      "  hellosearch-skill install [--target <path>] [--force]",
      "  hellosearch-skill info",
    ].join("\n"),
  )
}

function parseInstallArgs(argv) {
  let targetRoot
  let force = false

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === "--target") {
      targetRoot = argv[index + 1]
      index += 1
      continue
    }
    if (arg === "--force") {
      force = true
      continue
    }
    throw new Error(`Unknown argument: ${arg}`)
  }

  return { targetRoot, force }
}

async function main() {
  const [command, ...args] = process.argv.slice(2)

  if (!command || command === "--help" || command === "-h") {
    printUsage()
    return
  }

  if (command === "info") {
    console.log(JSON.stringify(getInstallInfo(), null, 2))
    return
  }

  if (command === "install") {
    const options = parseInstallArgs(args)
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
