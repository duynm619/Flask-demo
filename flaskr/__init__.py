import os

from flask import Flask, request 
from flask import Flask, jsonify
from pymongo import MongoClient
from flask_pymongo import PyMongo


# config = configparser.ConfigParser()
# config.read(os.path.abspath(os.path.join(".ini")))

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    ) 
    

    # create with MongoDB
    # app = create_app()
    app.config['DEBUG'] = True
    # app.config['MONGO_URI'] = config['PROD']['DB_URI']
    app.config['MONGO_URI'] = "mongodb://localhost:27017/demoDB"

    # dblist = client.list_database_names() 
    # app = Flask(__name__)
    # app.config["MONGO_URI"] = "mongodb://localhost:27017/demoDB"
    # mongo = PyMongo(app)

        
    # print("The database exists." if "demoDB" in dblist else "No.")


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
     
    # a simple page that says hello
    @app.route('/hello')
    def hello():        
        return 'hello world'
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import feature
    app.register_blueprint(feature.bp)
    app.add_url_rule('/', endpoint='feature')

    from . import users
    app.register_blueprint(users.bp)
    app.add_url_rule('/users', endpoint='users')

    from . import teams
    app.register_blueprint(teams.bp)
    app.add_url_rule('/', endpoint='teams')

    # Tạo một route để thao tác với MongoDB:
    @app.route('/insert_data', methods=['POST'])
    def insert_data():
        # Thêm dữ liệu vào MongoDB
        data = {'key': 'value'}  # Thay đổi theo cấu trúc dữ liệu của bạn
        collection = db['ten_collection']  # Thay 'ten_collection' bằng tên collection của bạn
        result = collection.insert_one(data)
        return jsonify({'message': 'Data inserted successfully!', 'id': str(result.inserted_id)})


    app.run()
    return app