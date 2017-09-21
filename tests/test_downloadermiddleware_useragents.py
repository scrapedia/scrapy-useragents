from unittest import TestCase

from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.utils.test import get_crawler

from scrapy_useragents.downloadermiddlewares.useragents import \
    UserAgentsMiddleware


class UserAgentsMiddlewareTest(TestCase):
    def get_spider_and_mw(self, default_useragents):
        crawler = get_crawler(spidercls=Spider,
                              settings_dict={'USER_AGENTS': default_useragents})
        spider = crawler._create_spider('foo')
        return spider, UserAgentsMiddleware.from_crawler(crawler)

    def test_default_agent(self):
        default_useragents = ['default_useragent_1', 'default_useragent_2']
        spider, mw = self.get_spider_and_mw(default_useragents)

        mw.spider_opened(spider)

        for useragent in default_useragents:
            req = Request('http://scrapytest.org/')
            assert mw.process_request(req, spider) is None
            self.assertEqual(req.headers['User-Agent'], useragent.encode())

    def test_remove_agent(self):
        default_useragents = ['default_useragent_1', 'default_useragent_2']
        spider, mw = self.get_spider_and_mw(default_useragents)

        # settings UESR_AGENT to None should remove the user agent
        spider.user_agents = None
        mw.spider_opened(spider)

        for useragent in default_useragents:
            req = Request('http://scrapytest.org/')
            assert mw.process_request(req, spider) is None
            assert req.headers.get('User-Agent') is None

    def test_spider_agent(self):
        default_useragents = ['default_useragent_1', 'default_useragent_2']
        spider, mw = self.get_spider_and_mw(default_useragents)

        spider.user_agents = ['spider_useragent_1',
                              'spider_useragent_2']
        mw.spider_opened(spider)

        for useragent in spider.user_agents:
            req = Request('http://scrapytest.org/')
            assert mw.process_request(req, spider) is None
            self.assertEqual(req.headers['User-Agent'], useragent.encode())

    def test_header_agent(self):
        default_useragents = ['default_useragent_1', 'default_useragent_2']
        spider, mw = self.get_spider_and_mw(default_useragents)

        spider.user_agents = ['spider_useragent_1', 'spider_useragent_2']
        mw.spider_opened(spider)

        for useragent in spider.user_agents:
            req = Request('http://scrapytest.org/',
                          headers={'User-Agent': 'header_useragent'})
            assert mw.process_request(req, spider) is None
            self.assertEqual(req.headers['User-Agent'], b'header_useragent')

    def test_no_agent(self):
        spider, mw = self.get_spider_and_mw(None)

        spider.user_agents = None
        mw.spider_opened(spider)

        req = Request('http://scrapytest.org/')
        assert mw.process_request(req, spider) is None
        assert 'User-Agent' not in req.headers
