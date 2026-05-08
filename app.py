import os
import asyncio
import threading
import configparser
from flask import Flask, render_template, request, jsonify, session
from androidtvremote2 import AndroidTVRemote

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')
ACCESS_PASSWORD = config.get('DEFAULT', 'password', fallback='123456')
DEFAULT_IP = config.get('DEFAULT', 'default_ip', fallback='192.168.1.200')

CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
remotes = {}

async_loop = asyncio.new_event_loop()
def run_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
threading.Thread(target=run_async_loop, args=(async_loop,), daemon=True).start()

def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, async_loop).result()

@app.before_request
def check_login():
    if request.path in ['/login', '/static/favicon.ico'] or request.path.startswith('/static/'):
        return
    if 'authenticated' not in session and request.path != '/':
        return jsonify({"error": "unauthorized"}), 401

@app.route('/')
def index():
    if 'authenticated' not in session:
        return render_template('login.html')
    return render_template('index.html', default_ip=DEFAULT_IP)

@app.route('/login', methods=['POST'])
def login():
    password = request.json.get('password')
    if password == ACCESS_PASSWORD:
        session['authenticated'] = True
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"}), 403

@app.route('/connect', methods=['POST'])
def connect():
    host = request.json.get('host')
    async def do_connect():
        remote = AndroidTVRemote("PythonRemote", CERT_FILE, KEY_FILE, host, loop=async_loop)
        await remote.async_generate_cert_if_missing()
        try:
            await remote.async_connect()
            remotes[host] = remote
            return True
        except Exception:
            return False
    success = run_async(do_connect())
    return jsonify({"status": "connected" if success else "pairing_required"})

@app.route('/start_pairing', methods=['POST'])
def start_pairing():
    host = request.json.get('host')
    async def do_start():
        remote = AndroidTVRemote("PythonRemote", CERT_FILE, KEY_FILE, host, loop=async_loop)
        await remote.async_generate_cert_if_missing()
        await remote.async_start_pairing()
        remotes[host] = remote
    run_async(do_start())
    return jsonify({"status": "pairing_started"})

@app.route('/finish_pairing', methods=['POST'])
def finish_pairing():
    host = request.json.get('host')
    code = request.json.get('code')
    remote = remotes.get(host)
    async def do_finish():
        await remote.async_finish_pairing(code)
        await remote.async_connect()
    run_async(do_finish())
    return jsonify({"status": "success"})

@app.route('/command', methods=['POST'])
def command():
    host = request.json.get('host')
    key = int(request.json.get('key'))
    direction = request.json.get('direction', 'SHORT')
    remote = remotes.get(host)
    if remote:
        # Map START/STOP from frontend to START_LONG/END_LONG in protocol
        proto_direction = direction
        if direction == "START": proto_direction = "START_LONG"
        if direction == "STOP": proto_direction = "END_LONG"
        
        remote.send_key_command(key, proto_direction)
    return jsonify({"status": "ok"})

@app.route('/send_text', methods=['POST'])
def send_text():
    host = request.json.get('host')
    text = request.json.get('text')
    remote = remotes.get(host)
    if remote: remote.send_text(text)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
