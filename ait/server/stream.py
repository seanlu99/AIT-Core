import gevent
import gevent.socket
import gevent.server as gs
import gevent.monkey; gevent.monkey.patch_all()

import zmq.green as zmq

import ait
from ait.core import log
from client import Client


class Stream(Client):

    def __init__(self, name, input_, handlers, zmq_args=None):
        self.name = name
        self.input_ = input_
        self.handlers = handlers

        if not self.valid_workflow():
            raise ValueError('Sequential workflow inputs and outputs ' +
                             'are not compatible. Workflow is invalid.')

        super(Stream, self).__init__(zmq_args)

    @property
    def type(self):
        try:
            if self in ait.broker.inbound_streams:
                return 'Inbound Stream'
            elif self in ait.broker.outbound_streams:
                return 'Outbound Stream'
            else:
                log.warn('Stream %s not registered with broker.' % self.name)
                raise(Exception)
        except Exception:
            return 'Stream'

    def __repr__(self):
        return '<Stream name=%s>' % (self.name)

    def process(self, input_data, topic=None):
        log.info('in stream handling data')
        for handler in self.handlers:
            output = handler.execute_handler(input_data)
            input_data = output
        self.publish(input_data)

    def valid_workflow(self):
        """
        Return true if each handler's output type is the same as
        the next handler's input type. Return False if not.
        """
        for ix, handler in enumerate(self.handlers[:-1]):
            next_input_type = self.handlers[ix + 1].input_type

            if (handler.output_type is not None and
                    next_input_type is not None):
                if handler.output_type != next_input_type:
                    return False

        return True

class InputPortStream(gs.DatagramServer):
    def __init__ (self, listener, name, input_, handlers, zmq_args=None):
        log.info("init InputPortStream")
        super(InputPortStream, self).__init__(listener)
        self.name = name
        self.input_ = input_
        self.handlers = handlers

        # if not self.valid_workflow():
            # raise ValueError('Sequential workflow inputs and outputs ' +
                             # 'are not compatible. Workflow is invalid.')

        if zmq_args is None:
            zmq_args = {'context': ait.broker.context,
                        'XSUB_URL': ait.broker.XSUB_URL,
                        'XPUB_URL': ait.broker.XPUB_URL}

        self.context = zmq_args['context']
        # open PUB and SUB socket
        self.pub = self.context.socket(zmq.PUB)
        # self.sub = self.context.socket(zmq.SUB)
        self.sub = gevent.socket.socket(gevent.socket.AF_INET, gevent.socket.SOCK_DGRAM)
        # connect to broker
        # self.sub.connect(zmq_args['XPUB_URL'].replace('*', 'localhost'))
        self.pub.connect(zmq_args['XSUB_URL'].replace('*', 'localhost'))

    def start (self):
        super(InputPortStream, self).start()

    def handle (self, packet, address):
        topic, messagedata = packet.split()
        log.info('%s %s recieved message \"%s\" from %s'
                 % (self.type, self.name, messagedata, topic))
        log.info('received data in Client, passing to process')
        self.process(messagedata, topic=topic)

    def publish(self, msg):
        """
        Publish specified message with client name as topic.
        """
        self.pub.send("%s %s" % (self.name, msg))
        log.info('Published message %s from %s %s'
                   % (msg, self.type, self.name))

    def process(self, input_data, topic=None):
        log.info('in stream handling data')
        for handler in self.handlers:
            output = handler.execute_handler(input_data)
            input_data = output
        self.publish(input_data)

    def valid_workflow(self):
        """
        Return true if each handler's output type is the same as
        the next handler's input type. Return False if not.
        """
        for ix, handler in enumerate(self.handlers[:-1]):
            next_input_type = self.handlers[ix + 1].input_type

            if (handler.output_type is not None and
                    next_input_type is not None):
                if handler.output_type != next_input_type:
                    return False

        return True
