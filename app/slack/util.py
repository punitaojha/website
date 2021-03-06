import enum
import logging
from typing import Any, Dict, List

import requests

logger = logging.getLogger('pyslackers.config.util')


class SlackException(Exception):
    """Exception to wrap any issues specific to Slack's
    ok: false field in their responses vs an HTTP related
    issue. The slack error reason is the text"""


class _SlackMethod(enum.Enum):
    ADMIN_INVITE = 'users.admin.invite'
    CHANNEL_LIST = 'channels.list'
    USER_LIST = 'users.list'

    @property
    def url(self):
        return f'https://slack.com/api/{self.value}'


class SlackClient:
    __slots__ = ('_token', '_session')

    def __init__(self, token: str):
        self._token = token
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
        })

    def invite(self, email: str, channels: List[str], *, resend: bool = True):
        logger.info('Sending slack invite to %s', email)
        r = self._session.post(_SlackMethod.ADMIN_INVITE.url,
                               data={
                                   'token': self._token,
                                   'email': email,
                                   'channels': ','.join(channels),
                                   'resend': resend,
                               })
        r.raise_for_status()
        body = r.json()
        if not body['ok']:
            logger.error('Error sending invite: %s', body)
            raise SlackException(body['error'])
        return body['ok']

    def members(self) -> List[Dict[str, Any]]:
        logger.info('Retrieving user list from slack')
        r = self._session.get(_SlackMethod.USER_LIST.url,
                              params={
                                  'token': self._token,
                                  'presence': True
                              })
        r.raise_for_status()
        body = r.json()
        if not body['ok']:
            logger.error('Unable to retrieve slack user list: %s', body)
            raise SlackException(body['error'])
        return body['members']

    def channels(self, *, exclude_archived: bool = True,
                 exclude_members: bool = True):
        """Gets a list of slack channels for the current instance's
        token.
        :param exclude_archived: Exclude the archived channels
        :param exclude_members: Exclude the members collection"""
        logger.info('Retrieving channel list from slack')
        r = self._session.get(_SlackMethod.CHANNEL_LIST.url,
                              params={
                                  'token': self._token,
                                  'exclude_archived': exclude_archived,
                                  'exclude_members': exclude_members,
                              })
        r.raise_for_status()
        body = r.json()
        if not body['ok']:
            logger.error('Unable to retrieve slack channel list: %s', body)
            raise SlackException(body['error'])
        return body['channels']
