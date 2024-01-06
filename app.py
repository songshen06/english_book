from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
#from words import modules
from test_utils import check_answer, get_image_path
from data_recorder import record_data,record_result
import glob
import importlib
import random
import csv

from database import db, init_db


app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)

# 创建数据库和表
with app.app_context():
    db.drop_all()  # 先删除所有旧的表结构
    db.create_all()  # 创建新的表结构

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
        #selected_module = request.form.get('selected_module')
        selected_modules = request.form.getlist('selected_modules')  # 获取多个选中的模块
        selected_test_type = request.form.get('test_type')

        # If a book is selected, update the session and load its modules
        if selected_book in available_books:
            session['selected_book'] = selected_book
            modules = BOOKS_MODULES[selected_book]
            return render_template('select.html', books=available_books, modules=modules.keys())  # Reload with modules



        # If a module and test type is selected, update the session and redirect
        #elif selected_module and selected_test_type:
        elif selected_modules and selected_test_type:
            if 'selected_book' in session:
                #modules = BOOKS_MODULES[session['selected_book']]
                #if selected_module in modules:
                session['selected_modules'] = selected_modules
                print(session)
                if selected_test_type == "cn_to_en":
                    return redirect(url_for('test_cn_to_en'))
                elif selected_test_type == "en_to_cn": #看英文选中文
                    return redirect(url_for('test_en_to_cn'))
                elif selected_test_type == "cn_to_m_en":  # 看中文，选英文
                    return redirect(url_for('test_cn_to_m_en'))
                elif selected_test_type == "test_mode_en_to_cn": # 考试模式
                    return redirect(url_for('test_mode_en_to_cn'))
                elif selected_test_type == "retest_mode_en_to_cn": # 无尽模式
                    return redirect(url_for('retest_mode_en_to_cn'))
                elif selected_test_type == "read_en_to_cn": #例句模式
                    return redirect(url_for('read_en_to_cn'))
                elif selected_test_type == "sentence_reorder_test": #例句模式
                    return redirect(url_for('sentence_reorder_test'))
                    
    # If a book is already selected, get its modules
    elif 'selected_book' in session and session['selected_book'] in BOOKS_MODULES:
        modules = BOOKS_MODULES[session['selected_book']]

    return render_template('select.html', books=available_books, modules=modules.keys())



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


#optimized 
def load_words(selected_book, selected_modules):
    """
    Load and combine words from selected book and modules.
    """
    words = {}
    book_module_path = f"books.{selected_book}"
    try:
        book_module = importlib.import_module(book_module_path)
        for module_name in selected_modules:
            words.update(book_module.modules[module_name])
    except ImportError as e:
        print(f"Error importing module {module_name}: {e}")
    return words

def generate_random_indexes(words):
    """
    Generate a list of random indexes for the words.
    """
    return random.sample(range(len(words)), len(words))

def generate_dummy_choices(correct_answer, all_answers, num_dummies=3):
    """
    Generate dummy choices for a quiz question.
    """
    dummy_choices = random.sample([word for word in all_answers if word != correct_answer], num_dummies)
    dummy_choices.append(correct_answer)
    random.shuffle(dummy_choices)
    return dummy_choices

def generate_dummy_choices_new(correct_answer, all_answers, num_dummies=3):
    """
    Generate dummy choices for a quiz question.
    Given the new dictionary structure, where each word has a dictionary
    containing its translation and example sentences, this function will
    pick dummy choices based on the 'translation' field.
    """
    # 提取所有的翻译，并从中选择不是正确答案的翻译
    dummy_choices = random.sample([word_info['translation'] for word, word_info in all_answers.items() if word_info['translation'] != correct_answer], num_dummies)
    dummy_choices.append(correct_answer)
    random.shuffle(dummy_choices)
    return dummy_choices

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
            #record_to_db(session['username'], session['current_word'], session['selected_book'], session['selected_module'], True, "cn_to_en")
            current_index = list(words.keys()).index(session['current_word'])
            if current_index + 1 < len(words):
                session['current_word'] = list(words.keys())[current_index + 1]
            else:
                session.clear()
                return "Module completed!"
        else:
            record_data(session['username'], session['current_word'], session['selected_book'], session['selected_module'], False)
            #record_to_db(session['username'], session['current_word'], session['selected_book'], session['selected_module'], False, "cn_to_en")
            image_path = get_image_path(session['current_word'])         
            return render_template('test_cn_to_en.html', word=words[session['current_word']], image_path=image_path)
    
    return render_template('test_cn_to_en.html', word=words[session['current_word']])

