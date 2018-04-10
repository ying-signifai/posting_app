import asyncio
import aioamqp
import aiohttp


class QueueReceiver():
    async def callback(self, channel, body, envelope, properties):
        print(" [x] Received %r" % body)
        async with aiohttp.ClientSession() as session:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            id, msg = body.decode('ascii').split('#')
            async with session.put('http://localhost:9200/posts/msg/%s' % id, data='{"message":"%s"}'% msg, headers = headers) as resp:
                assert 1 == 1
                   # resp.url == 'http://localhost:9200/?key=value2&key=value1'
                #print(resp.status)
            #print(await resp.text())


    async def receive(self):
        transport, protocol = await aioamqp.connect()
        channel = await protocol.channel()
        await channel.queue_declare(queue_name='msg_queue')
        await channel.basic_consume(self.callback, queue_name='msg_queue')



def main():
    receiver = QueueReceiver()
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(receiver.receive())
    event_loop.run_forever()

if __name__ == '__main__':
    main()



