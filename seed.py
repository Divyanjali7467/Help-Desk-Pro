import copy
from app import app
from models import db, Ticket, Comment

SAMPLE_TICKETS = [
    {
        "title": "VPN connection drops every 15 minutes",
        "description": "Whenever I connect to the corporate VPN from my home network on Windows 11, the session repeatedly disconnects after 15 minutes of inactivity.",
        "category": "IT",
        "priority": "High",
        "status": "In Progress",
        "requester_name": "Alice Johnson",
        "requester_email": "alice.johnson@company.com",
        "comments": [
            {"author": "IT Helpdesk", "content": "Checking user authentication timeout parameters on VPN gateway."},
            {"author": "Alice Johnson", "content": "Using Cisco AnyConnect client version 4.10."}
        ]
    },
    {
        "title": "Request for dual 27-inch 4K monitor setup",
        "description": "I need a dual monitor arm and two 27-inch 4K displays for financial reporting and spreadsheet analysis at my designated desk.",
        "category": "Hardware",
        "priority": "Low",
        "status": "Open",
        "requester_name": "Bob Smith",
        "requester_email": "bob.smith@company.com",
        "comments": []
    },
    {
        "title": "New hire onboarding documentation & drive access issue",
        "description": "Newly onboarded engineering team members are unable to view the internal Notion wiki and Google Drive onboarding folder.",
        "category": "HR",
        "priority": "Medium",
        "status": "Resolved",
        "requester_name": "Clara Davis",
        "requester_email": "clara.davis@company.com",
        "comments": [
            {"author": "HR Ops", "content": "Updated Google Workspace group permissions for @engineering domain."}
        ]
    },
    {
        "title": "Critical production database query latency spike",
        "description": "Customer Portal API gateway is logging HTTP 504 gateway timeouts due to unindexed queries locking the primary PostgreSQL cluster.",
        "category": "Software",
        "priority": "Urgent",
        "status": "In Progress",
        "requester_name": "DevOps On-Call",
        "requester_email": "devops@company.com",
        "comments": [
            {"author": "SRE Team", "content": "Identified missing composite index on order_history table. Executing migration."},
            {"author": "Lead Architect", "content": "Query response times back down to under 50ms."}
        ]
    },
    {
        "title": "MacBook Pro keyboard spacebar stuck",
        "description": "The physical spacebar key on my assigned M2 MacBook Pro is sticking and missing keystrokes during daily use.",
        "category": "Hardware",
        "priority": "Medium",
        "status": "Open",
        "requester_name": "Evan Wright",
        "requester_email": "evan.wright@company.com",
        "comments": []
    },
    {
        "title": "Payroll Portal direct deposit routing update error",
        "description": "Attempting to update bank routing information on Workday Payroll yields an internal validation error 4032.",
        "category": "HR",
        "priority": "High",
        "status": "Resolved",
        "requester_name": "Grace Hopper",
        "requester_email": "grace.hopper@company.com",
        "comments": [
            {"author": "Payroll Admin", "content": "Manually cleared routing lock in Workday portal. User verified successful submission."}
        ]
    },
    {
        "title": "Request for JetBrains IntelliJ IDEA Ultimate License",
        "description": "Requesting a standalone developer subscription for IntelliJ IDEA Ultimate for backend Java service development.",
        "category": "Software",
        "priority": "Low",
        "status": "Open",
        "requester_name": "David Miller",
        "requester_email": "david.miller@company.com",
        "comments": []
    },
    {
        "title": "Conference Room B AV display & microphone failure",
        "description": "The ceiling microphone array and main HDMI display in Conference Room B are not broadcasting audio during Zoom meetings.",
        "category": "IT",
        "priority": "Urgent",
        "status": "Open",
        "requester_name": "Facilities Team",
        "requester_email": "facilities@company.com",
        "comments": [
            {"author": "IT AV Support", "content": "Dispatched technician to check AV receiver and switch box."}
        ]
    }
]

def seed_database():
    with app.app_context():
        print("Resetting and populating sample dataset...")
        db.drop_all()
        db.create_all()

        tickets_data = copy.deepcopy(SAMPLE_TICKETS)
        for data in tickets_data:
            comments_data = data.pop('comments', [])
            ticket = Ticket(**data)
            db.session.add(ticket)
            db.session.flush()

            for c_data in comments_data:
                comment = Comment(ticket_id=ticket.id, **c_data)
                db.session.add(comment)

        db.session.commit()
        print(f"Sample dataset loaded successfully! ({len(SAMPLE_TICKETS)} tickets created)")

if __name__ == '__main__':
    seed_database()
