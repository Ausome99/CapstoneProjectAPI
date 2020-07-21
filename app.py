from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt
import io

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://agnayctohkpfkb:8b5c2e76d508ed7600f60feb9e7a40014301f7cc07db3d59acb3da92be318dca@ec2-34-192-173-173.compute-1.amazonaws.com:5432/db62c3nqb7dreq"

db = SQLAlchemy(app)
ma = Marshmallow(app)

heroku = Heroku(app)
CORS(app)
bcrypt = Bcrypt(app)


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), nullable=False, unique=True)
#     password = db.Column(db.String(), nullable=False)

#     def __init__(self, username, password):
#         self.username = username
#         self.password = password

# class UserSchema(ma.Schema):
#     class Meta:
#         fields = ("id", "username", "password")

# user_schema = UserSchema()
# users_schema = UserSchema(many=True)

# @app.route("/user/create", methods=["POST"])
# def create_user():
#     if request.content_type != "application/json":
#         return jsonify("Error: Data must be sent as JSON")

#     post_data = request.get_json()
#     username = post_data.get("username")
#     password = post_data.get("password")

#     hashed_password = bcrypt.generate_password_hash(password).decode("utf8")

#     record = User(username, hashed_password)
#     db.session.add(record)
#     db.session.commit()

#     return jsonify("User Created Successfully!")

# @app.route("/user/get", methods=["GET"])
# def get_all_users():
#     all_users = db.session.query(User).all()
#     return jsonify(users_schema.dump(all_users))

# @app.route("/user/get/<id>", methods=["GET"])
# def get_user_by_id(id):
#     user = db.session.query(User).filter(User.id == id).first()
#     return jsonify(user_schema.dump(user))

# @app.route("/user/verification", methods=["POST"])
# def verify_user():
#     if request.content_type != "application/json":
#         return jsonify("Error: Data must be sent as JSON")
    
#     post_data = request.get_json()
#     username = post_data.get("username")
#     password = post_data.get("password")

#     stored_password = db.session.query(User.password).filter(User.username == username).first()

#     if stored_password is None:
#         return jsonify("User NOT Verified")

#     valid_password_check = bcrypt.check_password_hash(stored_password[0], password)

#     if valid_password_check == False:
#         return jsonify("User NOT Verified")

#     return jsonify("User Verified")

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

# @app.route("/character/get/<id>", methods=["GET"])
# def get_character_by_id(id):
#     character = db.session.query(Character).filter(Character.id == id).first()
#     return jsonify(character_schema.dump(character))

# @app.route("/character/delete/<id>", methods=["DELETE"])
# def delete_character_by_id(id):
#     character = db.session.query(Character).filter(Character.id == id).first()
#     db.session.delete(character)
#     db.session.commit()
#     return jsonify("Character Deleted")

# @app.route("/character/update/<id>", methods=["PUT"])
# def update_character_by_id(id):
#     if request.content_type != "application/json":
#         return jsonify("Error: Data must be sent as JSON")

#     put_data = request.get_json()
#     name = put_data.get("name")
#     character_class = put_data.get("character_class")
#     hitpoints = put_data.get("hitpoints")

#     character = db.session.query(Character).filter(Character.id == id).first()
#     if name is not None:
#         character.name = name
#     if character_class is not None:
#         character.character_class = character_class
#     if hitpoints is not None:
#         character.hitpoints = hitpoints

#     db.session.commit()

#     return jsonify("Character Updated")

if __name__ == "__main__":
    app.run(debug=True)