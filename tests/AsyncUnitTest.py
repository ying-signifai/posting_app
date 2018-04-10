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

    @asyncio.coroutine
    def tearDown(self):
        self.application.rabbitmq.close()
        self.application.redis.close()
        #self.application.redis.wait_closed()
        self.application.db.close()
        #self.application.db.wait_closed()
        self.application = None  # de-initialize application (so it re-inits on next IOLoop creation)
        super(TestPostingApp, self).tearDown()

    def test_homepage(self):
        post_args = {'message': 'hello'}
        #response = self.http_client.fetch('/', self.stop, method='POST', body=urlencode(post_args))
        response = self.fetch('/', method='POST', body=urlencode(post_args))
       # self.assertEqual(response.code, 302)
       # self.assertEqual(response.code, 200)
        #self.assertEqual(response.body, 'hello')

def main():
    unittest.main()

if __name__ == '__main__':
    main()