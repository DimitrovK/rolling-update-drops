import http.server, os, signal, socket, sys, threading, time
MODE = os.environ.get("SHUTDOWN_MODE", "immediate")
HOST = socket.gethostname()
draining = threading.Event()
def log(m): print(f"{time.time():.3f} {HOST} {m}", flush=True)
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"          # keep-alive, like a real client
    def do_GET(self):
        if self.path == "/healthz":
            body = b"draining" if draining.is_set() else b"ok"
            code = 503 if draining.is_set() else 200
        else:
            body, code = HOST.encode(), 200
        self.send_response(code)
        self.send_header("Content-Type","text/plain")
        self.send_header("Content-Length",str(len(body)))
        if draining.is_set() and MODE == "drain_conns":
            # tell the client to stop reusing this connection, then close it
            self.send_header("Connection","close")
            self.close_connection = True
        self.end_headers(); self.wfile.write(body)
    def log_message(self,*a): pass
srv = http.server.ThreadingHTTPServer(("",8080), H)
srv.daemon_threads = True
def on_term(signum, frame):
    log("SIGTERM received")
    draining.set()
    if MODE == "immediate":
        log("exiting immediately"); os._exit(0)
    if MODE == "drain_conns":
        # keep serving, but close every keep-alive as it is used, so the
        # pool empties instead of being severed when we exit
        time.sleep(12)
        threading.Thread(target=srv.shutdown, daemon=True).start()
        time.sleep(1)
        log("drained exit"); os._exit(0)
    # graceful: stop accepting, let in-flight finish, then go
    threading.Thread(target=srv.shutdown, daemon=True).start()
    time.sleep(3)
    log("graceful exit"); os._exit(0)
signal.signal(signal.SIGTERM, on_term)
log(f"serving, mode={MODE}")
srv.serve_forever()
