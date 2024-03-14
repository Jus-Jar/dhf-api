from flask import jsonify, request
from app import app
from controllers import pratt_create_textgrid, pratt_save_textgrid, pratt_open_textgrid, vosk_open_audio

# @app.route('/api/books', methods=['GET'])
# def get_books_view():
#     return jsonify(get_books())

# @app.route('/api/books/<int:book_id>', methods=['GET'])
# def get_book_view(book_id):
#     return jsonify(get_book(book_id))

# @app.route('/api/books', methods=['POST'])
# def create_book_view():
#     return create_book(request.json), 201

@app.route('/api/pratt', methods=['GET'])
def test_pratt():
    return pratt_create_textgrid(), 201


@app.route('/api/pratttg', methods=['GET'])
def savepratt():
    return pratt_save_textgrid(), 201

@app.route('/api/prattto', methods=['GET'])
def open_pratt():
    return pratt_open_textgrid(), 201

@app.route('/api/vosk', methods=['GET'])
def open_vosk():
    return vosk_open_audio(), 201