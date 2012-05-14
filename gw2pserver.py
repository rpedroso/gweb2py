import os
import sys
import bdb
import linecache
import thread
import threading
import Queue

from wsgiref.simple_server import make_server, WSGIRequestHandler


ALLOW_GLUON = False
DEBUG_ENABLED = False
SERV = True

#toggle_input_ev = threading.Event()

q = Queue.Queue()


def STDERR(t):
    sys.stderr.write("%s\n" % t)


def DBG(w, t=''):
    sys.stdout.write("DBG:%s:%s\n" % (w, t))


def WSOUT(w, t=''):
    sys.stdout.write("WSOUT:%s:%d:%s\n" % (w, len(t), t))


def in_user_code(fn, line):
    #print 'fn:', fn
    #if not fn.endswith('.py'):
    #    return False
    line = line.strip()
    if not line:
        return False
    if line.startswith('@') \
            or line.startswith('def ') or line.startswith('class '):
        return False
    if '%sapplications%s' % (os.sep, os.sep) in fn:
        if '%sapplications%sadmin%s' % (os.sep, os.sep, os.sep) in fn:
            return False
        return True
    if ALLOW_GLUON and '%sgluon%s' % (os.sep, os.sep) in fn:
        return True

    return False


class Tracer(bdb.Bdb):

    def __init__(self):
        bdb.Bdb.__init__(self)

        if not hasattr(bdb.Bdb, 'set_until'):
            self.set_until = self.set_next
        #self.until = self.set_until

    # normalize method signature with the others set_'s
    def set_trace(self, frame=None):
        bdb.Bdb.set_trace(self)

    def set_step(self, frame=None):
        bdb.Bdb.set_step(self)

    def set_continue(self, frame=None):
        bdb.Bdb.set_continue(self)

    def set_break(self, frame, (filename, lineno)):
        bdb.Bdb.set_break(self, filename, int(lineno))
        return True

    def clear_break(self, frame, (filename, lineno)):
        bdb.Bdb.clear_break(self, filename, int(lineno))
        return True

    def user_line(self, frame):
        #print 'user_line'
        if not DEBUG_ENABLED:
            return
        fn = self.canonic(frame.f_code.co_filename)
        line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        if in_user_code(fn, line):
            #print getattr(self, "currentbp", False)
            DBG("STEP", "%s|%s|%s" % (fn, frame.f_lineno, 'line'))
            while True:
                keep_loop = self.wait_command(frame)
                if not keep_loop:
                    break
            #self.__wakeup_debug.wait()

    def process_pending_commands(self):
        global q
        while q.unfinished_tasks > 0:
            command = q.get()
            frame = sys._getframe().f_back
            self.process_command(command, frame)

    def wait_command(self, frame):
        global q
        #command = raw_input('> ') #self.q.get()
        #STDERR('waiting command')
        command = q.get()
        return self.process_command(command, frame)

    def process_command(self, command, frame):
        global q
        #STDERR('process command %s'% command)
        parts = command.split()
        if len(parts) > 1:
            command = parts[0]
            command = 'pprint' if command == 'print' else command
            args = parts[1:]
            #STDERR("frame: %s, args: %s" % (repr(frame), repr(args)))
            keep_loop = getattr(self, command)(frame, args)
        else:
            keep_loop = getattr(self, command)(frame)
        q.task_done()
        return keep_loop

    def _getval(self, frame, arg):
        try:
            return eval(arg, frame.f_globals, frame.f_locals)
        except:
            t, v = sys.exc_info()[:2]
            if isinstance(t, str):
                exc_type_name = t
            else:
                exc_type_name = t.__name__
            return exc_type_name + ':', repr(v)

    def pprint(self, frame, args):
        #STDERR(args)
        for arg in args:
            t = repr(self._getval(frame, arg.strip()))
            DBG("RES", "%d:%s" % (len(t), t))
        return True


tracer = Tracer()