@app.route('/sentence_reorder_test', methods=['GET', 'POST'])
def sentence_reorder_test():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    #correct_answer_chosen = False
    if 'selected_book' in session and 'selected_modules' in session:
        words = load_words(session['selected_book'], session['selected_modules'])
    if 'random_indexes' not in session:
        session['random_indexes'] = generate_random_indexes(words)  
        session['word_index'] = 0
    current_index = session['random_indexes'][session['word_index']]
    word_en, word_info = list(words.items())[current_index]
    word_cn = word_info['translation']
    example_en = word_info['sentences']['example_en']
    example_cn = word_info['sentences']['example_cn']
# 打乱英文句子的单词顺序
    example_en_words = example_en.split()
    random.shuffle(example_en_words)

    if request.method == 'POST':
        user_input = request.form.get('reordered_sentence')
        #print(user_input)
        if user_input.strip() == example_en.strip():
            # 如果答案正确，移动到下一个单词
            session['word_index'] += 1
            if session['word_index'] >= len(session['random_indexes']):
                # 测试结束
                return redirect(url_for('learning_results'))
            else:
                return redirect(url_for('sentence_reorder_test'))
        else:
            # 答案错误，重新加载页面
            flash('Incorrect order, please try again.')

    return render_template('sentence_reorder_test.html', example_cn=example_cn, jumbled_words=example_en_words)

@app.route('/read_en_to_cn', methods=['GET', 'POST'])
def read_en_to_cn():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    correct_answer_chosen = False
    if 'selected_book' in session and 'selected_modules' in session:
        words = load_words(session['selected_book'], session['selected_modules'])
    if 'random_indexes' not in session:
        session['random_indexes'] = generate_random_indexes(words)  
        session['word_index'] = 0
    current_index = session['random_indexes'][session['word_index']]
    word_en, word_info = list(words.items())[current_index]
    word_cn = word_info['translation']
    example_en = word_info['sentences']['example_en']
    example_cn = word_info['sentences']['example_cn']


    if request.method == 'POST':
        if 'next_word' in request.form:
            # 处理“下一个单词”的逻辑
            session['word_index'] += 1
            if session['word_index'] >= len(words):
                # 所有单词完成
                return redirect(url_for('learning_results'))
            return redirect(url_for('read_en_to_cn'))
        elif 'word_choice' in request.form:            
            choices = session.get('previous_choices')
            user_choice = request.form.get('word_choice')
            #print('use choose abc is ',user_choice)
            correct_answer = word_cn
                #print('user choice is ',choices[user_choice])
            if choices[user_choice] == correct_answer:
                correct_answer_chosen = True
                    # 记录正确答案
                    # 这里可以更新session或数据库来记录用户得分
                flash('Correct!', 'success')
                #flash(f'Example: {example_en} - {example_cn}', 'info')
                return render_template('read_en_to_cn.html', word_en=word_en, choices=choices, example_en=example_en, example_cn=example_cn, correct_answer_chosen=correct_answer_chosen)
                #record_data(session['username'], word_en, session['selected_book'], session['selected_modules'], True)
                    #record_to_db(session['username'], word_en, session['selected_book'], session['selected_module'], True, "en_to_cn")
                    
            else:
                    # 记录错误答案
                    # 这里可以更新session或数据库来记录用户的错误
                    #wrong_answer = True 
                flash(f'Wrong! The correct answer is: {correct_answer}', 'danger')
                #record_data(session['username'], word_en, session['selected_book'], session['selected_modules'], False)
                    #record_to_db(session['username'], word_en, session['selected_book'], session['selected_module'], False, "en_to_cn")
                image_path = get_image_path(word_en)         
                return render_template('read_en_to_cn.html', word_en=word_en, choices=choices, image_path=image_path)
        #session['word_index'] += 1
        #if 'next_word' in request.form:
         #   session['word_index'] += 1
          #  if session['word_index'] >= len(words):
                # 所有单词完成
           #     return redirect(url_for('learning_results'))
                #time.sleep == 1
            #return redirect(url_for('read_en_to_cn'))

    else:
        # 生成不包含正确答案的假选项
        correct_answer = word_cn
        #dummy_choices = generate_dummy_choices(correct_answer, words.values())
        dummy_choices = generate_dummy_choices_new(correct_answer, words)
        choices = {
            'a': dummy_choices[0],
            'b': dummy_choices[1],
            'c': dummy_choices[2]
        }
        session['previous_choices'] = choices
        # 在最后返回修改后的模板
        #return render_template('read_en_to_cn.html',word_en=word_en, choices=choices, example_en=example_en, example_cn=example_cn)
        return render_template('read_en_to_cn.html', word_en=word_en, choices=choices, example_en=example_en, example_cn=example_cn, correct_answer_chosen=correct_answer_chosen)

