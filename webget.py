import socket
import sys

# 命令行参数
if len(sys.argv) < 3:
    sys.exit(1)

HOST = sys.argv[1]
PATH = sys.argv[2]
PORT = int(sys.argv[3]) if len(sys.argv) >= 4 else 80

# 建立 TCP 连接
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect((HOST, PORT))

# 构造 HTTP 请求
request = ("GET " + PATH + " HTTP/1.1\r\n"
           "Host: " + HOST + "\r\n"
           "Connection: close\r\n"
           "\r\n").encode()
s.sendall(request)

# 循环接收
buf = b""
count = 0
sizes = []

while True:
    chunk = s.recv(4096)
    if not chunk:
        break
    count += 1
    sizes.append(len(chunk))
    buf += chunk

    # 检查是否已收到完整的响应头和 Content-Length 指定的正文
    if b"\r\n\r\n" in buf:
        head = buf.split(b"\r\n\r\n", 1)[0]
        clen = None
        for line in head.split(b"\r\n"):
            if line.lower().startswith(b"content-length:"):
                clen = int(line.split(b":", 1)[1].strip())
        if clen is not None:
            body_len = len(buf) - (buf.find(b"\r\n\r\n") + 4)
            if body_len >= clen:
                break

s.close()

# 打印 T1
print("T1: recv called %d times" % count)
for i, sz in enumerate(sizes, 1):
    print("  recv #%d: %d bytes" % (i, sz))
print("total: %d bytes" % len(buf))

# 拆分状态行、头部、正文
sep = buf.find(b"\r\n\r\n")
head = buf[:sep].decode("iso-8859-1", errors="replace")
body = buf[sep + 4:]

lines = head.split("\r\n")
print("")
print("T2: status  %s" % lines[0].split(" ", 2)[1])
print("status line:", lines[0])
for h in lines[1:]:
    print("  ", h)

# 把收到的正文按原始字节写入文件
with open("body.out", "wb") as f:
    f.write(body)
print("")
print("body saved: body.out (%d bytes, wb mode)" % len(body))
