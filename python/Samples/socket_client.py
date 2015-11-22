from ws4py.client.threadedclient import WebSocketClient



class DummyClient(WebSocketClient):
    def opened(self):
        # def data_provider():
        #     for i in range(1, 200, 25):
        #         yield "#" * i

        # self.send(data_provider())

        # for i in range(0, 200, 25):
        #     print i

        self.send(str({
            "hello":"world"            
        }))

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        print m
        if len(m) == 175:
            self.close(reason='Bye bye')

if __name__ == '__main__':
    try:
        ws = DummyClient('ws://localhost:9200/ws', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
