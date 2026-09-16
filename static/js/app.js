/**
 * HelpDesk Pro - Single Page Application Frontend Script
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    let currentTickets = [];
    let activeTicketId = null;

    // --- DOM Elements ---
    const statTotal = document.getElementById('statTotal');
    const statOpen = document.getElementById('statOpen');
    const statProgress = document.getElementById('statProgress');
    const statResolved = document.getElementById('statResolved');

    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');

    const ticketsGrid = document.getElementById('ticketsGrid');
    const ticketCountBadge = document.getElementById('ticketCountBadge');
    const emptyState = document.getElementById('emptyState');

    // Create Modal Elements
    const openCreateModalBtn = document.getElementById('openCreateModalBtn');
    const createTicketModal = document.getElementById('createTicketModal');
    const closeCreateModalBtn = document.getElementById('closeCreateModalBtn');
    const cancelCreateBtn = document.getElementById('cancelCreateBtn');
    const createTicketForm = document.getElementById('createTicketForm');

    // Detail Modal Elements
    const ticketDetailModal = document.getElementById('ticketDetailModal');
    const closeDetailModalBtn = document.getElementById('closeDetailModalBtn');
    const detailTicketId = document.getElementById('detailTicketId');
    const detailTicketTitle = document.getElementById('detailTicketTitle');
    const detailCategoryBadge = document.getElementById('detailCategoryBadge');
    const detailPriorityBadge = document.getElementById('detailPriorityBadge');
    const detailStatusBadge = document.getElementById('detailStatusBadge');
    const detailAvatar = document.getElementById('detailAvatar');
    const detailRequesterName = document.getElementById('detailRequesterName');
    const detailRequesterEmail = document.getElementById('detailRequesterEmail');
    const detailCreatedAt = document.getElementById('detailCreatedAt');
    const detailDescription = document.getElementById('detailDescription');
    const detailCommentCount = document.getElementById('detailCommentCount');
    const commentsList = document.getElementById('commentsList');

    const detailStatusSelect = document.getElementById('detailStatusSelect');
    const detailPrioritySelect = document.getElementById('detailPrioritySelect');
    const saveTicketChangesBtn = document.getElementById('saveTicketChangesBtn');
    const deleteTicketBtn = document.getElementById('deleteTicketBtn');
    const addCommentForm = document.getElementById('addCommentForm');

    const toastContainer = document.getElementById('toastContainer');

    // --- Init ---
    init();

    function init() {
        loadStats();
        loadTickets();
        setupEventListeners();
    }

    // --- Event Listeners ---
    function setupEventListeners() {
        // Filters & Search
        let searchTimeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(loadTickets, 300);
        });

        statusFilter.addEventListener('change', loadTickets);
        priorityFilter.addEventListener('change', loadTickets);
        categoryFilter.addEventListener('change', loadTickets);

        resetFiltersBtn.addEventListener('click', () => {
            searchInput.value = '';
            statusFilter.value = 'All';
            priorityFilter.value = 'All';
            categoryFilter.value = 'All';
            loadTickets();
        });

        // Modals toggle
        openCreateModalBtn.addEventListener('click', () => openModal(createTicketModal));
        closeCreateModalBtn.addEventListener('click', () => closeModal(createTicketModal));
        cancelCreateBtn.addEventListener('click', () => closeModal(createTicketModal));

        closeDetailModalBtn.addEventListener('click', () => closeModal(ticketDetailModal));

        // Submit new ticket
        createTicketForm.addEventListener('submit', handleCreateTicket);

        // Management Actions
        saveTicketChangesBtn.addEventListener('click', handleUpdateTicket);
        deleteTicketBtn.addEventListener('click', handleDeleteTicket);
        addCommentForm.addEventListener('submit', handleAddComment);

        // Backdrop click to close
        window.addEventListener('click', (e) => {
            if (e.target === createTicketModal) closeModal(createTicketModal);
            if (e.target === ticketDetailModal) closeModal(ticketDetailModal);
        });
    }

    // --- API Calls ---

    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            if (!res.ok) throw new Error('Failed to fetch stats');
            const data = await res.json();

            statTotal.textContent = data.total;
            statOpen.textContent = data.open;
            statProgress.textContent = data.in_progress;
            statResolved.textContent = data.resolved;
        } catch (err) {
            console.error('Error loading stats:', err);
        }
    }

    async function loadTickets() {
        const queryParams = new URLSearchParams();
        if (statusFilter.value !== 'All') queryParams.append('status', statusFilter.value);
        if (priorityFilter.value !== 'All') queryParams.append('priority', priorityFilter.value);
        if (categoryFilter.value !== 'All') queryParams.append('category', categoryFilter.value);
        if (searchInput.value.trim()) queryParams.append('search', searchInput.value.trim());

        try {
            const res = await fetch(`/api/tickets?${queryParams.toString()}`);
            if (!res.ok) throw new Error('Failed to fetch tickets');
            currentTickets = await res.json();
            renderTickets(currentTickets);
        } catch (err) {
            console.error('Error loading tickets:', err);
            showToast('Error loading tickets from server', 'error');
        }
    }

    async function handleCreateTicket(e) {
        e.preventDefault();

        const newTicket = {
            title: document.getElementById('ticketTitle').value,
            category: document.getElementById('ticketCategory').value,
            priority: document.getElementById('ticketPriority').value,
            requester_name: document.getElementById('requesterName').value,
            requester_email: document.getElementById('requesterEmail').value,
            description: document.getElementById('ticketDescription').value
        };

        try {
            const res = await fetch('/api/tickets', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newTicket)
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Failed to create ticket');
            }

            const created = await res.json();
            showToast(`Ticket #${created.id} submitted successfully!`, 'success');
            createTicketForm.reset();
            closeModal(createTicketModal);
            loadTickets();
            loadStats();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function openTicketDetail(ticketId) {
        activeTicketId = ticketId;
        try {
            const res = await fetch(`/api/tickets/${ticketId}`);
            if (!res.ok) throw new Error('Ticket not found');
            const ticket = await res.json();

            // Populate Modal Content
            detailTicketId.textContent = `#${ticket.id}`;
            detailTicketTitle.textContent = ticket.title;
            detailCategoryBadge.textContent = ticket.category;
            
            // Badges
            updateBadgeClasses(detailStatusBadge, ticket.status, 'status');
            updateBadgeClasses(detailPriorityBadge, ticket.priority, 'priority');

            // Requester Avatar Initials
            const initials = ticket.requester_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
            detailAvatar.textContent = initials || 'U';

            detailRequesterName.textContent = ticket.requester_name;
            detailRequesterEmail.textContent = ticket.requester_email;
            detailCreatedAt.textContent = formatDate(ticket.created_at);
            detailDescription.textContent = ticket.description;

            // Form Selects
            detailStatusSelect.value = ticket.status;
            detailPrioritySelect.value = ticket.priority;

            // Comments
            renderComments(ticket.comments || []);

            openModal(ticketDetailModal);
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function handleUpdateTicket() {
        if (!activeTicketId) return;

        const payload = {
            status: detailStatusSelect.value,
            priority: detailPrioritySelect.value
        };

        try {
            const res = await fetch(`/api/tickets/${activeTicketId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error('Failed to update ticket');

            const updated = await res.json();
            showToast(`Ticket #${activeTicketId} updated.`, 'success');
            
            updateBadgeClasses(detailStatusBadge, updated.status, 'status');
            updateBadgeClasses(detailPriorityBadge, updated.priority, 'priority');

            loadTickets();
            loadStats();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function handleDeleteTicket() {
        if (!activeTicketId) return;
        if (!confirm(`Are you sure you want to delete Ticket #${activeTicketId}?`)) return;

        try {
            const res = await fetch(`/api/tickets/${activeTicketId}`, {
                method: 'DELETE'
            });

            if (!res.ok) throw new Error('Failed to delete ticket');

            showToast(`Ticket #${activeTicketId} deleted successfully.`, 'success');
            closeModal(ticketDetailModal);
            loadTickets();
            loadStats();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function handleAddComment(e) {
        e.preventDefault();
        if (!activeTicketId) return;

        const authorInput = document.getElementById('commentAuthor');
        const contentInput = document.getElementById('commentContent');

        const payload = {
            author: authorInput.value.trim() || 'Support Agent',
            content: contentInput.value.trim()
        };

        try {
            const res = await fetch(`/api/tickets/${activeTicketId}/comments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error('Failed to post comment');

            contentInput.value = '';
            showToast('Note added to ticket.', 'success');
            
            // Reload ticket details to update comments list
            openTicketDetail(activeTicketId);
            loadTickets();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // --- Rendering Helpers ---

    function renderTickets(tickets) {
        ticketsGrid.innerHTML = '';
        ticketCountBadge.textContent = tickets.length;

        if (tickets.length === 0) {
            emptyState.classList.remove('hidden');
            return;
        }

        emptyState.classList.add('hidden');

        tickets.forEach(ticket => {
            const card = document.createElement('div');
            card.className = 'ticket-card';
            card.innerHTML = `
                <div>
                    <div class="ticket-card-header">
                        <span class="ticket-id">#${ticket.id}</span>
                        <div class="badges-group">
                            <span class="category-tag">${escapeHtml(ticket.category)}</span>
                            <span class="badge ${getPriorityBadgeClass(ticket.priority)}">${escapeHtml(ticket.priority)}</span>
                            <span class="badge ${getStatusBadgeClass(ticket.status)}">${escapeHtml(ticket.status)}</span>
                        </div>
                    </div>
                    <div class="ticket-card-body">
                        <h4>${escapeHtml(ticket.title)}</h4>
                        <p>${escapeHtml(ticket.description)}</p>
                    </div>
                </div>
                <div class="ticket-card-footer">
                    <span class="requester-name">👤 ${escapeHtml(ticket.requester_name)}</span>
                    <span class="comments-count">💬 ${ticket.comment_count}</span>
                </div>
            `;

            card.addEventListener('click', () => openTicketDetail(ticket.id));
            ticketsGrid.appendChild(card);
        });
    }

    function renderComments(comments) {
        commentsList.innerHTML = '';
        detailCommentCount.textContent = comments.length;

        if (comments.length === 0) {
            commentsList.innerHTML = '<div class="text-muted" style="font-size: 13px; font-style: italic;">No resolution notes yet.</div>';
            return;
        }

        comments.forEach(c => {
            const item = document.createElement('div');
            item.className = 'comment-item';
            item.innerHTML = `
                <div class="comment-header">
                    <span class="comment-author">${escapeHtml(c.author)}</span>
                    <span class="comment-time">${formatDate(c.created_at)}</span>
                </div>
                <div class="comment-body">${escapeHtml(c.content)}</div>
            `;
            commentsList.appendChild(item);
        });
    }

    // --- Utility Functions ---

    function openModal(modal) {
        modal.classList.remove('hidden');
    }

    function closeModal(modal) {
        modal.classList.add('hidden');
    }

    function getStatusBadgeClass(status) {
        switch (status) {
            case 'Open': return 'badge-status-open';
            case 'In Progress': return 'badge-status-in-progress';
            case 'Resolved': return 'badge-status-resolved';
            case 'Closed': return 'badge-status-closed';
            default: return 'badge-status-open';
        }
    }

    function getPriorityBadgeClass(priority) {
        switch (priority) {
            case 'Urgent': return 'badge-priority-urgent';
            case 'High': return 'badge-priority-high';
            case 'Medium': return 'badge-priority-medium';
            case 'Low': return 'badge-priority-low';
            default: return 'badge-priority-medium';
        }
    }

    function updateBadgeClasses(element, text, type) {
        element.textContent = text;
        element.className = 'badge';
        if (type === 'status') element.classList.add(getStatusBadgeClass(text));
        if (type === 'priority') element.classList.add(getPriorityBadgeClass(text));
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3500);
    }
});
