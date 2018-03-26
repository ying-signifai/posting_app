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
#import executor
#import concurrent.futures
#from concurrent.futures import ThreadPoolExecutor

define("internal_port", default=3301, help="the given internal port", type=int)
define("mysql_host", default="127.0.0.1", help="database host")
define("mysql_database", default="mysql", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="pw", help="blog database password")
define("port", default=8080, help="run on the external port")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', WebHandler)
        ]
        super(Application, self).__init__(handlers) # important
        asyncio.get_event_loop().run_until_complete(self.create_tb())
        loop = asyncio.get_event_loop()
        self.db = loop.run_until_complete(self.connect_db())
        self.logger = structlog.get_logger()


    async def connect_db(self):
        return await aiomysql.connect(host=options.mysql_host, port=options.internal_port,
                                      user=options.mysql_user, password=options.mysql_password,
                                      db=options.mysql_database)

    async def create_tb(self):
        conn = await self.connect_db()
        cur = await conn.cursor()
        async with conn.cursor() as cur:
            await cur.execute("DROP TABLE IF EXISTS msg_tb4;")
            await cur.execute("""CREATE TABLE msg_tb4
                                      (msg_id INT,
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
    async def post(self):
        msg = self.get_argument('message')
        self.application.logger.msg("get input msg to post", msg=msg)
        conn = self.application.db
        cur = await conn.cursor()
        id = await cur.execute("SELECT * from msg_tb4")
        self.application.logger.msg("get id for msg from query db", id=id, msg=msg)
        if id > 0:
            messages = await cur.fetchall()
            for col in messages:
                self.write(str(col[0]) + "." + col[1] + '\r\n') # not io involved
        await cur.execute("INSERT INTO msg_tb4 VALUES(%s, %s)", (id, msg))
       # self.application.logger.msg("Execution of insertion to db completed before commit", id=id, msg=msg)
        await conn.commit()
        self.application.logger.msg("Execution of insertion to db completed after commit", id=id, msg=msg)
        self.write(str(id) + "." + msg)
        #conn.close()


def main():
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application()
    app.listen(options.port)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()