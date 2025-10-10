from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import random
import sqlite3

        
app = Flask(__name__)
app.secret_key = 'aS3cr3t!Key#789@dev'

TASKS_FILE = 'tasks.csv'

if os.path.exists(TASKS_FILE):
    tasks = pd.read_csv(TASKS_FILE)
else:
    tasks = pd.DataFrame(columns=['description','priority'])


def save_task():
    tasks.to_csv(TASKS_FILE, index=False)
    print("Task saved successfully")

vectorizer = CountVectorizer()   # It is used for convert the text into machine understandable format i.e binary code

clf = MultinomialNB()   # It is basically classifier it user Naive bayes theorem to get the word count and frequescies  

model = make_pipeline(vectorizer, clf)  # It combines multiple tasks of the data processing together.

if not tasks.empty:
    model.fit(tasks['description'],tasks['priority'])

@app.route('/')
def main():
    return render_template('main.html',tasks=tasks.to_dict(orient='records'))

@app.route('/add_task',methods=['GET', 'POST'])
def add_task():
    global tasks
    if request.method == "POST":
        description = request.form.get('description')
        priority = request.form.get('priority')
        new_task = pd.DataFrame({'description':[description] , 'priority':[priority]})
        tasks = pd.concat([tasks,new_task] , ignore_index=True)
        save_task()
        model.fit(tasks['description'],tasks['priority'])
        flash('Task added successfully')
        return redirect(url_for('main'))
    return render_template('add_task.html')

@app.route('/remove/<description>')
def remove_task(description):
    global tasks
    tasks = tasks[tasks['description'] != description]
    save_task()
    flash('Task removed successfully ✅')
    return redirect(url_for('main'))

def list_task():
    if tasks.empty:
        print('No tasks available')
    else:
        print(tasks)
    
@app.route('/recommend')
def recommend_task():
    if tasks.empty:
        flash('No tasks available for recommendations ❌')
        return redirect(url_for('index'))
    
    high_priority_task = tasks[tasks['priority'] == 'High']
    second_priority_task = tasks[tasks['priority'] == 'Medium']
    low_priority_task = tasks[tasks['priority'] == 'Low']

    if not high_priority_task.empty:
        random_task = random.choice(high_priority_task['description'].tolist())
        priority='High'
        print(f'Recommended task : {random_task} - priority : {priority}')
    elif not second_priority_task.empty:
        random_task = random.choice(second_priority_task['description'].tolist())
        priority='Medium'
        print(f'Recommended task : {random_task} - priority : {priority}')
    elif not low_priority_task.empty:
        random_task = random.choice(low_priority_task['description'].tolist())
        priority='Low'
        print(f'Recommended task : {random_task} - priority : {priority}')
    else:
        flash('No tasks available ❌')
        return redirect(url_for('index'))

    return render_template('recommend.html', task=random_task, priority=priority)

    # def user_interaction():
        # while True:
        #     print("\nTask Management App")
        #     print("1. Add Task")
        #     print("2. Remove Task")
        #     print("3. List Tasks")
        #     print("4. Recommend Task")
        #     print("5. Exit")    

        #     response = input("Select an option : ")
        #     if response == '1':
        #         description = input("Enter the task description : ")
        #         priority = input('Enter priority of this task - High, Medium, Low :')
        #         add_task(description, priority)
        #         print("Task added successfully.")    
        #     elif response == '2':
        #         description = input("Enter the task description : ")
        #         remove_task(description)
        #         print("Task removed successfully.")
        #     elif response == '3':
        #         list_task()
        #     elif response == '4':
        #         recommend_task()
        #     elif response == '5':
        #         print("Thanks for visiting")
        #         break
        #     else:
        #         print("Select valied option.")


if __name__ == '__main__':
    app.run(debug=True)