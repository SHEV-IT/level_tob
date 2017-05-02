# coding: utf-8
from helpers.abstract import BotFather
import constants as c

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from Queue import Queue
import threading
import cgi
import simplejson
import ssl
import logging

import projects


def make_handler_with_queue(msg_queue):
    class HTTPRequestHandler(BaseHTTPRequestHandler):
        queue = msg_queue

        def do_POST(self):
            logging.info(self.path)

            if c.CALLBACK_PATH != self.path:
                self.reply_not_found()
                return

            try:
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                length = int(self.headers.getheader('content-length'))
                data = self.rfile.read(length)
                data = simplejson.loads(data)
                group_id = data['group_id']
            except:
                # bad request
                self.reply_code_msg(400, '')
                return

            if group_id not in c.VK_PROJECTS:
                # unknown group
                self.reply_not_found()
                return

            request_type = data.get('type', 'kek')
            group_data = c.VK_PROJECTS[group_id]
            name = group_data['name']

            if request_type == 'confirmation' and c.CONFIRMATION_ENABLED:
                logging.info('got confirmation request for %s' % name)
                self.reply_ok(group_data['confirm'])
            elif data['secret'] == group_data['token']:
                logging.info('got vk request %s for %s' % (request_type, name))
                self.queue[group_id].put({'from': 'vk', 'event': data})
                self.reply_ok()
            else:
                logging.info('wrong secret in request for %s' % name)
                self.reply_not_found()

        def reply_code_msg(self, code, msg=None):
            self.send_response(code)
            self.end_headers()
            if msg is not None:
                self.wfile.write(msg)

        def reply_not_found(self, msg=''):
            self.reply_code_msg(404, msg)

        def reply_ok(self, msg='ok'):
            self.reply_code_msg(200, msg)

        def log_message(self, format, *args):
            return

    return HTTPRequestHandler


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer():
    def __init__(self, ip, port, queue):
        self.server = ThreadedHTTPServer((ip, port), make_handler_with_queue(queue))
        if not c.DEBUG:
            self.server.socket = ssl.wrap_socket(self.server.socket,
                                                 keyfile=c.HTTPS_KEY,
                                                 certfile=c.HTTPS_CERT, server_side=True)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.server.socket.close()
        self.waitForThread()


class VkBot(BotFather):
    def __init__(self, token=None):
        super(VkBot, self).__init__(token)
        # /callkek -> bot queue
        self.queue = dict()
        self.bots = []
        for project_id in c.VK_PROJECTS:
            project_name = c.VK_PROJECTS[project_id]['name']
            print 'starting', project_name
            queue = Queue()
            bot_instance = projects.modules[project_name](queue=queue)
            bot_thread = threading.Thread(target=bot_instance.worker, name='bot_thread_%s' % project_name)
            bot_thread.start()
            self.bots.append(bot_instance)
            self.queue[project_id] = queue
        self.server = SimpleHttpServer('0.0.0.0', 443 if not c.DEBUG else 80, queue=self.queue)

    def run(self):
        logging.info('HTTP Server Running...........')
        self.server.start()

    def stop(self):
        for bot in self.bots:
            bot.stop = True
        for queue in self.queue.values():
            queue.put({'from': 'vk', 'event': 'stop'})
        self.server.stop()
