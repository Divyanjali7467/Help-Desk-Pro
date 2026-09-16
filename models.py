from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='IT')
    priority = db.Column(db.String(20), nullable=False, default='Medium') # Low, Medium, High, Urgent
    status = db.Column(db.String(20), nullable=False, default='Open')    # Open, In Progress, Resolved, Closed
    requester_name = db.Column(db.String(100), nullable=False)
    requester_email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    comments = db.relationship('Comment', backref='ticket', cascade='all, delete-orphan', lazy=True, order_by='Comment.created_at.asc()')

    def to_dict(self, include_comments=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'requester_name': self.requester_name,
            'requester_email': self.requester_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'comment_count': len(self.comments)
        }
        if include_comments:
            data['comments'] = [c.to_dict() for c in self.comments]
        return data

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'author': self.author,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
