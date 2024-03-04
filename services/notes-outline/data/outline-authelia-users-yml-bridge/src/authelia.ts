import { parse } from '@std/yaml'

const AUTHELIA_USERS_FILE = Deno.env.get('AUTHELIA_USERS_FILE')
if (!AUTHELIA_USERS_FILE) {
  throw new Error('Must set AUTHELIA_USERS_FILE')
}

export async function getAutheliaUserFromEmail(email: string) {
  const { users } = await getAutheliaUsers()
  let foundUser: AutheliaUser | undefined

  for (const userName in users) {
    if (users[userName]?.email === email) {
      foundUser = users[userName]
    }
  }

  if (!foundUser) {
    throw new Error(
      `Authelia: Could not find user with email ${email}`,
    )
  }

  return foundUser
}

async function getAutheliaUsers() {
  const parsed = parse(
    await getUsersYaml(),
  )

  if (!isAutheliaParsedUsersYml(parsed)) {
    throw new Error('Authelia: Could not load users')
  }

  return parsed
}

function isAutheliaParsedUsersYml(obj: unknown): obj is AutheliaParsedUsersYml {
  if (obj && typeof obj === 'object' && 'users' in obj) {
    return true
  }

  return false
}

function getUsersYaml() {
  return Deno.readTextFile(AUTHELIA_USERS_FILE)
}

export interface AutheliaUser {
  disabled: boolean
  displayName: string
  email: string
  groups?: string[]
  // Intentionally left out because it shouldn't be used.
  // password: string
}

export interface AutheliaParsedUsersYml {
  users: {
    [userName: string]: AutheliaUser
  }
}
