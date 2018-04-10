import asyncio
import tornado.concurrent
import tornado.ioloop
import tornado.web
import tornado.platform.asyncio
import tornado.httpclient
import uvloop
import aiomysql
import structlog
from tornado.options import define, options
import aioredis
import aioamqp
import aiohttp
from aioamqp_receive import QueueReceiver
#import numpy as np

from pyformance.meters import Counter, Histogram, Meter, Timer
from pyformance import timer, time_calls
from pyformance.registry import MetricsRegistry
#from pyformance.reporters import HostedGraphiteReporter


define("internal_port", default=3301, help="mysql internal port", type=int)
define("redis_address", default='redis://localhost:6377', help="redis internal port", type=int)
#define("redis_host", default="127.0.0.1", help="redis host")
define("local_host", default="127.0.0.1", help="database host")
define("mysql_database", default="mysql", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="pw", help="blog database password")
define("port", default=8082, help="run on the external port")
define("amqp_port", default=5672, help="run on the amqp port to activeMQ")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', WebHandler)
        ]
        super(Application, self).__init__(handlers) # important
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tb())
        self.logger = structlog.get_logger()
        self.db = loop.run_until_complete(self.connect_db())
        self.redis = loop.run_until_complete(self.connect_redis())
        self.rabbitmq = loop.run_until_complete(self.connect_rabbitmq())

    async def connect_rabbitmq(self):
        transport, protocol = await aioamqp.connect()
        channel = await protocol.channel()
        await channel.queue_declare(queue_name='msg_queue')
        return channel

    async def connect_redis(self):
        return await aioredis.create_redis_pool(
            options.redis_address
        )

    async def connect_db(self):
        return await aiomysql.create_pool(host=options.local_host, port=options.internal_port,
                                      user=options.mysql_user, password=options.mysql_password,
                                      db=options.mysql_database)


    async def create_tb(self):
        conn = await aiomysql.connect(host=options.local_host, port=options.internal_port,
                                      user=options.mysql_user, password=options.mysql_password,
                                      db=options.mysql_database)
        cur = await conn.cursor()
        async with conn.cursor() as cur:
            await cur.execute("DROP TABLE IF EXISTS msg_tb4;")
            await cur.execute("""CREATE TABLE msg_tb4
                                      (msg_id INT AUTO_INCREMENT,
                                      msg VARCHAR(255),
                                      PRIMARY KEY (msg_id));""")
            await conn.commit()
           # self.application.logger.msg("Execution of create table msg_tb4 completed")
            conn.close()

class WebHandler(tornado.web.RequestHandler):
    async def get(self):
        form = """<form method="post">
        <input type="text" name="message"/>
        <input type="submit"/>
        </form>"""
        self.write(form)
    #@time_calls

    async def post(self):
        #timer = metricsRegistry.timer("post_calls")
        #histogram = metricsRegistry.histogram("pos_calls");
        #histogram.add(timer)
        msg = self.get_argument('message')
        channel = self.application.rabbitmq
        '''self.application.logger.msg("before publish to channel", msg=msg)
        await channel.basic_publish(
            payload=msg,
            exchange_name='',
            routing_key='msg_queue'
        )'''
        self.application.logger.msg("Get input msg to post", msg=msg)
        pool = self.application.db
        async with pool.acquire() as conn:
            with timer("test").time():
                async with conn.cursor() as cur:
                    await cur.execute("INSERT INTO msg_tb4 (msg) VALUES(%s)", (msg))
                    await cur.execute("SELECT LAST_INSERT_ID()")
                    id_row = await cur.fetchone()
                    id = id_row[0]
                    await conn.commit() # commit might come after msg_cnt
                    self.application.logger.msg("Execution of insertion to db completed after commit", id =id, msg=msg)
                    self.application.logger.msg(str(timer("test").get_mean()))
                    self.application.logger.msg("before publish to channel", id=id, msg=msg)
                    await channel.basic_publish(
                        payload=str(id) + '#' + msg,
                        exchange_name='',
                        routing_key='msg_queue'
                    )
                    msg_cnt = await cur.execute("SELECT * from msg_tb4")
                    self.application.logger.msg("Msg count:", msg_cnt = msg_cnt)
                    res = [None] * msg_cnt
                    for i in range(msg_cnt):
                        tmp = await self.application.redis.get(i+1)
                        if tmp is not None:
                            res[i] = tmp.decode('utf-8')
                            self.application.logger.msg("Read message from redis", msg_id = i+1, msg = res[i])
                        else:
                            await cur.execute("SELECT * from msg_tb4 WHERE msg_id = %s", i+1)
                            tmp = await cur.fetchone()
                            res[i] = tmp[1]
                            await self.application.redis.set(i+1, str(res[i]))
                            self.application.logger.msg("Read message from mysql", msg_id = i+1, msg = res[i])
                    for i in range(msg_cnt):
                        self.write(str(i+1) + "." + res[i] + '\n')

       # self.application.logger.msg(str(metricsRegistry._get_timer_metrics("post_calls")))
        #conn.close()

def main():
    global metricsRegistry
    metricsRegistry = MetricsRegistry()
    #timer = metricsRegistry.timer("post_calls")
    #print((str(metricsRegistry._get_timer_metrics("post_calls"))))
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application()
    app.listen(options.port)
    asyncio.get_event_loop().run_forever()
    #print((str(metricsRegistry._get_timer_metrics("post_calls"))))


if __name__ == '__main__':
    main()