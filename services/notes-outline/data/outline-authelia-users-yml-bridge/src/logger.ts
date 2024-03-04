import * as log from '@std/log'

const DENO_LOG_LEVEL_ENV = Deno.env.get('DENO_LOG_LEVEL') || 'INFO'

if (
  DENO_LOG_LEVEL_ENV !== 'DEBUG' && DENO_LOG_LEVEL_ENV !== 'INFO' &&
  DENO_LOG_LEVEL_ENV !== 'WARN' && DENO_LOG_LEVEL_ENV !== 'ERROR'
) {
  throw new Error(`Invalid DENO_LOG_LEVEL: ${DENO_LOG_LEVEL_ENV}`)
}

const DENO_LOG_LEVEL = DENO_LOG_LEVEL_ENV

log.setup({
  handlers: {
    console: new log.ConsoleHandler(DENO_LOG_LEVEL),
  },
  loggers: {
    default: {
      level: DENO_LOG_LEVEL,
      handlers: ['console'],
    },
  },
})

export default log
