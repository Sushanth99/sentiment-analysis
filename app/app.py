#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect
from DBcm_pymysql import UseDatabase, ConnectionError, CredentialsError, SQLError
import json
import datetime
from utilities import *
import time 

app = Flask(__name__)

app.secret_key = 'YouWillNeverGuessMySecretKey'

# db_user = os.environ.get('CLOUD_SQL_USERNAME')
# db_password = os.environ.get('CLOUD_SQL_PASSWORD')
# db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
# db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
# unix_socket = '/cloudsql/{}'.format(db_connection_name)

# app.config['dbconfig'] = {
#                           'user': db_user,
#                           'password': db_password,
#                           'database': db_name,
#                           'unix_socket': unix_socket,
#                           'use_unicode': True, 
#                           'charset': "utf8",
#                          }

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'testuser',
                          'password': 'testpasswd',
                          'database': 'testDB',
                          'use_unicode': True, 
                          'charset': "utf8",
                         }


CLASSIFIERS = ['Sentiment', 'Sarcasm']

# Loading the models
sentiment_model, sarcasm_model = load_model()
# UNIQUE_ID = 1
date = datetime.datetime.today().strftime('%d-%m-%Y')


def log_request(req: 'flask_request', comment: str, res: 'json') -> None:
    """Logs details of the web request and the results."""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into user_queries
                (username, tweet, classifier, comment, ip_address, browser, result)
                values
                (%s, %s, %s, %s, %s, %s, %s)"""
        print(req.user_agent)
        print('BROWSER:', req.user_agent.browser)
        print(type(req.user_agent))
        print(vars(req.user_agent))
        print(req.user_agent.platform)
        cursor.execute(_SQL, (session.get('username', 'chutki'),
                            req.form.get('tweet', None),
                            req.form.get('classifier', None),
                            comment,
                            req.remote_addr,
                            req.user_agent.browser,
                            res,
                            ))

def log_user(username, password) -> None:
    """Logs new user info into the user_login table."""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into user_login
                (username, password)
                values
                (%s, %s)"""
        cursor.execute(_SQL, (username, password))

@app.route('/login', methods=['POST', 'GET'])
def do_login() -> str:
    if check_login(): return redirect('/')
    
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    if username is None or password is None:
        return render_template('login.html', date=date)
    else:
        ## Check login credentials
        try:
            with UseDatabase(app.config['dbconfig']) as cursor:
                _SQL = """select * from user_login where username = %s and password = %s"""
                cursor.execute(_SQL, (username, password))
                contents = cursor.fetchall()
                if len(contents) == 0: 
                    message = 'Incorrect Username or Password!!.'
                    return render_template('login.html', date=date, message=message)
                else:
                    session['logged_in'] = True
                    session['username'] = username
                    return redirect('/')
        #     titles = ('ID', 'Timestamp', 'Tweet', 'Classifier', 'Comment', 'IP', 'Browser', 'Result')
        #     return render_template('queries.html',
        #                         the_row_titles=titles,
        #                         the_data=contents,
        #                             )
        except ConnectionError as err:
            print('Is your database switched on? Error:', str(err))
        except CredentialsError as err:
            print('User-id/Password issues. Error:', str(err))
        except SQLError as err:
            print('Is your query correct? Error:', str(err))
        except Exception as err:
            print('Something went wrong:', str(err))
        return 'Error'


@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in', None)
    session.pop('username', None)
    message = 'You are now logged out.'
    return render_template('/login.html', date=date, message=message)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if check_login(): return redirect('/')
    
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    if username is None or password is None:
        return render_template('register.html', date=date)
    else:
        try:
            with UseDatabase(app.config['dbconfig']) as cursor:
                _SQL = """select * from user_login where username = %s"""
                cursor.execute(_SQL, (username,))
                contents = cursor.fetchall()
                if len(contents) == 0:
                    log_user(username, password)
                    message = 'You are registered. Please login.'
                    return render_template('login.html', date=date, message=message)
                else:
                    message = 'User already exists!! Choose a different username.'
                    return render_template('register.html', date=date, message=message)

        except ConnectionError as err:
            print('Is your database switched on? Error:', str(err))
        except CredentialsError as err:
            print('User-id/Password issues. Error:', str(err))
        except SQLError as err:
            print('Is your query correct? Error:', str(err))
        except Exception as err:
            print('Something went wrong:', str(err))
        return 'Error'

@app.route('/')
def home():
    date = datetime.datetime.today().strftime('%d-%m-%Y')
    return render_template('home.html', date=date, classifiers=CLASSIFIERS, login=check_login())

@app.route('/results', methods=['POST'])
def get_results():
    # Variables
    timestamp = datetime.datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    t1 = time.time()

    # Getting data from form
    analysis_type = request.form.get('analysis_type', None)
    text = request.form.get('tweet', None)
    classifier = request.form.get('classifier', None)
    tweet_count = int(request.form.get('tweet_count', None))
    since_date = request.form.get('since_date', None)
    until_date = request.form.get('until_date', None)

    # res = {'sentiment': sentiment_model.predict([text]),
    #        'sarcasm': sarcasm_model.predict([text])}
    # res = json.dumps(res)

    res, _input_data = nlp(analysis_type, text, classifier, tweet_count, until_date, since_date, sentiment_model, sarcasm_model)
    if text is None:
        return render_template('input_not_supported.html')

    ## Edit
    # analysis_type = request.form['analysis_type']
    # print('analysis_type:', analysis_type)

    # Generating result in json
    # res = json.dumps({'Classifier': 'Both', 'Result': 'neutral'})

    if classifier != 'Both' and classifier not in CLASSIFIERS:
        # Storing the query data
        log_request(request, comment='UNSUPPORTED CLASSIFIER', res=json.dumps({}))
        return render_template('input_not_supported.html')

    # Storing the query data
    log_request(request, comment='OK', res=json.dumps(res))
    print('After logging the request in the database.')
    t2 = time.time()

    print('Total time taken: {:.2f}'.format(t2 - t1))
    # Loading the results page
    return render_template('results.html',
                            timestamp=timestamp,
                            classifier=classifier,
                            tweet=text,
                            res=res)



@app.route('/queries')
@check_logged_in
def view_the_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select id, ts, tweet, classifier, comment, ip_address, browser, result from user_queries where username=%s"""
            cursor.execute(_SQL, (session['username'],))
            contents = cursor.fetchall()

        titles = ('ID', 'Timestamp', 'Tweet', 'Classifier', 'Comment', 'IP', 'Browser', 'Result')
        return render_template('queries.html',
                               the_row_titles=titles,
                               the_data=contents,
                                 )
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
    except CredentialsError as err:
        print('User-id/Password issues. Error:', str(err))
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
    except Exception as err:
        print('Something went wrong:', str(err))
    return 'Error'


if __name__ == '__main__':
    app.run(debug=True)
    