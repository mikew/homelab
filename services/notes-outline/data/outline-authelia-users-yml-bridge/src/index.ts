import type {
  OutlineApiGroup,
  OutlineApiGroupMembership,
  OutlineApiUser,
  OutlineWebhookBody,
  OutlineWebhookPayloadUser,
} from './outline.ts'
import { outlineRequest, verifyOutlineSignature } from './outline.ts'
import log from './logger.ts'
import { getAutheliaUserFromEmail } from './authelia.ts'

Deno.serve(async (request) => {
  try {
    const parsedUrl = new URL(request.url)

    if (parsedUrl.pathname !== '/webhook' || request.method !== 'POST') {
      throw new Error('Must a POST request to /webhook')
    }

    const body = await request.text()
    const outlineWebhookBody: OutlineWebhookBody<OutlineWebhookPayloadUser> =
      JSON.parse(body)

    if (outlineWebhookBody.event !== 'users.signin') {
      throw new Error(
        `Expected Outline webhook of users.signin, received ${outlineWebhookBody.payload}`,
      )
    }

    const signatureHeader = request.headers.get('Outline-Signature')
    if (!signatureHeader) {
      throw new Error('Missing Outline-Signature header')
    }

    await verifyOutlineSignature(signatureHeader, body)

    log.debug('Outline: Signature is valid')

    log.debug(
      `Outline: Formatted webhook request body:\n${
        JSON.stringify(outlineWebhookBody, undefined, 4)
      }`,
    )

    const outlineUserResponse = await outlineRequest<OutlineApiUser>(
      '/api/users.info',
      {
        id: outlineWebhookBody.payload.model.id,
      },
    )

    const autheliaUser = await getAutheliaUserFromEmail(
      outlineUserResponse.data.email,
    )

    if (autheliaUser.groups) {
      const outlineUserGroupsResponse = await outlineRequest<{
        groups: OutlineApiGroup[]
        groupMemberships: OutlineApiGroupMembership[]
      }>(
        '/api/groups.list',
        {
          offset: 0,
          limit: 100,
          userId: outlineUserResponse.data.id,
        },
      )

      const outlineGroupsResponse = await outlineRequest<{
        groups: OutlineApiGroup[]
        groupMemberships: OutlineApiGroupMembership[]
      }>(
        '/api/groups.list',
        {
          offset: 0,
          limit: 100,
        },
      )

      const groupsToCreate = autheliaUser.groups.filter((autheliaUserGroup) =>
        !outlineGroupsResponse.data.groups.find((outlineGroup) =>
          outlineGroup.name === autheliaUserGroup
        )
      )
      const groupsToJoin = autheliaUser.groups.filter((autheliaUserGroup) =>
        !outlineUserGroupsResponse.data.groups.find((outlineGroup) =>
          outlineGroup.name === autheliaUserGroup
        )
      )

      log.info(`Outline: Creating groups: ${groupsToCreate.join(', ')}`)
      log.info(
        `Outline: Adding ${outlineUserResponse.data.name} to: ${
          groupsToJoin.join(', ')
        }`,
      )

      for (const name of groupsToCreate) {
        log.info(`Outline: Creating group ${name}`)
        const { data } = await outlineRequest<OutlineApiGroup>(
          '/api/groups.create',
          { name },
        )
        outlineGroupsResponse.data.groups.push(data)
      }

      for (const name of groupsToJoin) {
        log.info(`Outline: Adding ${outlineUserResponse.data.name} to ${name}`)
        const group = outlineGroupsResponse.data.groups.find((x) =>
          x.name === name
        )
        if (!group) {
          throw new Error('Invalid group: ' + name)
        }
        await outlineRequest('/api/groups.add_user', {
          id: group.id,
          userId: outlineUserResponse.data.id,
        })
      }
    }

    return new Response('', { status: 200 })
  } catch (err) {
    if (err instanceof Error) {
      log.error(`${err.stack}`)
    }

    return buildJsonResponse(
      {
        error: true,
        message: String(err),
      },
      400,
      {},
    )
  }
})

function buildJsonResponse(
  json: unknown,
  status: number,
  headers: Record<string, string>,
) {
  return new Response(
    JSON.stringify(json),
    {
      status,
      headers: {
        'content-type': 'application/json',
        ...headers,
      },
    },
  )
}
