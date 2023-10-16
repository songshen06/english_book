from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from words import modules
from data_recorder import record_data

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Please enter a username')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('select_module.html', modules=modules.keys())

@app.route('/test/<module_name>', methods=['GET', 'POST'])
def test(module_name):
    if module_name not in modules:
        return "Invalid module", 404

    words = modules[module_name]
    if 'current_word' not in session or session['current_word'] not in words:
        session['current_word'] = list(words.keys())[0]
    
    if request.method == 'POST':
        user_input = request.form.get('word_input')
        if user_input == session['current_word']:
            record_data(session['username'], session['current_word'], module_name, True)
            # Move to the next word
            current_index = list(words.keys()).index(session['current_word'])
            if current_index + 1 < len(words):
                session['current_word'] = list(words.keys())[current_index + 1]               
            else:
                return "Module completed!"
        else:
            record_data(session['username'], session['current_word'], module_name, False)
            # Show hint image
            image_filename = f"pics/{session['current_word']}.png"
            if not os.path.exists(os.path.join("static", image_filename)):
                image_filename = "pics/day.png"
            #image_path = f"./pics/{session['current_word']}.png"
            image_path = url_for('static', filename=image_filename)            
            return render_template('test.html', word=words[session['current_word']], image_path=image_path)
    

    return render_template('test.html', word=words[session['current_word']])

if __name__ == '__main__':
    app.run(debug=True,port=8000)
