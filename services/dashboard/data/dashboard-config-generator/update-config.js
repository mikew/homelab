#!/usr/bin/env node

const spec = require('./spec')
const yaml = require('yaml')
const fs = require('fs/promises')

async function main() {
  const previousConfigStr = await fs.readFile('/output/config.yml', 'utf-8')
  const previousConfig = yaml.parse(previousConfigStr)
  previousConfig.subtitle = process.env.HOMELAB_HOST_NAME

  spec.sort((a, b) => {
    return a.name.localeCompare(b.name)
  })

  for (const service of spec) {
    service.items.sort((a, b) => {
      return a.name.localeCompare(b.name)
    })
  }

  previousConfig.services = spec

  const newConfigStr = yaml.stringify(previousConfig)

  await fs.writeFile('/output/config.yml', newConfigStr, 'utf-8')
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(err)
    process.exit(1)
  })
