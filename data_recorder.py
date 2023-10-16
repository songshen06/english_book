import csv
from datetime import datetime

def record_data(username, word, book_name, module, is_correct):
    with open('data_records.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'correct' if is_correct else 'fault'
        writer.writerow([username, current_time, word, book_name, module, status])
