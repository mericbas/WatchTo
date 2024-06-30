from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/video'
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

live_stream = {
    "file_path": "",
    "link": "",
    "status": "stopped",
    "current_time": 0
}

@app.route('/')
def index():
    return redirect(url_for('live'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global live_stream
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                live_stream['file_path'] = filename
                live_stream['link'] = ""
        elif 'link' in request.form and request.form['link'] != '':
            live_stream['link'] = request.form['link']
            live_stream['file_path'] = ""
        if 'action' in request.form:
            live_stream['status'] = request.form['action']
            emit('control', {'status': live_stream['status']}, namespace='/', broadcast=True)
        return redirect(url_for('admin'))
    return render_template('admin.html', live_stream=live_stream)

@app.route('/live')
def live():
    return render_template('live.html', live_stream=live_stream)

@socketio.on('control')
def handle_control(data):
    global live_stream
    live_stream['status'] = data['status']
    emit('control', {'status': live_stream['status']}, namespace='/', broadcast=True)

@socketio.on('seek')
def handle_seek(data):
    global live_stream
    live_stream['current_time'] = data['time']
    emit('seek', {'time': live_stream['current_time']}, namespace='/', broadcast=True)

@socketio.on('timeupdate')
def handle_timeupdate(data):
    global live_stream
    live_stream['current_time'] = data['time']
    emit('timeupdate', {'time': live_stream['current_time']}, namespace='/', broadcast=True)

if __name__ == '__main__':
    app.debug = True  # Hata ayıklama modu
    socketio.run(app, host='0.0.0.0', port=80)