# 确保其他代码引用此函数时使用新的函数名 read_en_to_cn


@app.route('/test_en_to_cn', methods=['GET', 'POST'])
def test_en_to_cn():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'selected_book' in session and 'selected_modules' in session:
        words = load_words(session['selected_book'], session['selected_modules'])
    if 'random_indexes' not in session:
        session['random_indexes'] = generate_random_indexes(words)  
        session['word_index'] = 0
    # 获取当前单词
    current_index = session['random_indexes'][session['word_index']]
    word_en, word_cn = list(words.items())[current_index]
    #print('现在测试的答案是', word_cn)
    #print('english world', word_en)
   # print(current_index)  


    if request.method == 'POST':
        choices = session.get('previous_choices')
        user_choice = request.form.get('word_choice')
        print('use choose abc is ',user_choice)
        correct_answer = word_cn
            #print('user choice is ',choices[user_choice])
        if choices[user_choice] == correct_answer:
                # 记录正确答案
                # 这里可以更新session或数据库来记录用户得分
            flash('Correct!', 'success')
            record_data(session['username'], word_en, session['selected_book'], session['selected_modules'], True)
                #record_to_db(session['username'], word_en, session['selected_book'], session['selected_module'], True, "en_to_cn")
                
        else:
                # 记录错误答案
                # 这里可以更新session或数据库来记录用户的错误
                #wrong_answer = True 
            flash(f'Wrong! The correct answer is: {correct_answer}', 'danger')
            record_data(session['username'], word_en, session['selected_book'], session['selected_modules'], False)
                #record_to_db(session['username'], word_en, session['selected_book'], session['selected_module'], False, "en_to_cn")
            image_path = get_image_path(word_en)         
            return render_template('test_en_to_cn.html', word_en=word_en, choices=choices, image_path=image_path)
        session['word_index'] += 1
        if session['word_index'] >= len(words):
            # 所有单词完成
            return redirect(url_for('learning_results'))
            #time.sleep == 1
        return redirect(url_for('test_en_to_cn'))
    
    else:
        # 生成不包含正确答案的假选项
        correct_answer = word_cn
        dummy_choices = generate_dummy_choices(correct_answer, words.values())
        choices = {
            'a': dummy_choices[0],
            'b': dummy_choices[1],
            'c': dummy_choices[2]
        }
        session['previous_choices'] = choices
    #print(choices)
    # 显示当前单词和选项
    return render_template('test_en_to_cn.html', word_en=word_en, choices=choices)




