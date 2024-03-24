import os
import re
import functools
from bson import json_util
from bson import ObjectId
import json
from flask import Flask, jsonify
from pymongo import MongoClient
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
) 
from flaskr.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash
bp = Blueprint('feature', __name__, url_prefix='/feature')

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


@bp.route('/uploader', methods=['POST'])
def uploader_file():
    if request.method == 'POST':
        # print('use post')
        f = request.files['filename']
        if not os.path.exists('flaskr/save_files/'):
            os.makedirs('flaskr/save_files/')
        f.save(dst = 'flaskr/save_files/' + f.filename)  
        print('file saved at: ' + 'flaskr/save_files/' + f.filename)
        
    # if request.method == 'GET':
    #     print('use GET')
    
    return 'file uploaded successfully', {"Refresh": "1; url=/feature"}

@bp.route('/NewUser', methods=('GET', 'POST'))
def New_User():
    # account sẽ có 

    # username
    # name: max length = 25
    # email: regex đúng định đạng
    # phone: nếu format theo định dạng (+84)123-456-1234
    # note: max= 1000
    # avatar: file png|jpg|jpeg|gift & size < 5MB

    # print(request)
    error_mes = ''
    if request.method == 'POST':
        # print('use post')
        # check
        if not email_check(request.form['email']):
            print('email sai')
            error_mes += 'email, '
        if request.form['password'] != request.form['repassword']:
            error_mes += 'password, '
        if error_mes != '':
            return 'có lỗi: ' + error_mes
        
        f = request.files['filename']
        if not os.path.exists('flaskr/save_files/'):
            os.makedirs('flaskr/save_files/')
        f.save(dst = 'flaskr/save_files/' + f.filename)  
        # print('file saved at: ' + 'flaskr/save_files/' + f.filename)


        response  = {   "username": request.form['username'],
                            "name": request.form['name'],
                            "password": request.form['password'],
                            "email": request.form['email'],
                            "phone": request.form['phone'],
                            "note": request.form['note'],
                            "avatar": 'flaskr/save_files/' + f.filename,
                }
        # resJ = jsonify(response )

        client = MongoClient('mongodb://localhost:27017/') 
        db = client['demoDB'] 
        # collection = db['customers'] 
        db['customers'].insert_one(response)

    return 'Tạo user mới thành công', {"Refresh": "1; url=/feature/upload"}

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