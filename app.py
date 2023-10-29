from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
#from words import modules
from test_utils import check_answer, get_next_word, get_image_path
from data_recorder import record_data
import glob
import importlib
import random
import csv

from database import db, WordRecord,init_db


app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testrecord.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize the db with this app
init_db(app)  # This line ensures db is initialized with the app

def record_to_db(username, word, book_name, module, is_correct, test_type):
    print("recodrding data in DB")
    record = WordRecord(
        student_name=username,
        word=word,
        book_name=book_name,
        module=module,
        is_correct=is_correct,
        test_type=test_type
    )
    db.session.add(record)
    db.session.commit()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('select'))  # Redirect to the combined selection route

@app.route('/select', methods=['GET', 'POST'])
def select():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # Dynamically import all books and their modules
    BOOKS_MODULES = {}
    BOOKS_DIR = "books"
    for book_file in glob.glob(f"{BOOKS_DIR}/book*.py"):
        book_name = os.path.splitext(os.path.basename(book_file))[0]
        book_module = importlib.import_module(f"{BOOKS_DIR}.{book_name}")
        BOOKS_MODULES[book_name] = book_module.modules
    available_books = list(BOOKS_MODULES.keys())
    modules = {}

    if request.method == 'POST':
        selected_book = request.form.get('selected_book')
        selected_module = request.form.get('selected_module')
        selected_test_type = request.form.get('test_type')

        # If a book is selected, update the session and load its modules
        if selected_book in available_books:
            session['selected_book'] = selected_book
            modules = BOOKS_MODULES[selected_book]
            return render_template('select.html', books=available_books, modules=modules.keys())  # Reload with modules


        # If a module and test type is selected, update the session and redirect
        elif selected_module and selected_test_type:
            if 'selected_book' in session:
                modules = BOOKS_MODULES[session['selected_book']]
                if selected_module in modules:
                    session['selected_module'] = selected_module
                    if selected_test_type == "cn_to_en":
                        return redirect(url_for('test_cn_to_en'))
                    elif selected_test_type == "en_to_cn":
                        return redirect(url_for('test_en_to_cn'))
                    elif selected_test_type == "cn_to_m_en":  # 这是新增的逻辑
                        return redirect(url_for('test_cn_to_m_en'))
                    elif selected_test_type == "test_mode_en_to_cn": # new test mode
                        return redirect(url_for('test_mode_en_to_cn'))

    # If a book is already selected, get its modules
    elif 'selected_book' in session and session['selected_book'] in BOOKS_MODULES:
        modules = BOOKS_MODULES[session['selected_book']]

    return render_template('select.html', books=available_books, modules=modules.keys())


'''
BOOKS_DIR = "books"
BOOKS_MODULES = {}

# Dynamically import all books and their modules
for book_file in glob.glob(f"{BOOKS_DIR}/book*.py"):
    book_name = os.path.splitext(os.path.basename(book_file))[0]
    book_module = __import__(f"{BOOKS_DIR}.{book_name}", fromlist=[''])
    BOOKS_MODULES[book_name] = book_module.modules



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
            #return redirect(url_for('test', module_name=selected_module))
            return redirect(url_for('select_test_type'))  # 重定向到测试类型选择页面

    return render_template('select_module.html', modules=modules.keys())

@app.route('/select_test_type', methods=['GET', 'POST'])
def select_test_type():
    if 'selected_module' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        selected_test_type = request.form.get('test_type')
        if selected_test_type == "cn_to_en":
            return redirect(url_for('test_cn_to_en'))
        elif selected_test_type == "en_to_cn":
            return redirect(url_for('test_en_to_cn'))

    return render_template('select_test_type.html')

'''

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


@app.route('/video_list')
def video_list():
    video_files = [f for f in os.listdir('static/videos') if f.endswith('.mp4')]
    return render_template('video_list.html', video_files=video_files)

@app.route('/play_video/<filename>')
def play_video(filename):
    return render_template('play_video.html', video_file=url_for('static', filename=f'videos/{filename}'))




