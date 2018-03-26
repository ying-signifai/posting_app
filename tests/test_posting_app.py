import posting_app
import asyncio
import tornado.concurrent
import tornado.ioloop
import tornado.web
import tornado.platform.asyncio
import tornado.httpclient
import unittest
import tornado.testing
from tornado.options import define, options
from tornado.testing import AsyncHTTPTestCase,AsyncTestCase,AsyncHTTPClient
import urllib
from urllib.parse import urlencode

class TestPostingApp(AsyncHTTPTestCase):
    def get_app(self):
        if not getattr(self, 'application', None):  # if the application is not initialized
            self.application = posting_app.Application()  # initialize the application (application will pull test current IOLoop)
        return self.application

    def tearDown(self):
        self.application.db.close()
        self.application = None  # de-initialize application (so it re-inits on next IOLoop creation)
        super(TestPostingApp, self).tearDown()

    def test_homepage(self):
        post_args = {'message': 'hello'}
        response = self.fetch('/', method='POST', body=urlencode(post_args))
       # self.assertEqual(response.code, 302)
       # self.assertEqual(response.code, 200)
        #self.assertEqual(response.body, 'hello')

def main():
    unittest.main()

if __name__ == '__main__':
    main()

'''import asyncio
import aiohttp


@asyncio.coroutine
def get_status(url):
    code = '000'
    try:
        res = yield from asyncio.wait_for(aiohttp.request('GET', url), 4)
        code = res.status
        res.close()
    except Exception as e:
        print(e)
    print(code)


if __name__ == "__main__":
    urls = ['https://google.com/'] * 100
    coros = [asyncio.Task(get_status(url)) for url in urls]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(coros))
    loop.close()'''