"""Set User-Agent header per spider or use a default value from settings"""
from itertools import cycle

from scrapy import signals


class UserAgentsMiddleware(object):
    """This middleware allows spiders to override the user_agent"""

    def __init__(self, user_agents):
        if isinstance(user_agents, (list, tuple, set)) or user_agents is None:
            self.user_agents = user_agents
            if self.user_agents:
                self.user_agents_cycle = cycle(self.user_agents)
        else:
            raise TypeError('USER_AGENTS should be a list, tuple, or set, or '
                            'None, which get {}'.format(type(user_agents)))

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings['USER_AGENTS'])
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agents = getattr(spider, 'user_agents', self.user_agents)
        if self.user_agents:
            self.user_agents_cycle = cycle(self.user_agents)

    def process_request(self, request, spider):
        if request.headers.get('User-Agent'):
            return
        if self.user_agents:
            request.headers.setdefault(b'User-Agent',
                                       next(self.user_agents_cycle))
