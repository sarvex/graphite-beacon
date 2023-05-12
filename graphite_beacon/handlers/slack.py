import json
from tornado import gen, httpclient as hc

from . import AbstractHandler, LOGGER


class SlackHandler(AbstractHandler):

    name = 'slack'

    # Default options
    defaults = {
        'webhook': None,
        'channel': None,
        'username': 'graphite-beacon',
    }

    emoji = {
        'critical': ':exclamation:',
        'warning': ':warning:',
        'normal': ':white_check_mark:',
    }

    def init_handler(self):
        self.webhook = self.options.get('webhook')
        assert self.webhook, 'Slack webhook is not defined.'

        self.channel = self.options.get('channel')
        if self.channel and not self.channel.startswith('#'):
            self.channel = f'#{self.channel}'
        self.username = self.options.get('username')
        self.client = hc.AsyncHTTPClient()

    @gen.coroutine
    def notify(self, level, *args, **kwargs):
        LOGGER.debug("Handler (%s) %s", self.name, level)

        message = self.get_short(level, *args, **kwargs)
        data = {
            'username': self.username,
            'text': message,
            'icon_emoji': self.emoji.get(level, ':warning:'),
        }
        if self.channel:
            data['channel'] = self.channel

        body = json.dumps(data)
        yield self.client.fetch(self.webhook, method='POST', body=body)
