import os
import asyncio
import threading
from flask import Flask, render_template, request, jsonify
from androidtvremote2 import AndroidTVRemote

app = Flask(__name__)

# Storage for certificates and active remotes
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
remotes = {}  # host -> AndroidTVRemote object

# Global event loop running in a background thread
async_loop = asyncio.new_event_loop()

def run_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=run_async_loop, args=(async_loop,), daemon=True).start()

def run_async(coro):
    future = asyncio.run_coroutine_threadsafe(coro, async_loop)
    return future.result()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    host = request.json.get('host')
    if not host:
        return jsonify({"error": "Missing host"}), 400
    
    async def do_connect():
        if host in remotes:
            try:
                await remotes[host].async_connect()
                return True
            except Exception:
                pass
        
        remote = AndroidTVRemote("PythonRemote", CERT_FILE, KEY_FILE, host, loop=async_loop)
        await remote.async_generate_cert_if_missing()
        try:
            await remote.async_connect()
            remotes[host] = remote
            return True
        except Exception as e:
            print(f"Connect error: {e}")
            return False

    success = run_async(do_connect())
    if success:
        return jsonify({"status": "connected"})
    else:
        return jsonify({"status": "pairing_required"})

@app.route('/start_pairing', methods=['POST'])
def start_pairing():
    host = request.json.get('host')
    if not host:
        return jsonify({"error": "Missing host"}), 400

    async def do_start_pairing():
        remote = AndroidTVRemote("PythonRemote", CERT_FILE, KEY_FILE, host, loop=async_loop)
        await remote.async_generate_cert_if_missing()
        await remote.async_start_pairing()
        remotes[host] = remote
        return True

    try:
        run_async(do_start_pairing())
        return jsonify({"status": "pairing_started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/finish_pairing', methods=['POST'])
def finish_pairing():
    host = request.json.get('host')
    code = request.json.get('code')
    remote = remotes.get(host)
    if not remote:
        return jsonify({"error": "No remote for host"}), 400
    
    async def do_finish_pairing():
        await remote.async_finish_pairing(code)
        await remote.async_connect()
        return True

    try:
        run_async(do_finish_pairing())
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/command', methods=['POST'])
def command():
    host = request.json.get('host')
    key = request.json.get('key')
    remote = remotes.get(host)
    if not remote:
        return jsonify({"error": "Not connected"}), 400
    
    # send_key_command is safe to call from any thread as it uses loop.call_soon
    try:
        remote.send_key_command(key, "SHORT")
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/send_text', methods=['POST'])
def send_text():
    host = request.json.get('host')
    text = request.json.get('text')
    remote = remotes.get(host)
    if not remote:
        return jsonify({"error": "Not connected"}), 400
    
    try:
        remote.send_text(text)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    # use_reloader=False to avoid starting multiple background threads
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