class RequestHandler(WSGIRequestHandler):

    def __init__(self, *args, **kwargs):
        global tracer
        global q
        self._response_headers = []
        #print DEBUG_ENABLED
        #self.http_version = "1.1"
        DBG("START")
        #STDERR("START: debug_enable=%s"%DEBUG_ENABLED)
        if DEBUG_ENABLED:
            #STDERR("bps: %s" % tracer.get_all_breaks())
            if tracer.get_all_breaks():
                q.put('set_continue')
            tracer.set_trace()
            tracer.process_pending_commands()
            #STDERR("bps: %s" % tracer.get_all_breaks())
            #STDERR("%d" % q.unfinished_tasks)
        else:
            # Debug is not enable and there are no breakpoints
            # continue without debugger overhead
            #STDERR(repr(tracer.get_all_breaks()))
            sys.settrace(None)
        WSGIRequestHandler.__init__(self, *args, **kwargs)
        #STDOUT("aqui")
        #print self.requestline
        #print self.headers
        try:
            WSOUT('REQUEST_HEADERS', '%s\n%s\n%s' % (
                '-' * 20, self.requestline, self.headers))
        except AttributeError:
            pass
        DBG("STOP")

    def log_request(self, code='-', size='-'):
        WSOUT('LOG', '%s %s %s' % (self.requestline, str(code), str(size)))


def _toggle_command(i_queue, d_queue):
    global DEBUG_ENABLED
    global ALLOW_GLUON
    global SERV
    global srv
    while True:
        #STDOUT('>')
        command = raw_input()
        if command == 'toggle_debug':
            DEBUG_ENABLED = not DEBUG_ENABLED
        elif command == 'toggle_gluon':
            ALLOW_GLUON = not ALLOW_GLUON
        elif command.startswith('SH:'):
            i_queue.put(command[3:])
        elif command == '__quit__':
            SERV = False
            #if hasattr(srv, 'shutdown'):
            #    sys.stderr.write('shutting down\n')
            #    srv.shutdown()
            #else:
            #    sys.stderr.write('closing\n')
            #    srv.server_close()
        else:
            d_queue.put(command)


class TraceResponseHeaderMiddleware(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        # Do something here to modify request

        # Call the wrapped application
        app_iter = self.application(environ,
                                    self._sr_callback(start_response))

        # Do something to modify the response body

        # Return modified response
        return app_iter

    def _sr_callback(self, start_response):

        def callback(status, headers, exc_info=None):
            # Do something to modify the response status or headers
            pass

            # Call upstream start_response
            start_response(status, headers, exc_info)
            out = []
            for k, v in headers:
                out.append("%s: %s" % (k, v))
            h = "%s" % '\n'.join(out)
            WSOUT('RESPONSE_HEADERS', '%s\n%s\n%s\n' % ('-' * 20, status, h))
        return callback


def _interpreter(i_queue, d_queue):
    while True:
        command = i_queue.get()
        command = command.strip()
        if command:
            d_queue.put('print %s' % command)


def run(port):
    global q
    global srv
    import gluon.main
    from gluon.settings import global_settings
    global_settings.web2py_crontype = 'soft'

    queue_interpreter = Queue.Queue()
    thread.start_new_thread(_toggle_command, (queue_interpreter, q))
    thread.start_new_thread(_interpreter, (queue_interpreter, q))

    app = TraceResponseHeaderMiddleware(gluon.main.wsgibase)
    try:
        1 / 0
        import eventlet
        from eventlet import wsgi
        WSOUT('Using eventlet')
        wsgi.server(eventlet.listen(('', port)), app)
    except Exception, e:
        #print e
        srv = make_server('', port, app, handler_class=RequestHandler)
        WSOUT('Using wsgiref')
        while SERV:
            srv.handle_request()


if __name__ == '__main__':
    WEB2PY_SRC = sys.argv[2]
    os.chdir(WEB2PY_SRC)
    sys.path.insert(0, WEB2PY_SRC)

    port = int(sys.argv[1])
    WSOUT('STATUS', 'webserver running on port %d' % port)
    run(port)
    WSOUT('STATUS', 'webserver stopped')
