import * as hex from '@std/encoding/hex'

import log from './logger.ts'

const encoder = new TextEncoder()

const OUTLINE_WEBHOOK_SIGNING_KEY = Deno.env.get('OUTLINE_WEBHOOK_SIGNING_KEY')
if (!OUTLINE_WEBHOOK_SIGNING_KEY) {
  throw new Error('Must set OUTLINE_WEBHOOK_SIGNING_KEY')
}

const OUTLINE_URL = Deno.env.get('OUTLINE_URL')
if (!OUTLINE_URL) {
  throw new Error('Must set OUTLINE_URL')
}

const OUTLINE_API_TOKEN = Deno.env.get('OUTLINE_API_TOKEN')
if (!OUTLINE_API_TOKEN) {
  throw new Error('Must set OUTLINE_API_TOKEN')
}

const OUTLINE_SIGNING_CRYPTO_KEY = await crypto.subtle.importKey(
  'raw',
  encoder.encode(OUTLINE_WEBHOOK_SIGNING_KEY),
  { name: 'HMAC', hash: 'SHA-256' },
  false,
  ['sign', 'verify'],
)

export async function verifyOutlineSignature(
  outlineSignature: string,
  body: string,
) {
  let timestamp: string | undefined
  let signature: string | undefined

  const [timestampPart, signaturePart] = outlineSignature.split(',')

  if (timestampPart) {
    timestamp = timestampPart.split('=')[1]
  }

  if (signaturePart) {
    signature = signaturePart.split('=')[1]
  }

  if (!timestamp || !signature) {
    throw new Error('Invalid Outline signature')
  }

  const result = await crypto.subtle.verify(
    'HMAC',
    OUTLINE_SIGNING_CRYPTO_KEY,
    hex.decodeHex(signature),
    encoder.encode(`${timestamp}.${body}`),
  )

  if (!result) {
    throw new Error('Invalid Outline signature')
  }

  return true
}

export async function outlineRequest<OutlineResponseData>(
  path: string,
  body?: unknown,
) {
  const url = `${OUTLINE_URL}${path}`

  log.debug(`Outline: Requesting ${url}`)

  const response = await fetch(
    url,
    {
      body: body ? JSON.stringify(body) : '',
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${OUTLINE_API_TOKEN}`,
      },
    },
  )

  if (!response.ok) {
    throw new Error(
      `Outline: Error when requesting ${path}: ${await response.text()}`,
    )
  }

  const json: OutlineApiResponse<OutlineResponseData> = await response.json()

  if (!json.ok) {
    throw new Error(`Outline: Error when requesting ${path}: ${json.error}`)
  }

  log.debug(
    `Outline: Response from ${url}:\n${JSON.stringify(json, undefined, 4)}`,
  )

  return json
}

export interface OutlineWebhookBody<Payload = unknown> {
  /** UUID that represents the delivery attempt */
  id: string
  /** UUID of the user that triggered the event */
  actorId: string
  /** UUID of the specific webhook */
  webhookSubscriptionId: string
  /** Date the event was sent in ISO 8601 */
  createdAt: string
  /** The name of the event, eg. "users.create" */
  event: string
  payload: {
    /** UUID of the model that was mutated */
    id: string
    /** The model attribute contains the properties of the object */
    model: Payload
  }
}

export interface OutlineWebhookPayloadUser {
  id: string
  name: string
  avatarUrl: string | null
  color: string
  isAdmin: boolean
  isSuspended: boolean
  isViewer: boolean
  createdAt: string
  updatedAt: string
  lastActiveAt: string
}

export interface OutlineApiResponse<Data> {
  ok: boolean
  status: number
  error?: string
  data: Data
}

export interface OutlineApiUser {
  id: string
  name: string
  avatarUrl: string | null
  color: string
  isAdmin: boolean
  isSuspended: boolean
  isViewer: boolean
  createdAt: string
  updatedAt: string
  lastActiveAt: string
  email: string
  language: string
  preferences: unknown
  notificationSettings: unknown
}

export interface OutlineApiGroup {
  id: string
  name: string
  memberCount: number
  createdAt: string
  updatedAt: string
}

export interface OutlineApiGroupMembership {
  id: string
  userId: string
  groupId: string
  user: OutlineWebhookPayloadUser
}