#@app.route('/test', methods=['GET', 'POST'])
#def test():
@app.route('/test_cn_to_en', methods=['GET', 'POST'])
def test_cn_to_en():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # Check if the book and module are selected
    #if 'selected_book' not in session or 'selected_module' not in session:
     #   return redirect(url_for('select_book'))

    # Dynamically import the selected book's module
    #book_module = importlib.import_module(f"books.{session['selected_book']}")
    #modules = book_module.modules  # Access the 'modules' dictionary from the imported book module

    # Get the selected module's words
   # words = modules[session['selected_module']]
    if 'selected_book' not in session or 'selected_module' not in session:
        return redirect(url_for('select'))  # Redirect to combined selection route

    # Dynamically import the selected book's module
    book_module = importlib.import_module(f"books.{session['selected_book']}")

    # Get the selected module's words
    words = book_module.modules[session['selected_module']]  # Directly access the 'modules' dictionary from the imported book module
    #print(session)
    if 'current_word' not in session or session['current_word'] not in words:
        session['current_word'] = list(words.keys())[0]
    

    if request.method == 'POST':
        user_input = request.form.get('word_input')
        if check_answer(user_input, session['current_word']):
            record_data(session['username'], session['current_word'], session['selected_book'], session['selected_module'], True)
            record_to_db(session['username'], session['current_word'], session['selected_book'], session['selected_module'], True, "cn_to_en")
            current_index = list(words.keys()).index(session['current_word'])
            if current_index + 1 < len(words):
                session['current_word'] = list(words.keys())[current_index + 1]
            else:
                session.clear()
                return "Module completed!"
        else:
            record_data(session['username'], session['current_word'], session['selected_book'], session['selected_module'], False)
            record_to_db(session['username'], session['current_word'], session['selected_book'], session['selected_module'], False, "cn_to_en")
            image_path = get_image_path(session['current_word'])         
            return render_template('test_cn_to_en.html', word=words[session['current_word']], image_path=image_path)
    
    return render_template('test_cn_to_en.html', word=words[session['current_word']])

@app.route('/test_en_to_cn', methods=['GET', 'POST'])
def test_en_to_cn():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # Check if the book and module are selected
   # if 'selected_book' not in session or 'selected_module' not in session:
    #    return redirect(url_for('select_book'))

    # Dynamically import the selected book's module
    #book_module = importlib.import_module(f"books.{session['selected_book']}")
    #modules = book_module.modules  # Access the 'modules' dictionary from the imported book module

    #words = dict(modules[session['selected_module']])  # Create a copy to avoid modifying the original
    if 'selected_book' not in session or 'selected_module' not in session:
        return redirect(url_for('select'))  # Redirect to combined selection route

    # Dynamically import the selected book's module
    book_module = importlib.import_module(f"books.{session['selected_book']}")

    # Get the selected module's words
    words = dict(book_module.modules[session['selected_module']])  # Directly access the 'modules' dictionary from the imported book module
    #print(session)
# Get a random word from the module
  #  word_en, word_cn = random.choice(list(words.items()))
    if 'word_index' not in session:
        session['word_index'] = 0
    word_keys = list(words.keys())
    if session['word_index'] < len(word_keys):
        word_en = word_keys[session['word_index']]
        word_cn = words[word_en]
        #print('现在测试的答案是', word_cn)
        #print('english world', word_en)

  


    # Remove the correct answer from words
        del words[word_en]


        if request.method == 'POST':
            choices = session.get('previous_choices')
            user_choice = request.form.get('word_choice')
            #print('use choose abc is ',user_choice)
            correct_answer = word_cn
            #print('user choice is ',choices[user_choice])
            if choices[user_choice] == correct_answer:
                # 记录正确答案
                # 这里可以更新session或数据库来记录用户得分
                flash('Correct!', 'success')
                record_data(session['username'], word_en, session['selected_book'], session['selected_module'], True)
                record_to_db(session['username'], word_en, session['selected_book'], session['selected_module'], True, "en_to_cn")
                
            else:
                # 记录错误答案
                # 这里可以更新session或数据库来记录用户的错误
                #wrong_answer = True 
                flash(f'Wrong! The correct answer is: {correct_answer}', 'danger')
                record_data(session['username'], word_en, session['selected_book'], session['selected_module'], False)
                record_to_db(session['username'], word_en, session['selected_book'], session['selected_module'], False, "en_to_cn")
                image_path = get_image_path(word_en)         
                return render_template('test_en_to_cn.html', word_en=word_en, choices=choices, image_path=image_path)
            session['word_index'] += 1
            #time.sleep == 1
            return redirect(url_for('test_en_to_cn'))
        else:
                # Generate dummy choices
            dummy_choices = random.sample(list(words.values()), 2)
            dummy_choices.append(word_cn)
            random.shuffle(dummy_choices)

            choices = {
                'a': dummy_choices[0],
                'b': dummy_choices[1],
                'c': dummy_choices[2]
            }
            #print(choices)
            session['previous_choices'] = choices

    else:
        session.clear()
        return "You have completed the module!"

    return render_template('test_en_to_cn.html', word_en=word_en, choices=choices)