@app.route('/test_cn_to_m_en', methods=['GET', 'POST'])
def test_cn_to_m_en():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'selected_book' in session and 'selected_modules' in session:
        words = load_words(session['selected_book'], session['selected_modules'])

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
                #record_to_db(session['username'], word_cn, session['selected_book'], session['selected_module'], True, "cn_to_m_en")
            else:
                flash(f'Wrong! The correct answer is: {correct_answer}', 'danger')
                record_data(session['username'], word_cn, session['selected_book'], session['selected_module'], False)
                #record_to_db(session['username'], word_cn, session['selected_book'], session['selected_module'], False, "cn_to_m_en")
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

@app.route('/test_mode_en_to_cn', methods=['GET', 'POST'])   #考试模式
def test_mode_en_to_cn():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'selected_book' in session and 'selected_modules' in session:
        words = load_words(session['selected_book'], session['selected_modules'])
    if 'random_indexes' not in session:
        session['random_indexes'] = generate_random_indexes(words)  
        session['word_index'] = 0
    # 获取当前单词
    current_index = session['random_indexes'][session['word_index']]
    word_en, word_cn = list(words.items())[current_index]
    #print('现在测试的答案是', word_cn)
    #print('english world', word_en)
    print(current_index)  

    if 'random_indexes' not in session:
        session['random_indexes'] = random.sample(range(len(words)), len(words))
        session['word_index'] = 0
    # 检查是否已测试完所有单词
    if session['word_index'] >= len(session['random_indexes']):
        # 处理所有单词都已测试的情况
        # 计算准确率，显示测试结果，或者重定向到其他页面
        # ...
        correct_answers_count = sum([result['correct'] for result in session['test_results']])
        total_questions = len(session['test_results'])
        #accuracy = (correct_answers_count / total_questions) * 100
        accuracy = int((correct_answers_count / total_questions) * 100)
        correct_answers = [result for result in session['test_results'] if result['correct']]
        incorrect_answers = [result for result in session['test_results'] if not result['correct']]
        #print(incorrect_answers)
        #incorrect_words = [result['word'] for result in incorrect_answers]

    # 如果你想将这些单词记录到数据库，你可以遍历 incorrect_words 列表，并为每个单词调用你的记录函数。
        #for word in incorrect_words:
    # 假设 record_word 是你用来记录单词到数据库的函数
            
        record_result(session['username'], session['selected_book'], session['selected_modules'],accuracy )
        
        # Clean up session data
        for key in ['selected_book', 'selected_modules', 'word_index', 'test_results']:
            if key in session:
                del session[key]

    # Render the test report template with correct and incorrect answers as well as accuracy
        return render_template('test_report.html', correct_answers=correct_answers, incorrect_answers=incorrect_answers, accuracy=accuracy)
    
# 获取当前单词
    current_index = session['random_indexes'][session['word_index']]
    word_en, word_cn = list(words.items())[current_index]
    #print('现在测试的答案是', word_cn)
    #print('english world', word_en)
    print(current_index)  

    #if 'word_index' not in session:
    #    session['word_index'] = 0
    #    session['test_results'] = []  # Initialize test results
    
    if 'test_results' not in session:
       # session['test_results'] = {}
       session['test_results'] = []

    word_keys = list(words.keys())
    if session['word_index'] < len(word_keys):
        #word_en = word_keys[session['word_index']]
        #word_cn = words[word_en]

        #del words[word_en]
        #print(words)

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
            #dummy_choices = random.sample(list(words.values()), 2)
            # 生成不包含正确答案的假选项
            correct_answer = word_cn
            dummy_choices = generate_dummy_choices(correct_answer, words.values())
            choices = {
                'a': dummy_choices[0],
                'b': dummy_choices[1],
                'c': dummy_choices[2],
                'd': dummy_choices[3]
            }

            session['previous_choices'] = choices
    return render_template('test_mode_en_to_cn.html', word_en=word_en, choices=choices)

