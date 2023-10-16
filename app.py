from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
#from words import modules
from test_utils import check_answer, get_next_word, get_image_path
from data_recorder import record_data
import glob
import importlib


app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management


BOOKS_DIR = "books"
BOOKS_MODULES = {}

# Dynamically import all books and their modules
for book_file in glob.glob(f"{BOOKS_DIR}/book*.py"):
    book_name = os.path.splitext(os.path.basename(book_file))[0]
    book_module = __import__(f"{BOOKS_DIR}.{book_name}", fromlist=[''])
    BOOKS_MODULES[book_name] = book_module.modules

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('select_book.html', books=BOOKS_MODULES.keys())

@app.route('/select_book', methods=['GET', 'POST'])
def select_book():
    # 获取 books 目录下所有的 .py 文件
    book_files = [f for f in os.listdir('books') if f.endswith('.py')]
    
    # 从文件名中提取书的名字，例如从"book1.py"中提取"book1"
    available_books = [os.path.splitext(f)[0] for f in book_files]

    # 如果用户已经选择了一个书籍，将选择存储到 session 中，并重定向到选择模块的页面
    if request.method == 'POST':
        selected_book = request.form.get('selected_book')
        if selected_book in available_books:
            session['selected_book'] = selected_book
            return redirect(url_for('select_module'))
    
    return render_template('select_book.html', books=available_books)




@app.route('/select_module', methods=['GET', 'POST'])
def select_module():
    print(session)
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # Check if the book is selected
    if 'selected_book' not in session:
        print("enterin return select book\n")
        return redirect(url_for('select_book'))

    # Dynamically import the selected book's module
    book_module = importlib.import_module(f"books.{session['selected_book']}")
    modules = book_module.modules  # Access the 'modules' dictionary from the imported book module

    # Handle the form submission
    if request.method == 'POST':
        selected_module = request.form.get('selected_module')
        if selected_module in modules:
            session['selected_module'] = selected_module
            return redirect(url_for('test', module_name=selected_module))

    return render_template('select_module.html', modules=modules.keys())




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





@app.route('/test', methods=['GET', 'POST'])
def test():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # Check if the book and module are selected
    if 'selected_book' not in session or 'selected_module' not in session:
        return redirect(url_for('select_book'))

    # Dynamically import the selected book's module
    book_module = importlib.import_module(f"books.{session['selected_book']}")
    modules = book_module.modules  # Access the 'modules' dictionary from the imported book module

    # Get the selected module's words
    words = modules[session['selected_module']]
    print(session)
    if 'current_word' not in session or session['current_word'] not in words:
        session['current_word'] = list(words.keys())[0]
    
    '''if request.method == 'POST':
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
            return render_template('test.html', word=words[session['current_word']], image_path=image_path)'''
    if request.method == 'POST':
        user_input = request.form.get('word_input')
        if check_answer(user_input, session['current_word']):
            record_data(session['username'], session['current_word'], session['selected_book'], session['selected_module'], True)
            current_index = list(words.keys()).index(session['current_word'])
            if current_index + 1 < len(words):
                session['current_word'] = list(words.keys())[current_index + 1]
            else:
                return "Module completed!"
        else:
            record_data(session['username'], session['current_word'], session['selected_book'], session['selected_module'], False)
            image_path = get_image_path(session['current_word'])         
            return render_template('test.html', word=words[session['current_word']], image_path=image_path)
    
    return render_template('test.html', word=words[session['current_word']])

if __name__ == '__main__':
    app.run(debug=True,port=8080)
