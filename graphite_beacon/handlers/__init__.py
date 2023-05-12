from tornado import log

from .. import _compat as _
from ..template import TEMPLATES

LOGGER = log.gen_log


class HandlerMeta(type):

    loaded = {}
    handlers = {}

    def __new__(mcs, name, bases, params):
        cls = super(HandlerMeta, mcs).__new__(mcs, name, bases, params)
        if name := params.get('name'):
            mcs.handlers[name] = cls
            LOGGER.info(f"Register Handler: {name}")
        return cls

    @classmethod
    def clean(cls):
        cls.loaded = {}

    @classmethod
    def get(cls, reactor, name):
        if name not in cls.loaded:
            cls.loaded[name] = cls.handlers[name](reactor)
        return cls.loaded[name]


class AbstractHandler(_.with_metaclass(HandlerMeta)):

    name = None
    defaults = {}

    def __init__(self, reactor):
        self.reactor = reactor
        self.options = dict(self.defaults)
        self.options |= self.reactor.options.get(self.name, {})
        self.init_handler()
        LOGGER.debug('Handler "%s" has inited: %s', self.name, self.options)

    def get_short(self, level, alert, value, target=None, ntype=None, rule=None):
        tmpl = TEMPLATES[ntype]['short']
        return tmpl.generate(
            level=level, reactor=self.reactor, alert=alert, value=value, target=target).strip()

    def init_handler(self):
        """ Init configuration here."""
        raise NotImplementedError()

    def notify(self, level, alert, value, target=None, ntype=None, rule=None):
        raise NotImplementedError()

registry = HandlerMeta

from .hipchat import HipChatHandler    # noqa
from .http import HttpHandler          # noqa
from .log import LogHandler            # noqa
from .slack import SlackHandler        # noqa
from .smtp import SMTPHandler          # noqa
from .cli import CliHandler            # noqa
from .opsgenie import OpsgenieHandler  # noqa