@app.route('/retest_mode_en_to_cn', methods=['GET', 'POST']) #不做完不结束
def retest_mode_en_to_cn():
    # 保证用户已登录
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'selected_book' in session and 'selected_modules' in session:
        words = load_words(session['selected_book'], session['selected_modules'])

    # 初始化 session 数据
    if 'incorrect_words' not in session :  # 检查incorrect_words是否存在
        session['incorrect_words'] = list(words.keys())  # 如果是，将其初始化为所有英文单词
        session['retest_random_indexes'] = random.sample(range(len(session['incorrect_words'])), len(session['incorrect_words']))
        session['retest_results'] = []
        session['word_index'] = 0

    current_index = session['retest_random_indexes'][session['word_index']]
    #word_en = session['incorrect_words'][session['word_index']]
    word_en = session['incorrect_words'][current_index]
    word_cn = words[word_en]


    #print(word_en)
    #print(word_cn)
    if request.method == 'POST':
        choices = session.get('previous_choices')
        user_choice = request.form.get('word_choice')
        correct_answer = word_cn

        #result_data = {
        #    'word': word_en,
        #    'correct': choices[user_choice] == correct_answer
        #}
        #session['retest_results'].append(result_data)

        if choices[user_choice] == correct_answer:  # 如果选择正确，从incorrect_words列表中移除该单词
            #session['incorrect_words'].pop(session['word_index'])
            session['incorrect_words'].pop(current_index)
            session['retest_random_indexes'] = random.sample(range(len(session['incorrect_words'])), len(session['incorrect_words']))
    # 更新或重置 word_index
            if session['incorrect_words']:  # 如果列表中还有单词
                session['word_index'] = session['word_index'] % len(session['incorrect_words'])  # 更新 word_index
            else:
                for key in ['incorrect_words', 'retest_results', 'word_index', 'previous_choices']:
                    if key in session:
                        del session[key]
                return redirect(url_for('retest_results'))
                
        else:
            #session['word_index'] = (session['word_index'] + 1) % len(session['incorrect_words'])  # 如果选择错误，移到下一个单词
            session['word_index'] = (session['word_index'] + 1) % len(session['retest_random_indexes'])

        return redirect(url_for('retest_mode_en_to_cn'))
    else:
        # 从字典中移除正确的答案，以确保不会被选为干扰项
        words_without_correct = {k: v for k, v in words.items() if v != word_cn}
        
        # 确保所有选项都是唯一的
        while True:
            dummy_choices = random.sample(list(words_without_correct.values()), 2)
            if dummy_choices[0] != word_cn and dummy_choices[1] != word_cn:
                break  # 如果干扰选项都是唯一的，并且不包含正确答案，则退出循环
        
        dummy_choices.append(word_cn)  # 添加正确答案
        random.shuffle(dummy_choices)  # 随机打乱选项顺序

        choices = {
            'a': dummy_choices[0],
            'b': dummy_choices[1],
            'c': dummy_choices[2]
        }

        session['previous_choices'] = choices

    return render_template('retest_mode_en_to_cn.html', word_en=word_en, choices=choices)  # 渲染测试模式模板

@app.route('/retest_results')
def retest_results():
    #selected_book = session.get('selected_book', 'Unknown Book')
    #selected_module = session.get('selected_module', 'Unknown Module')
    selected_book = session.get('selected_book')
    selected_modules = session.get('selected_modules')

    #record_result(session['username'], session['selected_book'], session['selected_modules'],'200' )
    return render_template('retest_results.html', selected_book=selected_book, selected_modules=selected_modules)

@app.route('/learning_results')
def learning_results():
    selected_book = session.get('selected_book', 'Unknown Book')
    selected_module = session.get('selected_modules', 'Unknown Module')
    session.clear()
    return render_template('learning_results.html', selected_book=selected_book, selected_module=selected_module)


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
