from werkzeug.exceptions import abort
from pymongo import MongoClient
from bson import json_util
from bson import ObjectId
import json
import os
import re
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('users', __name__, url_prefix='/')


@bp.route('/users/profile/views', methods=['GET'])
def get_user_by(check_author=True):
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    col = db['customers']
    myquery = {}
    for q in request.args:
        if q == '_id':
            myquery[q] = ObjectId('65fdaa0c8176c43081e785d5')
        else:
            myquery[q] = {"$regex": request.args.get(q)}
            
    result = col.find(myquery)
    result = json.loads(json_util.dumps(result))
    for res in result:
        res['_id'] = res['_id']['$oid']
    print(result)    

    return json.loads(json_util.dumps(result))

@bp.route('/users/profile/views/<string:id>', methods=['GET'])
def get_user_by_id(id, check_author=True):
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    col = db['customers']
    myquery = {}
    
    myquery['_id'] = ObjectId(id)
    result = []
    try:
        result = col.find(myquery)
    except:
        return {}
    if result == []:
        return {}
    result = json.loads(json_util.dumps(result))
    for res in result:
        res['_id'] = res['_id']['$oid'] 

    return json.loads(json_util.dumps(result))

@bp.route('/users', methods=['POST'])
def create_user():
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    col = db['customers']
    
    error = ''
    data = dict(request.form)
    img = request.files['avata']
    data['img'] = img.filename
    if len(data['name']) > 25:
        error += 'name error, '
    if not email_check(data['email']):
        error += 'email error, '
    if not phone_check(data['phone']):
        error += 'phone error, '
    if len(data['note']) > 1000:
        error += 'note error, '
    error += image_check(img)[1]
    print(error)
    if error == '':
        if not os.path.exists('flaskr/save_files/'):
            os.makedirs('flaskr/save_files/')
        img.save(dst = 'flaskr/save_files/' + img.filename)  
        # print('file saved at: ' + 'flaskr/save_files/' + f.filename)


        response  = {       "username": data['username'],
                            "name": data['name'],
                            "password": data['password'],
                            "email": data['email'],
                            "phone": data['phone'],
                            "note": data['note'],
                            "avatar": 'flaskr/save_files/' + img.filename,
                }
        resJ = json.loads(json_util.dumps(response))

        col.insert_one(response)
        return resJ
    else:
        return {'error': error}, 400
#
@bp.route('/users/<string:id>', methods=['PUT'])
def uppdate_user(id):
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    col = db['customers']
    # get_user_by_id
    old_data = get_user_by_id(id)
    if old_data == []:
        return {'error': 'user id khong dung.'}
    old_data = old_data[0]
    # print(old_data)
    data = dict(request.form)
    # print(data)
    myquery = {}
    newquery = {"$set":{}}
    for d in data:
        myquery[d] = old_data[d]
        newquery["$set"][d] = data[d]
            

    col.update_many(myquery, newquery)
    
    # print(myquery)
    # print(newquery)
    return newquery, '200'

@bp.route('/users/<string:id>', methods=['DELETE'])
def delete_user(id):
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    col = db['customers']
    # get_user_by_id
    old_data = get_user_by_id(id)
    if old_data == []:
        return {'error': 'user id khong dung.'}
    old_data = old_data[0]
    myquery = { "_id": ObjectId(id) }
    col.delete_one(myquery)
    
    print(myquery)
    # print(newquery)
    return {'status: ': 'delete success'}, '200'


@bp.route('/users/create')
def create_User():
    return render_template('feature/user/create.html')

@bp.route('/users/create_team')
def create_Team():
    return render_template('feature/user/create.html')

# @bp.route('/user')
# def render_user():
#     return render_template('feature/user/show_user.html')

@bp.route('/users/profile', methods=['POST', 'GET'])
def show_User():
    if request.method == 'POST':
        return render_template('feature/user/show_user.html' , users = get_user_by_username(request.form['username']))
    if request.method == 'GET':
        # return render_template('feature/user/show_user.html')
        return get_user_by_username(request.args.get('name'))

@bp.route('/users')
def upload_file():
   return render_template(['feature/user/user.html'], users = get_user_by_username())


def get_user_by_username(username = 'a', check_author=True):
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 

    col = db['customers']
    user = [i for i in col.find({'username':username})]
    
    # if post is None:
    #     abort(404, f"Post id {id} doesn't exist.")

    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    return json.loads(json_util.dumps(user))

def email_check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(re.fullmatch(regex, email)):
        return True
    return False

def phone_check(phone):
    regex = r'(?:\B\+ ?49|\b0)(?: *[(-]? *\d(?:[ \d]*\d)?)? *(?:[)-] *)?\d+ *(?:[/)-] *)?\d+ *(?:[/)-] *)?\d+(?: *- *\d+)?'
    if(re.fullmatch(regex, phone)):
        return True
    return False

def image_check(img):
    regex = r'(.*)(\w+)(.gif|.jpg|.jpeg|.tiff|.png)'
    err = ''
    if not (re.fullmatch(regex, img.filename)):
        err += 'hinh khong dung dinh dang, '
    if img.seek(0, os.SEEK_END) > 5000000:
        err += 'kich thuoc hinh lon hon 5MB.'
    if err != '':
        return False, err
    return True, err