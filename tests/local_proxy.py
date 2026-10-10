import socket, threading, sys, select, time
LOG=open(sys.argv[2],"a",buffering=1)
def log(m): LOG.write(f"{time.strftime('%H:%M:%S')} {m}\n")
def pipe(a,b):
    socks=[a,b]
    try:
        while True:
            r,_,_=select.select(socks,[],[],30)
            if not r: break
            for s in r:
                d=s.recv(65536)
                if not d: return
                (b if s is a else a).sendall(d)
    except OSError: pass
def handle(c,addr):
    try:
        data=b""
        while b"\r\n\r\n" not in data:
            ch=c.recv(65536)
            if not ch: return
            data+=ch
        line=data.split(b"\r\n",1)[0].decode("latin1")
        log(f"{addr[0]}:{addr[1]} REQ {line!r}")
        method,target,_=line.split(" ",2)
        if method=="CONNECT":
            h,p=target.rsplit(":",1)
            u=socket.create_connection((h,int(p)),10)
            c.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            log(f"TUNNEL OPEN {target}")
            pipe(c,u); log(f"TUNNEL CLOSED {target}")
        else:
            from urllib.parse import urlsplit
            s=urlsplit(target)
            if not s.hostname:
                log("REJECT non-absolute target"); c.sendall(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n"); return
            u=socket.create_connection((s.hostname,s.port or 80),10)
            path=(s.path or "/")+("?"+s.query if s.query else "")
            rest=data.split(b"\r\n",1)[1]
            u.sendall(f"{method} {path} HTTP/1.1\r\n".encode()+rest)
            log(f"FORWARD {method} {target}"); pipe(c,u)
    except Exception as e: log(f"ERR {e!r}")
    finally: c.close()
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind(("127.0.0.1",int(sys.argv[1]))); s.listen(50)
port=s.getsockname()[1]
log(f"listening {port}")
while True:
    c,a=s.accept(); threading.Thread(target=handle,args=(c,a),daemon=True).start()
