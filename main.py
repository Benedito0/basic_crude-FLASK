
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
from flask import session as login_session, make_response
from database_setup import Category, Base, Category, CategoryItem, User
import json
import httplib2
import random
import string
import requests

app = Flask(__name__)
app.secret_key = 'vkEphP-h9j2e7KNAv0W_X77v'

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


def create_user(login_session):

    session = DBSession()

    new_user = User(category_name=login_session['user_email'], name=login_session['name'])
    session.add(new_user)
    session.commit()

    user = session.query(User).filter_by(email=login_session['user_email']).one()
    session.close()
    return user.id


def get_userid(email):

    session = DBSession()

    try:
        user = session.query(User).filter_by(user_email=email).one()
        session.close();
        return user.id

    except:
        return None


def get_userinfo(user_id):

    session = DBSession()

    user = session.query(User).filter_by(id=user_id).one()
    session.close();
    return user


# Login Page!
# =====================================================================================================================#
#
#                                                Login
#
# =====================================================================================================================#


@app.route('/login',  methods=['POST', 'GET'])
def hello():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']




    return render_template('login.html', STATE=state)


@app.route('/gconnect',  methods=['POST', 'GET'])
def gconnect():

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        print("Invalid state parameter")
        return response

    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='', redirect_uri='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print("get_cred")

    except FlowExchangeError as error:
        print(error)
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'
        return response

    ggplus_id = credentials.id_token['sub']

    if result['user_id'] != ggplus_id:
        print("Aqui")
        response = make_response(json.dumps("Token's user ID doesnt match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_ggplus_id = login_session.get('gplus_id')

    if stored_credentials is not None and ggplus_id == stored_ggplus_id:
        response = make_response(json.dumps('Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        print("Ali")
        print(credentials.access_token)
        login_session['access_token'] = credentials.access_token
        return response

    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = credentials.id_token['sub']
    login_session['access_token'] = credentials.access_token

    print(login_session['access_token'])
    print(credentials.to_json())

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}

    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(data)

    login_session['user_name'] = data['name']
    login_session['user_email'] = data['email']


    user_exists = get_userid(login_session['user_email'])

    if user_exists is not None:
        user = get_userinfo(create_user(login_session))

    print(user_exists)
    user_id = get_userid(email=login_session['user_email'])
    login_session['user_id'] = user_id


    return redirect(url_for('index'))


# ------------> End Login Page


# =====================================================================================================================#
#
#                                                Logout
#
# =====================================================================================================================#


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token') 
    print("In gdisconnect access token is {}".format(access_token))


    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = "https://accounts.google.com/o/oauth2/revoke?token={}".format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print("Result is")
    print(result)
    if result['status'] == '200':
        
        for key in login_session.keys():

            login_session.pop(key)




        return redirect(url_for('index'))
    else:

        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# ------------> End Login Page
# =====================================================================================================================#
#
#                                                Index Page
#
# =====================================================================================================================#


@app.route('/index', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index():
    session = DBSession()

    categories = session.query(Category).order_by(asc(Category.category_name))
    items = session.query(CategoryItem).join("category")
    print(items)

    # login_session.clear()



    if 'user_id' in login_session:
        id_user = login_session['user_id']

        session.close()
        return render_template('index.html', id=id_user, is_logged=True, categories=categories)

    else:
        session.close()
        return render_template('index.html', categories=categories)


@app.route('/add/category', methods=['POST', 'GET'])
def add_category(categoryname):

    if request.method == 'GET':
        return render_template('show_items.html')

    if request.method == 'POST':
        namecategory = request.form['category_name']

        category = Category(name=namecategory)

        session.add(category)
        session.commit()


@app.route('/add/item',  methods =['POST', 'GET'])
def add_item():
    session = DBSession()


    categories = session.query(Category).order_by(asc(Category.category_name))

    if request.method == 'POST':
        item_name = request.form['item_name']
        item_description = request.form['item_description']
        category_id = request.form['category_id']
        user_id = login_session['user_id']

        item = CategoryItem(name=item_name, description=item_description, category_id=category_id, user_id=user_id)

        session.add(item)
        session.commit()
        flash("Item adicionado!")
        session.close()
        
        return redirect(url_for('index', categories=categories, is_logged=True))

    session.close()

    return render_template('new_item.html', is_logged=True, categories=categories)



@app.route('/catalog/<categoryname>/items',  methods =['POST', 'GET'])
def categoryitems(categoryname):
    session.query()



    if request.method == 'GET':
        return render_template('show_items.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=8080)
