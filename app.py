from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt
import io

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://clzwznpjvkrjxm:518b6d488de81bb4ce6cb9b37e6be6fa4810623056846951f3db8430c1046a69@ec2-50-19-26-235.compute-1.amazonaws.com:5432/dfftl76kkfiaar"

db = SQLAlchemy(app)
ma = Marshmallow(app)

heroku = Heroku(app)
CORS(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route("/user/create", methods=["POST"])
def create_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf8")

    record = User(username, hashed_password)
    db.session.add(record)
    db.session.commit()

    return jsonify("User Created Successfully!")

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(users_schema.dump(all_users))

@app.route("/user/get/<id>", methods=["GET"])
def get_user_by_id(id):
    user = db.session.query(User).filter(User.id == id).first()
    return jsonify(user_schema.dump(user))

@app.route("/user/verification", methods=["POST"])
def verify_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")
    
    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    stored_password = db.session.query(User.password).filter(User.username == username).first()

    if stored_password is None:
        return jsonify("User NOT Verified")

    valid_password_check = bcrypt.check_password_hash(stored_password[0], password)

    if valid_password_check == True:
        return jsonify("User Verified")

    return jsonify("User NOT Verified")

class Page(db.Model):
    __tablename__ = 'page'
    page_name = db.Column(db.String(), nullable=False, unique=True, primary_key=True)
    text = db.Column(db.String(), nullable=False)

    def __init__(self, page_name, text):
        self.page_name = page_name
        self.text = text

class PageSchema(ma.Schema):
    class Meta:
        fields = ("page_name", "text")

page_schema = PageSchema()
pages_schema = PageSchema(many=True)

class Choice(db.Model):
    __tablename__ = 'choice'
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(), nullable=False)
    text = db.Column(db.String(), nullable=False)
    go_to = db.Column(db.String(), nullable=False)

    def __init__(self, page_name, text, go_to):
        self.page_name = page_name
        self.text = text
        self.go_to = go_to
    
class ChoiceSchema(ma.Schema):
    class Meta:
        fields = ("id", "page_name", "text", "go_to")

choice_schema = ChoiceSchema()
choices_schema = ChoiceSchema(many=True)

class Save(db.Model):
    __tablename__ = 'save'
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), nullable=False, unique=True)

    def __init__(self, page_name, username):
        self.page_name = page_name
        self.username = username
    
class SaveSchema(ma.Schema):
    class Meta:
        fields = ("id", "page_name", "username")

save_schema = SaveSchema()
saves_schema = SaveSchema(many=True)

# Page

@app.route("/page/add", methods=["POST"])
def add_page():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    page_name = post_data.get("page_name")
    text = post_data.get("text")

    record = Page(page_name, text)
    db.session.add(record)
    db.session.commit()

    return jsonify("Page Created")

@app.route("/page/get", methods=["GET"])
def get_all_pages():
    all_pages = db.session.query(Page).all()
    return jsonify(pages_schema.dump(all_pages))

@app.route("/page/get/<page_name>", methods=["GET"])
def get_page_info(page_name):
    page = db.session.query(Page).filter(Page.page_name == page_name).first()
    page_dump = page_schema.dump(page)
    choices = db.session.query(Choice).filter(Choice.page_name == page_name).all()
    page_dump['choices'] = choices_schema.dump(choices)
    return jsonify(page_dump)

# Choices

@app.route("/choice/add", methods=["POST"])
def add_choice():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")
    
    post_data = request.get_json()
    page_name = post_data.get("page_name")
    text = post_data.get("text")
    go_to = post_data.get("go_to")

    record = Choice(page_name, text, go_to)
    db.session.add(record)
    db.session.commit()

    return jsonify("Choice Added")

@app.route("/choice/get", methods=["GET"])
def get_all_choices():
    all_choices = db.session.query(Choice).all()
    return jsonify(choices_schema.dump(all_choices))

# Save

@app.route("/save", methods=["POST"])
def add_save():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")
    
    post_data = request.get_json()
    page_name = post_data.get("page_name")
    username = post_data.get("username")

    save_game = db.session.query(Save).filter(Save.username == username).first()
    if save_game == None:
        record = Save(page_name, username)
        db.session.add(record) 
    else:
        save_game.page_name = page_name  

    db.session.commit()

    return jsonify( { "result":"success", "message":"Game Saved!" } )

@app.route("/load/<username>", methods=["GET"])
def load_save_game(username):
    load = db.session.query(Save).filter(Save.username == username).first()
    return jsonify(save_schema.dump(load))

@app.route("/load", methods=["GET"])
def load_all_save_games():
    load = db.session.query(Save).all()
    return jsonify(saves_schema.dump(load))

if __name__ == "__main__":
    app.run(debug=True)