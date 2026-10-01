#!/usr/bin/env python3
"""Drive the Flashforge Adventurer 5M over the LAN.

usage: printer.py status | list | upload <file.gcode> [name] | start <name>
                  | pause | resume | cancel | clear-platform | snapshot <out.jpg>

Two channels, each doing what the other cannot:
- TCP 8899 legacy protocol, no credentials: upload, start, status, file list.
- HTTP 8898 API, needs the check code: detailed status and clear-platform, which is the only
  remote way out of BUILDING_COMPLETED.
The camera is MJPEG on 8080. Credentials live in ~/.config/impression-3d/printer.env.
"""
import json, os, socket, subprocess, sys, time, urllib.request

ENV = os.path.expanduser("~/.config/impression-3d/printer.env")


def _config():
    cfg = {"AD5M_HOST": "192.168.0.199", "AD5M_SERIAL": "", "AD5M_CHECK_CODE": ""}
    if os.path.exists(ENV):
        for line in open(ENV):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                cfg[k] = v
    cfg.update({k: os.environ[k] for k in cfg if k in os.environ})
    for k, v in cfg.items():
        if v.startswith("op://"):
            cfg[k] = subprocess.run(["op", "read", v], check=True, capture_output=True, text=True).stdout.strip()
    return cfg


CFG = _config()
HOST = CFG["AD5M_HOST"]


class Printer:
    def __init__(self):
        self.s = socket.create_connection((HOST, 8899), timeout=20)
        self.cmd("~M601 S1")

    def read(self, timeout=3.0, until=b"ok"):
        self.s.settimeout(timeout)
        out = b""
        try:
            while until not in out:
                d = self.s.recv(65536)
                if not d:
                    break
                out += d
        except socket.timeout:
            pass
        return out

    def cmd(self, c, timeout=3.0):
        self.s.sendall((c + "\r\n").encode())
        return self.read(timeout).decode(errors="replace").strip().replace("\r\n", " | ")

    def close(self):
        self.s.sendall(b"~M602\r\n")
        self.s.close()


def legacy(fn):
    p = Printer()
    try:
        return fn(p)
    finally:
        p.close()


def http(path, payload=None):
    body = {"serialNumber": CFG["AD5M_SERIAL"], "checkCode": CFG["AD5M_CHECK_CODE"]}
    if payload:
        body["payload"] = payload
    req = urllib.request.Request(f"http://{HOST}:8898{path}", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    out = json.load(urllib.request.urlopen(req, timeout=10))
    if out.get("code") != 0:
        raise RuntimeError(f"printer HTTP API refused {path}: {out.get('message')}")
    return out


def status():
    lines = legacy(lambda p: [p.cmd(c) for c in ("~M119", "~M105", "~M27")])
    try:
        d = http("/detail")["detail"]
        lines.append(json.dumps({k: d.get(k) for k in (
            "status", "printFileName", "printProgress", "printLayer", "targetPrintLayer",
            "estimatedTime", "rightTemp", "platTemp")}))
    except Exception as e:  # the legacy lines already answer; the API adds detail
        lines.append(f"(HTTP detail unavailable: {e})")
    return "\n".join(lines)


def files():
    def run(p):
        p.s.sendall(b"~M661\r\n")
        time.sleep(1.5)
        raw = p.read(3, until=b"\x00\x00\x00\x00\x00\x00")
        return [part[part.index(b"/data/"):].decode(errors="replace")
                for part in raw.split(b"::") if b"/data/" in part]
    return legacy(run)


def upload(path, name=None):
    data = open(path, "rb").read()
    name = name or os.path.basename(path)

    def run(p):
        out = [p.cmd(f"~M28 {len(data)} 0:/user/{name}")]
        for i in range(0, len(data), 4096):
            p.s.sendall(data[i:i + 4096])
        time.sleep(3)
        out.append(p.cmd("~M29", 15))
        return " | ".join(out)
    return legacy(run)


def start(name):
    def run(p):
        state = p.cmd("~M119")
        if "MachineStatus: READY" not in state:
            raise RuntimeError("printer is not READY; a finished job needs clear-platform first "
                               f"(and an empty bed): {state}")
        return p.cmd(f"~M23 0:/user/{name}")
    return legacy(run)


def job(action):
    code = {"pause": "~M25", "resume": "~M24", "cancel": "~M26"}[action]
    return legacy(lambda p: p.cmd(code))


def clear_platform():
    http("/control", {"cmd": "stateCtrl_cmd", "args": {"action": "setClearPlatform"}})
    time.sleep(2)
    return legacy(lambda p: p.cmd("~M119"))


def snapshot(out_path):
    s = urllib.request.urlopen(f"http://{HOST}:8080/?action=stream", timeout=10)
    buf = b""
    while True:
        chunk = s.read(65536)
        if not chunk:
            raise RuntimeError("camera stream ended before a full frame")
        buf += chunk
        a = buf.find(b"\xff\xd8")
        b = buf.find(b"\xff\xd9", a + 2) if a >= 0 else -1
        if b > 0:
            break
    open(out_path, "wb").write(buf[a:b + 2])
    return out_path


def main(argv):
    if not argv:
        sys.exit(__doc__)
    op, args = argv[0], argv[1:]
    try:
        if op == "status":
            print(status())
        elif op == "list":
            print("\n".join(files()))
        elif op == "upload":
            print(upload(*args))
        elif op == "start":
            print(start(args[0]))
        elif op in ("pause", "resume", "cancel"):
            print(job(op))
        elif op == "clear-platform":
            print(clear_platform())
        elif op == "snapshot":
            print(snapshot(args[0]))
        else:
            sys.exit(__doc__)
    except RuntimeError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main(sys.argv[1:])
