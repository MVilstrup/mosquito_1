# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket
import zmq


class BaseSink(object):

    def __init__(self,
                 result_port,
                 send_port,
                 break_port="tcp://127.0.0.1:9999"):

        context = zmq.Context()

        # Socket to receive messages on
        self.receive_socket = context.socket(zmq.PULL)
        self.receive_socket.bind(result_port)

        # Socket to reschedule domains that timed out
        self.send_socket = context.socket(zmq.PUSH)
        self.send_socket.bind(send_port)

        # Socket to reschedule domains that timed out
        self.break_socket = context.socket(zmq.SUB)
        self.break_socket.bind(break_port)

        # Poller used to switch between the two sockets
        poller = zmq.Poller()
        poller.register(self.receive_socket, zmq.POLLIN)
        poller.register(self.break_socket, zmq.POLLIN)

    def start(self):
        should_continue = True
        while should_continue:
            sockets = dict(poller.poll())
            if self.receive_socket in sockets and sockets[
                    self.receive_socket] == zmq.POLLIN:
                message = self.receive_socket.recv_json()
                self._handle_messages(message)

            if self.break_socket in sockets and sockets[
                    self.break_socket] == zmq.POLLIN:
                signal = self.break_socket.recv_string()
                if signal == "QUIT":
                    should_continue = False
                    return

    def _handle_messages(self, message):
        raise NotImplementedError("_work should be implemented")

    def send_json(self, message):
        return self.send_socket.send_json(message)

    def send_string(self, message):
        return self.send_socket.send_string(message)

    def send(self, message):
        return self.send_socket.send(message)
