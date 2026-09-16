import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, Ticket, Comment

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "helpdesk.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# --- Page Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# --- REST API Endpoints ---

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retrieve ticket metrics breakdown"""
    total = Ticket.query.count()
    open_count = Ticket.query.filter_by(status='Open').count()
    in_progress_count = Ticket.query.filter_by(status='In Progress').count()
    resolved_count = Ticket.query.filter_by(status='Resolved').count()
    closed_count = Ticket.query.filter_by(status='Closed').count()

    return jsonify({
        'total': total,
        'open': open_count,
        'in_progress': in_progress_count,
        'resolved': resolved_count,
        'closed': closed_count
    }), 200

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Fetch tickets with optional filter and search parameters"""
    query = Ticket.query

    status = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')
    search = request.args.get('search')

    if status and status != 'All':
        query = query.filter_by(status=status)
    if priority and priority != 'All':
        query = query.filter_by(priority=priority)
    if category and category != 'All':
        query = query.filter_by(category=category)
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            (Ticket.title.ilike(search_pattern)) |
            (Ticket.description.ilike(search_pattern)) |
            (Ticket.requester_name.ilike(search_pattern)) |
            (Ticket.requester_email.ilike(search_pattern))
        )

    # Order by creation date descending
    tickets = query.order_by(Ticket.created_at.desc()).all()
    return jsonify([ticket.to_dict() for ticket in tickets]), 200

@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Fetch a single ticket with details and comments"""
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    return jsonify(ticket.to_dict(include_comments=True)), 200

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    """Create a new support ticket"""
    data = request.get_json() or {}

    required_fields = ['title', 'description', 'requester_name', 'requester_email']
    for field in required_fields:
        if not data.get(field, '').strip():
            return jsonify({'error': f'Field "{field}" is required.'}), 400

    new_ticket = Ticket(
        title=data['title'].strip(),
        description=data['description'].strip(),
        category=data.get('category', 'IT').strip(),
        priority=data.get('priority', 'Medium').strip(),
        status='Open',
        requester_name=data['requester_name'].strip(),
        requester_email=data['requester_email'].strip()
    )

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify(new_ticket.to_dict()), 201

@app.route('/api/tickets/<int:ticket_id>', methods=['PATCH'])
def update_ticket(ticket_id):
    """Update ticket attributes (status, priority, category)"""
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    data = request.get_json() or {}

    if 'status' in data:
        valid_statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
        if data['status'] in valid_statuses:
            ticket.status = data['status']
        else:
            return jsonify({'error': f'Invalid status. Must be one of {valid_statuses}'}), 400

    if 'priority' in data:
        valid_priorities = ['Low', 'Medium', 'High', 'Urgent']
        if data['priority'] in valid_priorities:
            ticket.priority = data['priority']
        else:
            return jsonify({'error': f'Invalid priority. Must be one of {valid_priorities}'}), 400

    if 'category' in data:
        ticket.category = data['category']

    db.session.commit()
    return jsonify(ticket.to_dict(include_comments=True)), 200

@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """Delete a support ticket"""
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': f'Ticket #{ticket_id} deleted successfully.'}), 200

@app.route('/api/tickets/<int:ticket_id>/comments', methods=['POST'])
def add_comment(ticket_id):
    """Add a comment/update note to a ticket"""
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    data = request.get_json() or {}
    author = data.get('author', 'Support Agent').strip()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'error': 'Comment content cannot be empty.'}), 400

    comment = Comment(
        ticket_id=ticket.id,
        author=author,
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
