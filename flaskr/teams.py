from werkzeug.exceptions import abort
from pymongo import MongoClient
from bson import json_util
from bson import ObjectId
from ast import literal_eval
import json
import os
import re
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from .users import get_user_by_id

bp = Blueprint('teams', __name__, url_prefix='/teams')

@bp.route('/create', methods=['POST'])
def create_teams(check_author=True):
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    TeamDB = db['Teams']
    TeamRoleDB = db['UsersRolesTeams']
    
    teamName = request.form['teamName']
    creater = request.form['creater']
    if not teamName or len(teamName) > 250 or teamName == '':
        return {'status': 'ten team khong hop le'}, 200
    if get_user_by_id(creater) == []:
        return {'status': 'creater khong ton tai'}, 200
    TeamData  = { 
                    "teamName": teamName,
                    "createrID": creater,
                }      
    res = TeamDB.insert_one(TeamData)
    roleData = {
                    'teamID': str(res.inserted_id),
                    'userID': creater,
                    'RoleID': '0'
    }
    TeamRoleDB.insert_one(roleData)

    return json.loads(json_util.dumps({'teamName': teamName, 'teamID': str(res.inserted_id), 'createrID': creater}))

@bp.route('/<string:id>', methods=['GET'])
def get_teams_by_ID(id, check_author=True):
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    TeamDB = db['Teams']
    TeamRoleDB = db['UsersRolesTeams']

    myquery = {}
    myquery['_id'] = ObjectId(id)
    team = []
    try:
        team = TeamDB.find(myquery)
        team = json.loads(json_util.dumps(team))
    except:
        return {'status': 'teamID error'}
    if team == []:
        return {'status': 'teamID error'}
    team = team[0]
    
    myquery = {'teamID' : team['_id']['$oid']}
    member = TeamRoleDB.find(myquery)
    if member == []:
        return {'teamID error'}, 200
    
    member = json.loads(json_util.dumps(member))
    members_array = []
    for m in member:
        members_array.append({'id': m['_id'], 'userID' : m['userID'], 'RoleID': m['RoleID']})
    team['members'] = members_array
    
    return team

@bp.route('/allteams', methods=['GET'])
def get_all_teams(check_author=True):
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    TeamDB = db['Teams']
    team = TeamDB.find()
    team = json.loads(json_util.dumps(team))
    
    return team, '200'

@bp.route('/<string:teamid>/users', methods=['POST'])
def add_teams_member(teamid, check_author=True):
    team = get_teams_by_ID(teamid)
    team_members = [i['userID'] for i in team['members']]
    myquery = []
    respone = ''
    for user in literal_eval(request.form['addUsers']):
        if user in team_members:
            respone += 'user ' + user + ' da o trong team. '
        else:
            myquery.append({'teamID': teamid, 'userID': user, 'RoleID': '1'})
            respone += 'user ' + user + ' chua co trong team. '
    if myquery == []:
        return {'status': 'cac user deu da o trong team nay.'}, 200
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    TeamRoleDB = db['UsersRolesTeams']
    res = TeamRoleDB.insert_many(myquery)
    return {'addUsers': [i['userID'] for i in myquery], 'status' : respone}, 200

@bp.route('/<string:teamid>', methods=['PUT'])  # change role of a user in a team
def update_teams(teamid, check_author=True):
    team_info = get_teams_by_ID(teamid)
    userID = request.form['userID']  
    team_members = [i['userID'] for i in team_info['members']]
    if userID not in team_members:
        return {'status': 'user khong thuoc team nay.'}, 200
    
    change_role_to = request.form['role']
    if change_role_to not in ['0', '1']:
        return {'status':'role thay doi khong dung.'},'200'
    
    number_of_admin = sum([1 for i in team_info['members'] if i['RoleID'] == '0'])
    cur_member = [i for i in team_info['members'] if i['userID'] == userID][0]
    if number_of_admin == 1 and cur_member['RoleID'] == '0' and change_role_to == '1':
        return {'status': 'khong the thay doi vi user ' + userID + ' dang la admin duy nhat.'}, 200

    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    TeamRoleDB = db['UsersRolesTeams']

    myquery = {'userID': userID, 'teamID': teamid}
    newquery = {"$set":{'RoleID': change_role_to}}

    res = TeamRoleDB.update_one(myquery, newquery)

    return {'status':'cap nhat thanh cong.'},'200'

@bp.route('/<string:teamid>/users', methods=['DELETE'])
def delete_member_from_teams(teamid, SU_cmd = False, check_author=True):
    team_info = get_teams_by_ID(teamid)
    userID = request.form['userID']  
    team_members = [i['userID'] for i in team_info['members']]
    if userID not in team_members:
        return {'status': 'user khong thuoc team nay.'}, 200
    cur_member = [i for i in team_info['members'] if i['userID'] == userID][0]
    if cur_member['RoleID'] == '0':
        return {'status': 'khong the xoa user dang la admin.'}, 200
    
    myquery = { "_id": ObjectId(cur_member['id']['$oid'])}

    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    TeamRoleDB = db['UsersRolesTeams']
    res = TeamRoleDB.delete_one(myquery)
    
    return {'status': 'da xoa user ' + userID + ' khoi team ' + teamid},'200'

@bp.route('/<string:teamid>', methods=['DELETE'])
def delete_teams(teamid, check_author=True):
    team_info = get_teams_by_ID(teamid)
    if 'status' in team_info.keys():
        return {'status': 'id team khong ton tai.'}
    
    client = MongoClient('mongodb://localhost:27017/') 
    db = client['demoDB'] 
    TeamDB = db['Teams']
    TeamRoleDB = db['UsersRolesTeams']
    TeamRoleDB.delete_many({'teamID': teamid})
    TeamDB.delete_one({'_id': ObjectId(teamid)})
    return {'status': 'da xoa team ' + teamid},'200'