@app.route('/test_cn_to_m_en', methods=['GET', 'POST'])
def test_cn_to_m_en():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'selected_book' not in session or 'selected_module' not in session:
        return redirect(url_for('select'))

    # Dynamically import the selected book's module
    book_module = importlib.import_module(f"books.{session['selected_book']}")

    # Get the selected module's words
    words = dict(book_module.modules[session['selected_module']])

    if 'word_index' not in session:
        session['word_index'] = 0
    word_keys = list(words.values())
    if session['word_index'] < len(word_keys):
        word_cn = word_keys[session['word_index']]
        word_en = list(words.keys())[list(words.values()).index(word_cn)]

        # Remove the correct answer from words
        words = {v: k for k, v in words.items()}
        del words[word_cn]

        if request.method == 'POST':
            choices = session.get('previous_choices')
            user_choice = request.form.get('word_choice')
            correct_answer = word_en
            if choices[user_choice] == correct_answer:
                flash('Correct!', 'success')
                record_data(session['username'], word_cn, session['selected_book'], session['selected_module'], True)
                record_to_db(session['username'], word_cn, session['selected_book'], session['selected_module'], True, "cn_to_m_en")
            else:
                flash(f'Wrong! The correct answer is: {correct_answer}', 'danger')
                record_data(session['username'], word_cn, session['selected_book'], session['selected_module'], False)
                record_to_db(session['username'], word_cn, session['selected_book'], session['selected_module'], False, "cn_to_m_en")
                return render_template('test_cn_to_m_en.html', word_cn=word_cn, choices=choices)
            session['word_index'] += 1
            return redirect(url_for('test_cn_to_m_en'))
        else:
            # Generate dummy choices
            dummy_choices = random.sample(list(words.values()), 2)
            dummy_choices.append(word_en)
            random.shuffle(dummy_choices)

            choices = {
                'a': dummy_choices[0],
                'b': dummy_choices[1],
                'c': dummy_choices[2]
            }
            session['previous_choices'] = choices

    else:
        for key in ['selected_book', 'selected_module', 'word_index']:
            if key in session:
                del session[key]
        flash("You have completed the module!")
        return redirect(url_for('select'))

    return render_template('test_cn_to_m_en.html', word_cn=word_cn, choices=choices)

@app.route('/test_mode_en_to_cn', methods=['GET', 'POST'])
def test_mode_en_to_cn():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'selected_book' not in session or 'selected_module' not in session:
        return redirect(url_for('select'))

    # Dynamically import the selected book's module
    book_module = importlib.import_module(f"books.{session['selected_book']}")

    # Get the selected module's words
    words = dict(book_module.modules[session['selected_module']])

    if 'word_index' not in session:
        session['word_index'] = 0
        session['test_results'] = []  # Initialize test results
    
    if 'test_results' not in session:
        session['test_results'] = {}

    word_keys = list(words.keys())
    if session['word_index'] < len(word_keys):
        word_en = word_keys[session['word_index']]
        word_cn = words[word_en]

        del words[word_en]

        if request.method == 'POST':
            choices = session.get('previous_choices')
            user_choice = request.form.get('word_choice')
            correct_answer = word_cn

            result_data = {
                'word': word_en,
                'correct': choices[user_choice] == correct_answer
            }
            session['test_results'].append(result_data)

            session['word_index'] += 1
            return redirect(url_for('test_mode_en_to_cn'))
        else:
            dummy_choices = random.sample(list(words.values()), 2)
            dummy_choices.append(word_cn)
            random.shuffle(dummy_choices)

            choices = {
                'a': dummy_choices[0],
                'b': dummy_choices[1],
                'c': dummy_choices[2]
            }

            session['previous_choices'] = choices
    else:
        correct_answers_count = sum([result['correct'] for result in session['test_results']])
        total_questions = len(session['test_results'])
        accuracy = (correct_answers_count / total_questions) * 100
        
        correct_answers = [result for result in session['test_results'] if result['correct']]
        incorrect_answers = [result for result in session['test_results'] if not result['correct']]

        
        # Clean up session data
        for key in ['selected_book', 'selected_module', 'word_index', 'test_results']:
            if key in session:
                del session[key]

        # Render the test report template with correct and incorrect answers as well as accuracy
        return render_template('test_report.html', correct_answers=correct_answers, incorrect_answers=incorrect_answers, accuracy=accuracy)

    return render_template('test_mode_en_to_cn.html', word_en=word_en, choices=choices)


def get_test_report(username, selected_book, selected_module):
    correct_words = []
    incorrect_words = []

    with open('data_records.csv', 'r') as file:
        records = csv.reader(file)
        next(records)  # Skip header
        for record in records:
            user, word, book, module, result, _ = record
            if user == username and book == selected_book and module == selected_module:
                if result == 'True':
                    correct_words.append(word)
                else:
                    incorrect_words.append(word)

    return correct_words, incorrect_words
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db(app)
    print('Initialized the database.')

if __name__ == '__main__':
    app.run(debug=True,port=8080)
