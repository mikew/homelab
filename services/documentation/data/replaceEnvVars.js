const fs = require('fs')

function main(args) {
  const inputPath = args[2]

  process.stdout.write(replaceEnvVars(fs.readFileSync(inputPath, 'utf8')))
}

function replaceEnvVars(input) {
  return input
    .replace(/\{\{(.+?)\}\}/g, (match, envVarName) => {
      if (envVarName === 'HOMELAB_USER_GUIDES') {
        return replaceEnvVars(process.env.HOMELAB_USER_GUIDES)
      }

      return process.env[envVarName] ?? match
    })
}

main(process.argv)
