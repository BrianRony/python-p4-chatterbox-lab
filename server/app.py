from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_dict = [message.to_dict() for message in messages]
        
        return make_response(jsonify(messages_dict), 200)
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'body' not in data or 'username' not in data:
            return make_response(jsonify({"error": "Invalid data"}), 400)
        
        try:
            new_message = Message(
                body=data['body'],
                username=data['username']
            )
            db.session.add(new_message)
            db.session.commit()

            return make_response(jsonify(new_message.to_dict()), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    
    if not message:
        return make_response(jsonify({"message": "This record does not exist in our database. Please try again."}), 404)
    
    if request.method == 'GET':
        return make_response(jsonify(message.to_dict()), 200)
    
    elif request.method == 'PATCH':
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "Invalid data"}), 400)
        
        try:
            for attr, value in data.items():
                if hasattr(message, attr):
                    setattr(message, attr, value)
            db.session.commit()

            return make_response(jsonify(message.to_dict()), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(message)
            db.session.commit()

            response_body = {
                "delete_successful": True,
                "message": "Message deleted."
            }

            return make_response(jsonify(response_body), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)

if __name__ == '__main__':
    app.run(port=5555)
