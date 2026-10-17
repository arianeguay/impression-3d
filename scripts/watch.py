#!/usr/bin/env python3
"""Watch a running print unattended: camera checks judged by `claude -p`, cancel on spaghetti.

usage: watch.py <the .gcode that was uploaded> [--notify CMD]

Meant to run on an always-on host (apollon) so a long print is watched without a laptop. Every
3 minutes for the first 15, then every 10, it takes a camera frame and asks Claude whether the
parts are failing. A failure verdict is confirmed on a second frame a minute later before the job
is cancelled, since a wrong cancel throws away hours of a good print. Exits when the printer
leaves the printing state. `--notify` is a command given `--title T --message M`, e.g. apollon's
pushover-notify.sh; without it, messages go to stdout only.
"""
import argparse, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import printer  # noqa: E402
import where  # noqa: E402

# apollon runs on UTC; the log is read against Montreal wall-clock time.
os.environ["TZ"] = "America/Toronto"
time.tzset()

PROMPT = """You are watching a 3D print through a camera. Read the image at {image}.
The printer is {status}, {progress} through the file, printing part "{part}" at {z} mm of height.
Parts on this plate: {parts}. A failing print shows loose strands or tangled filament
("spaghetti"), a part lying on its side, or a part clearly shorter than the height above.
A thin straight strand along the front edge of the plate is the purge line, and one long thin
strand across the plate at the start is ooze: neither is a failure. The printhead can hide parts.
Answer with one JSON object and nothing else:
{{"verdict": "ok" | "failure" | "unsure", "reason": "<one short sentence>"}}"""


def notify(cmd, title, message):
    print(f"[{time.strftime('%H:%M')}] {title}: {message}", flush=True)
    if cmd:
        subprocess.run(cmd.split() + ["--title", title, "--message", message], check=False)


def judge(gcode, parts, d):
    image = f"/tmp/watch-{os.getpid()}.jpg"
    printer.snapshot(image)
    part, z, _ = where.where(gcode, d["printProgress"])
    prompt = PROMPT.format(image=image, status=d["status"], progress=f"{d['printProgress']:.0%}",
                           part=part, z=z, parts=", ".join(parts))
    out = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read"],
                         capture_output=True, text=True, timeout=300).stdout
    m = re.search(r"\{.*\}", out, re.S)
    return (json.loads(m.group(0)) if m else {"verdict": "unsure", "reason": out.strip()[:200]}), part, z


def main():
    a = argparse.ArgumentParser()
    a.add_argument("gcode")
    a.add_argument("--notify")
    o = a.parse_args()
    parts = sorted(set(re.findall(r"^; printing object (\S+)", open(o.gcode).read(), re.M)))
    start = time.time()
    notify(o.notify, "Print watch", f"watching {os.path.basename(o.gcode)}: {', '.join(parts)}")
    misses = 0
    while True:
        try:
            d = printer.http("/detail")["detail"]
            misses = 0
        except OSError as e:  # the printer drops off Wi-Fi for seconds at a time
            misses += 1
            if misses == 5:
                notify(o.notify, "Print watch: printer unreachable", str(e)[:200])
            time.sleep(60)
            continue
        if d["status"] not in ("printing", "pausing", "paused"):
            notify(o.notify, "Print ended", f"status {d['status']}, {d['printProgress']:.0%} of the file")
            return
        try:
            v, part, z = judge(o.gcode, parts, d)
        except Exception as e:  # a failed check must not end the watch
            notify(o.notify, "Print watch: check failed", str(e)[:300])
            v, part, z = {"verdict": "unsure"}, None, None
        print(f"[{time.strftime('%H:%M')}] {part} z={z}: {v}", flush=True)
        if v["verdict"] == "failure":
            time.sleep(60)
            v2, part, z = judge(o.gcode, parts, printer.http("/detail")["detail"])
            if v2["verdict"] == "failure":
                printer.job("cancel")
                notify(o.notify, "Print CANCELLED: spaghetti",
                       f"{part} at {z} mm. {v['reason']} / {v2['reason']}")
                return
            notify(o.notify, "Print watch: false alarm", f"{v['reason']} / then: {v2['reason']}")
        time.sleep(180 if time.time() - start < 900 else 600)


if __name__ == "__main__":
    main()
