from app import app
from models import db, Ticket, Comment

def seed_database():
    with app.app_context():
        print("Resetting database...")
        db.drop_all()
        db.create_all()

        sample_tickets = [
            {
                "title": "VPN connection drops every 15 minutes",
                "description": "Whenever I connect to the corporate VPN from home, the connection drops repeatedly after 15 minutes of inactivity.",
                "category": "IT",
                "priority": "High",
                "status": "In Progress",
                "requester_name": "Alice Johnson",
                "requester_email": "alice.johnson@company.com",
                "comments": [
                    {"author": "IT Helpdesk", "content": "Checking user authentication logs on VPN gateway."},
                    {"author": "Alice Johnson", "content": "I am on Windows 11 using Cisco AnyConnect."}
                ]
            },
            {
                "title": "Request for dual monitor setup",
                "description": "I need a secondary 27-inch 4K monitor for data visualization and spreadsheet review at my desk.",
                "category": "Hardware",
                "priority": "Low",
                "status": "Open",
                "requester_name": "Bob Smith",
                "requester_email": "bob.smith@company.com",
                "comments": []
            },
            {
                "title": "Onboarding documentation access issue",
                "description": "New team member unable to access the Notion HR handbook and Benefits folder.",
                "category": "HR",
                "priority": "Medium",
                "status": "Resolved",
                "requester_name": "Clara Davis",
                "requester_email": "clara.davis@company.com",
                "comments": [
                    {"author": "HR Ops", "content": "Granted viewer permissions to HR drive folder."}
                ]
            },
            {
                "title": "Critical production database latency spike",
                "description": "Customer Portal reporting HTTP 504 timeouts due to query locks on Postgres main cluster.",
                "category": "Software",
                "priority": "Urgent",
                "status": "In Progress",
                "requester_name": "DevOps Team",
                "requester_email": "devops@company.com",
                "comments": [
                    {"author": "SRE On-Call", "content": "Identified slow index scan on order_history table. Applying query optimization."}
                ]
            },
            {
                "title": "MacBook Air keyboard spacebar stuck",
                "description": "The spacebar key on my assigned laptop feels sticky and misses keystrokes.",
                "category": "Hardware",
                "priority": "Medium",
                "status": "Open",
                "requester_name": "Evan Wright",
                "requester_email": "evan.wright@company.com",
                "comments": []
            }
        ]

        print("Seeding sample tickets and comments...")
        for data in sample_tickets:
            comments_data = data.pop('comments')
            ticket = Ticket(**data)
            db.session.add(ticket)
            db.session.flush() # get ticket.id

            for c_data in comments_data:
                comment = Comment(ticket_id=ticket.id, **c_data)
                db.session.add(comment)

        db.session.commit()
        print(f"Seeding completed successfully! ({len(sample_tickets)} tickets created)")

if __name__ == '__main__':
    seed_database()
