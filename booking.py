# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
db = SQLAlchemy(app)

# Models
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False) 
    booking_count = db.Column(db.Integer, default=0)
    date_joined = db.Column(db.DateTime, nullable=False)
    bookings = db.relationship('Booking', backref='member', lazy=True)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    remaining_count = db.Column(db.Integer, default=0)
    expiration_date = db.Column(db.DateTime, nullable=False)
    bookings = db.relationship('Booking', backref='item', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)

# Routes
@app.route('/import', methods=['POST'])
def import_data():
    def safe_text(value, default=''):
        if not value:
            return default
        return str(value).strip()
     
    def safe_int(value, default=0):
        try:
            return int(value.strip()) if value and value.strip() else default
        except ValueError:
            return default
    
    def parse_date(date_str):
        # Try different date formats
        formats = [
        '%Y-%m-%dT%H:%M:%S',  # For members.csv
        '%d/%m/%Y',           # For inventory.csv
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%d/%m/%y',
        '%d-%m-%y'
    ]
        # Clean the input
        date_str = str(date_str).strip()
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        print(f"Failed to parse date: {date_str}")  # Debug logging
        raise ValueError(f"Unsupported date format: {date_str}. Expected formats: YYYY-MM-DDThh:mm:ss or DD/MM/YYYY")

    try:
        with app.app_context():
            db.create_all()
            
            # Import members
            try:
                with open('member.csv', encoding='utf-8-sig') as f:  # Fixed filename
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            member = Member(
                                name=safe_text(row.get('name')),
                                surname=safe_text(row.get('surname')),
                                booking_count=safe_int(row.get('booking_count')),
                                date_joined=parse_date(row.get('date_joined'))
                            )
                            db.session.add(member)
                        except Exception as e:
                            print(f"Error processing member row: {row}, Error: {str(e)}")
                            continue

            except FileNotFoundError:
                return jsonify({"error": "member.csv not found"}), 404

            # Import inventory
            try:
                with open('inventory.csv', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            inventory = Inventory(
                                title=safe_text(row.get('title')),
                                description=safe_text(row.get('description')),
                                remaining_count=safe_int(row.get('remaining_count')),
                                expiration_date=parse_date(row.get('expiration_date'))
                            )
                            db.session.add(inventory)
                        except Exception as e:
                            print(f"Error processing inventory row: {row}, Error: {str(e)}")
                            continue

            except FileNotFoundError:
                return jsonify({"error": "inventory.csv not found"}), 404

            db.session.commit()
            return jsonify({"message": "Data imported successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Import failed: {str(e)}"}), 500

@app.route('/book', methods=['POST'])
def book_item():
    MAX_BOOKINGS = 2
    data = request.get_json()
    
    member = Member.query.get(data['member_id'])
    item = Inventory.query.get(data['inventory_id'])
    
    if not member or not item:
        return jsonify({"error": "Member or item not found"}), 404
        
    if member.booking_count >= MAX_BOOKINGS:
        return jsonify({"error": "Maximum bookings reached"}), 400
        
    if item.remaining_count <= 0:
        return jsonify({"error": "Item not available"}), 400

    booking = Booking(member_id=member.id, inventory_id=item.id)
    member.booking_count += 1
    item.remaining_count -= 1
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        "message": "Booking successful",
        "booking_id": booking.id
    })

@app.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
        
    member = booking.member
    item = booking.item
    
    member.booking_count -= 1
    item.remaining_count += 1
    
    db.session.delete(booking)
    db.session.commit()
    
    return jsonify({"message": "Booking cancelled successfully"})

if __name__ == '__main__':
    app.run(debug=True)