import streamlit as st
import pandas as pd
from datetime import datetime, timezone

# Import Flask app, database models, and seed script
from app import app, db
from models import Ticket, Comment
from seed import seed_database

# Page configuration
st.set_page_config(
    page_title="HelpDesk Pro - Enterprise Support",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for Streamlit
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .ticket-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-open { background-color: #dbeafe; color: #1d4ed8; }
    .badge-progress { background-color: #fef3c7; color: #b45309; }
    .badge-resolved { background-color: #dcfce7; color: #15803d; }
    .badge-closed { background-color: #f3f4f6; color: #374151; }
    .badge-urgent { background-color: #fee2e2; color: #b91c1c; }
    .badge-high { background-color: #ffedd5; color: #c2410c; }
    .badge-medium { background-color: #e0e7ff; color: #4338ca; }
    .badge-low { background-color: #f1f5f9; color: #475569; }
</style>
""", unsafe_allow_html=True)

# --- Helper DB Functions inside Flask app context ---

def auto_seed_if_empty():
    """Ensure database has initial sample dataset on first launch"""
    with app.app_context():
        db.create_all()
        if Ticket.query.count() == 0:
            seed_database()

# Trigger auto seed check on script load
auto_seed_if_empty()

def fetch_tickets_data(status="All", priority="All", category="All", search=""):
    with app.app_context():
        query = Ticket.query

        if status != "All":
            query = query.filter_by(status=status)
        if priority != "All":
            query = query.filter_by(priority=priority)
        if category != "All":
            query = query.filter_by(category=category)
        if search.strip():
            pattern = f"%{search.strip()}%"
            query = query.filter(
                (Ticket.title.ilike(pattern)) |
                (Ticket.description.ilike(pattern)) |
                (Ticket.requester_name.ilike(pattern)) |
                (Ticket.requester_email.ilike(pattern))
            )

        tickets = query.order_by(Ticket.created_at.desc()).all()
        return [t.to_dict(include_comments=True) for t in tickets]

def fetch_stats():
    with app.app_context():
        total = Ticket.query.count()
        open_c = Ticket.query.filter_by(status='Open').count()
        prog_c = Ticket.query.filter_by(status='In Progress').count()
        res_c = Ticket.query.filter_by(status='Resolved').count()
        closed_c = Ticket.query.filter_by(status='Closed').count()
        return {'total': total, 'open': open_c, 'in_progress': prog_c, 'resolved': res_c, 'closed': closed_c}

def create_ticket_db(title, description, category, priority, requester_name, requester_email):
    with app.app_context():
        ticket = Ticket(
            title=title.strip(),
            description=description.strip(),
            category=category,
            priority=priority,
            status='Open',
            requester_name=requester_name.strip(),
            requester_email=requester_email.strip()
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket.id

def update_ticket_db(ticket_id, new_status=None, new_priority=None):
    with app.app_context():
        ticket = Ticket.query.get(ticket_id)
        if ticket:
            if new_status:
                ticket.status = new_status
            if new_priority:
                ticket.priority = new_priority
            db.session.commit()

def add_comment_db(ticket_id, author, content):
    with app.app_context():
        comment = Comment(
            ticket_id=ticket_id,
            author=author.strip() or "Support Agent",
            content=content.strip()
        )
        db.session.add(comment)
        db.session.commit()

def delete_ticket_db(ticket_id):
    with app.app_context():
        ticket = Ticket.query.get(ticket_id)
        if ticket:
            db.session.delete(ticket)
            db.session.commit()

# --- Sidebar ---
st.sidebar.markdown("# 🚀 HelpDesk Pro")
st.sidebar.caption("Enterprise Service Management")

st.sidebar.divider()

# Navigation menu
page = st.sidebar.radio("Navigation", ["📋 Ticket Dashboard", "➕ Submit New Ticket", "📊 Analytics & Reports"])

st.sidebar.divider()
st.sidebar.markdown("### 🔍 Search & Filters")
search_query = st.sidebar.text_input("Search Tickets", placeholder="Keyword, requester...")
filter_status = st.sidebar.selectbox("Filter Status", ["All", "Open", "In Progress", "Resolved", "Closed"])
filter_priority = st.sidebar.selectbox("Filter Priority", ["All", "Urgent", "High", "Medium", "Low"])
filter_category = st.sidebar.selectbox("Filter Category", ["All", "IT", "Hardware", "Software", "HR", "General"])

col_sb1, col_sb2 = st.sidebar.columns(2)
with col_sb1:
    if st.button("↺ Reset Filters"):
        st.rerun()
with col_sb2:
    if st.button("⚡ Reset Data"):
        seed_database()
        st.sidebar.success("Demo data reset!")
        st.rerun()

# --- Header & Metrics ---
st.markdown("<div class='main-header'>HelpDesk Pro Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Streamlit Enterprise IT & HR Support Ticketing System</div>", unsafe_allow_html=True)

stats = fetch_stats()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tickets", stats['total'])
col2.metric("Open", stats['open'], delta=None)
col3.metric("In Progress", stats['in_progress'], delta=None)
col4.metric("Resolved", stats['resolved'], delta=None)

st.divider()

# --- Page 1: Ticket Dashboard ---
if page == "📋 Ticket Dashboard":
    tickets = fetch_tickets_data(filter_status, filter_priority, filter_category, search_query)

    st.subheader(f"Support Requests ({len(tickets)})")

    if not tickets:
        st.info("No support tickets match your search filters.")
    else:
        for t in tickets:
            header_label = f"#{t['id']} | [{t['category']}] {t['title']} — ({t['status']} / {t['priority']})"
            
            with st.expander(header_label, expanded=False):
                col_left, col_right = st.columns([2, 1])

                with col_left:
                    st.markdown(f"**Requester:** {t['requester_name']} (`{t['requester_email']}`)")
                    st.markdown(f"**Category:** `{t['category']}` | **Priority:** `{t['priority']}` | **Status:** `{t['status']}`")
                    st.markdown(f"**Created At:** `{t['created_at']}`")
                    st.markdown("#### Description")
                    st.write(t['description'])

                    st.markdown("---")
                    st.markdown(f"#### Activity & Resolution Notes ({len(t.get('comments', []))})")

                    if not t.get('comments'):
                        st.caption("No notes added yet.")
                    else:
                        for c in t['comments']:
                            st.markdown(f"**{c['author']}** *({c['created_at']})*")
                            st.info(c['content'])

                    # Add Comment Form
                    with st.form(key=f"comment_form_{t['id']}"):
                        author = st.text_input("Your Name / Agent", value="Support Agent", key=f"author_{t['id']}")
                        content = st.text_area("Resolution Note / Reply", key=f"content_{t['id']}")
                        submit_comment = st.form_submit_button("Add Note")

                        if submit_comment:
                            if content.strip():
                                add_comment_db(t['id'], author, content)
                                st.success("Note added!")
                                st.rerun()
                            else:
                                st.warning("Note content cannot be empty.")

                with col_right:
                    st.markdown("### ⚙️ Quick Actions")
                    new_st = st.selectbox("Update Status", ["Open", "In Progress", "Resolved", "Closed"], index=["Open", "In Progress", "Resolved", "Closed"].index(t['status']), key=f"status_sel_{t['id']}")
                    new_pr = st.selectbox("Update Priority", ["Low", "Medium", "High", "Urgent"], index=["Low", "Medium", "High", "Urgent"].index(t['priority']), key=f"priority_sel_{t['id']}")

                    if st.button("Save Changes", key=f"save_btn_{t['id']}"):
                        update_ticket_db(t['id'], new_status=new_st, new_priority=new_pr)
                        st.success(f"Ticket #{t['id']} updated!")
                        st.rerun()

                    st.markdown("---")
                    confirm_del = st.checkbox("Confirm Delete", key=f"del_chk_{t['id']}")
                    if st.button("🗑️ Delete Ticket", type="secondary", key=f"del_btn_{t['id']}"):
                        if confirm_del:
                            delete_ticket_db(t['id'])
                            st.success(f"Ticket #{t['id']} deleted.")
                            st.rerun()
                        else:
                            st.warning("Please check 'Confirm Delete' box first.")

# --- Page 2: Submit New Ticket ---
elif page == "➕ Submit New Ticket":
    st.subheader("Submit a New Support Request")

    with st.form("new_ticket_form", clear_on_submit=True):
        title = st.text_input("Ticket Title *", placeholder="e.g. Cannot access corporate VPN from remote network")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            category = st.selectbox("Category", ["IT", "Hardware", "Software", "HR", "General"])
        with col_c2:
            priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "Urgent"], index=1)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            req_name = st.text_input("Your Name *", placeholder="Jane Doe")
        with col_r2:
            req_email = st.text_input("Work Email *", placeholder="jane.doe@company.com")

        description = st.text_area("Issue Description *", rows=5, placeholder="Provide relevant context, error codes, steps to reproduce...")

        submitted = st.form_submit_button("Submit Request", type="primary")

        if submitted:
            if not title.strip() or not req_name.strip() or not req_email.strip() or not description.strip():
                st.error("Please fill in all required fields (*).")
            else:
                new_id = create_ticket_db(title, description, category, priority, req_name, req_email)
                st.success(f"🎉 Ticket #{new_id} submitted successfully!")
                st.rerun()

# --- Page 3: Analytics & Reports ---
elif page == "📊 Analytics & Reports":
    st.subheader("Support Analytics Overview")
    
    tickets_all = fetch_tickets_data("All", "All", "All", "")
    if not tickets_all:
        st.info("No ticket data available for analytics.")
    else:
        df = pd.DataFrame(tickets_all)
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("#### Tickets by Status")
            status_counts = df['status'].value_counts()
            st.bar_chart(status_counts)
            
        with col_a2:
            st.markdown("#### Tickets by Category")
            cat_counts = df['category'].value_counts()
            st.bar_chart(cat_counts)
            
        st.markdown("#### Tickets Summary Table")
        st.dataframe(
            df[['id', 'title', 'category', 'priority', 'status', 'requester_name', 'created_at']],
            use_container_width=True
        )
