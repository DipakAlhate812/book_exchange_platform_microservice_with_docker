from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests

# Initialize Flask app and the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Path to SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications to save resources
db = SQLAlchemy(app)

# Define the Book model (table)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.Integer)

    def __repr__(self):
        return f'<Book {self.title}>'

# Endpoint to list all books
@app.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()  # Query to fetch all books from the database
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'year': book.year
    } for book in books]), 200

# Endpoint to search books by title or author
@app.route('/books/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '').lower()  # Search query from URL params
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400
    
    # Search for books by title or author (case-insensitive search)
    books = Book.query.filter(
        (Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))
    ).all()

    if not books:
        return jsonify({"message": "No books found matching the search criteria."}), 404

    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'year': book.year
    } for book in books]), 200

# Endpoint to add a new book
@app.route('/books', methods=['POST'])
def add_book():
    new_book = request.get_json()
    
    if not new_book or not new_book.get('title') or not new_book.get('author'):
        return jsonify({"error": "Book title and author are required."}), 400

    book = Book(
        title=new_book['title'],
        author=new_book['author'],
        genre=new_book.get('genre'),
        year=new_book.get('year')
    )
    
    db.session.add(book)
    db.session.commit()  # Save to database
    
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'year': book.year
    }), 201

# Endpoint to edit a book
@app.route('/books/<int:id>', methods=['PUT'])
def edit_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"error": "Book not found."}), 404
    
    updated_data = request.get_json()

    # Update book fields if provided
    book.title = updated_data.get('title', book.title)
    book.author = updated_data.get('author', book.author)
    book.genre = updated_data.get('genre', book.genre)
    book.year = updated_data.get('year', book.year)

    db.session.commit()  # Save changes to the database

    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'year': book.year
    }), 200

# Endpoint to delete a book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"error": "Book not found."}), 404

    db.session.delete(book)
    db.session.commit()  # Remove the book from the database

    return jsonify({"message": "Book deleted successfully."}), 200

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True,host='0.0.0.0', port=8003)

