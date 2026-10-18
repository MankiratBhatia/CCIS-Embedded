"""Push simulated sensor readings to Firebase so the dashboard can be tested without hardware.
Usage: python simulate_data.py --url https://YOUR-PROJECT-default-rtdb.firebaseio.com --count 120
"""
import argparse, json, math, random, time, urllib.request

def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=10).status

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="Firebase Realtime DB URL")
    ap.add_argument("--device", default="ccis01")
    ap.add_argument("--count", type=int, default=120)
    ap.add_argument("--interval", type=float, default=15, help="seconds between simulated readings")
    ap.add_argument("--live", action="store_true", help="sleep between posts to mimic real time")
    a = ap.parse_args()
    endpoint = f"{a.url.rstrip('/')}/readings/{a.device}.json"
    t0 = int(time.time() * 1000) - int(a.count * a.interval * 1000)
    for i in range(a.count):
        load_on = (i % 50) < 36
        occupied = (i // 40) % 3 != 2
        power = (110 + random.uniform(-6, 6)) if load_on else 2.0
        row = {
            "ts": t0 + int(i * a.interval * 1000),
            "temp": round(28 + 2 * math.sin(i / 30), 1),
            "hum": round(60 + 5 * math.cos(i / 20), 1),
            "gas_raw": int(1100 + 120 * math.sin(i / 40) + (350 if i % 97 < 4 else 0)),
            "current_a": round(power / 230, 3), "power_w": round(power, 1),
            "occupied": int(occupied), "idle_waste": int(load_on and not occupied), "relay_on": 0,
        }
        print(i, post(endpoint, row))
        if a.live:
            time.sleep(a.interval)

if __name__ == "__main__":
    main()
