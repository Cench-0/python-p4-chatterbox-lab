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

# Route to get all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()  # Get all messages
    return jsonify([message.to_dict() for message in messages]), 200  # Return as JSON

# Route to create a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()  # Get the message data from the request body
    new_message = Message(
        body=data['body'],
        username=data['username']
    )
    db.session.add(new_message)
    db.session.commit()  # Save the new message to the database
    return jsonify(new_message.to_dict()), 201  # Return the created message as JSON

# Route to get, update, or delete a message by ID
@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def handle_message(id):
    message = Message.query.get(id)
    
    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    if request.method == 'GET':
        return jsonify(message.to_dict()), 200  # Return the message as JSON

    elif request.method == 'PATCH':
        data = request.get_json()  # Get the updated data from the request
        message.body = data.get('body', message.body)
        db.session.commit()  # Save the updated message
        return jsonify(message.to_dict()), 200  # Return the updated message

    elif request.method == 'DELETE':
        db.session.delete(message)  # Delete the message
        db.session.commit()  # Commit the deletion
        return jsonify({'message': 'Message deleted'}), 200

if __name__ == '__main__':
    app.run(port=5555)
