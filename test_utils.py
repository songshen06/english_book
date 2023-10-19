# test_utils.py
import os
from flask import url_for
from words import modules

def check_answer(user_input, current_word):
    return user_input == current_word

def get_next_word(module_name, current_word):
    words = modules[module_name]
    current_index = list(words.keys()).index(current_word)
    if current_index + 1 < len(words):
        return list(words.keys())[current_index + 1]
    return None

'''def get_image_path(current_word):
    image_filename = f"pics/{current_word}.png"
    if not os.path.exists(os.path.join("static", image_filename)):
        image_filename = "pics/day.png"
    return url_for('static', filename=image_filename)'''
def get_image_path(current_word):
    # List of supported formats
    formats = ['.png', '.jpeg']

    # Check each format to see if the file exists
    for ext in formats:
        image_filename = f"pics/{current_word}{ext}"
        if os.path.exists(os.path.join("static", image_filename)):
            return url_for('static', filename=image_filename)

    # If no matching format is found, use the default image
    return url_for('static', filename='pics/day.png')
