// Book Chatbot Frontend JavaScript

class BookChatbot {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.sessionId = this.generateSessionId();
        this.isLoading = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFeaturedBooks();
        this.setupAutoResize();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    setupEventListeners() {
        // Send message on Enter key or button click
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // Input suggestions
        document.querySelectorAll('.suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', (e) => {
                const text = e.currentTarget.dataset.text;
                messageInput.value = text;
                messageInput.focus();
            });
        });

        // Clear chat button
        document.getElementById('clearChat').addEventListener('click', () => {
            this.clearChat();
        });

        // New session button
        document.getElementById('newSession').addEventListener('click', () => {
            this.newSession();
        });

        // Modal close
        document.getElementById('modalClose').addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal on outside click
        document.getElementById('bookModal').addEventListener('click', (e) => {
            if (e.target.id === 'bookModal') {
                this.closeModal();
            }
        });

        // Auto-focus input
        messageInput.focus();
    }

    setupAutoResize() {
        const messageInput = document.getElementById('messageInput');
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = messageInput.scrollHeight + 'px';
        });
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message || this.isLoading) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // Show loading indicator
        this.showLoading();

        try {
            const response = await this.callAPI('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            // Hide loading indicator
            this.hideLoading();

            // Add bot response to chat
            this.addMessage(response.response, 'bot', response.intent);

            // Handle special responses (book details, etc.)
            this.handleSpecialResponse(response);

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideLoading();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    }

    async callAPI(endpoint, options = {}) {
        const url = this.apiBaseUrl + endpoint;
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    addMessage(text, sender, intent = null) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.formatMessage(text, intent);

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.getCurrentTime();

        content.appendChild(messageText);
        content.appendChild(messageTime);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    formatMessage(text, intent) {
        // Convert markdown-like formatting to HTML
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');

        // Add clickable book titles
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, (match, title) => {
            return `<span class="book-link" onclick="chatbot.showBookDetails('${title}')">${title}</span>`;
        });

        // Add rating stars
        formatted = formatted.replace(/(\d+(?:\.\d+)?)\/5/g, (match, rating) => {
            return this.createStarRating(parseFloat(rating));
        });

        // Add price highlighting
        formatted = formatted.replace(/\$(\d+(?:\.\d+)?)/g, '<span class="price-highlight">$$$1</span>');

        return formatted;
    }

    createStarRating(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

        let stars = '';
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star star"></i>';
        }
        if (hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt star"></i>';
        }
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="far fa-star star empty"></i>';
        }

        return `<span class="rating-stars">${stars}</span>`;
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    showLoading() {
        this.isLoading = true;
        document.getElementById('loadingOverlay').classList.add('show');
        document.getElementById('sendBtn').disabled = true;
    }

    hideLoading() {
        this.isLoading = false;
        document.getElementById('loadingOverlay').classList.remove('show');
        document.getElementById('sendBtn').disabled = false;
    }

    handleSpecialResponse(response) {
        // Handle different types of responses
        if (response.intent === 'search_book' || response.intent === 'recommend_books') {
            // Extract book titles from response and make them clickable
            this.makeBookTitlesClickable();
        }
    }

    makeBookTitlesClickable() {
        const chatMessages = document.getElementById('chatMessages');
        const lastMessage = chatMessages.lastElementChild;
        if (lastMessage && lastMessage.classList.contains('bot-message')) {
            const messageText = lastMessage.querySelector('.message-text');
            const bookTitles = messageText.querySelectorAll('strong');
            bookTitles.forEach(title => {
                title.classList.add('book-link');
                title.style.cursor = 'pointer';
                title.addEventListener('click', () => {
                    this.showBookDetails(title.textContent);
                });
            });
        }
    }

    async showBookDetails(bookTitle) {
        try {
            this.showLoading();

            const response = await this.callAPI('/book-details', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: bookTitle
                })
            });

            this.hideLoading();
            this.displayBookModal(response);

        } catch (error) {
            console.error('Error fetching book details:', error);
            this.hideLoading();
            this.addMessage(`Sorry, I couldn't find details for "${bookTitle}".`, 'bot');
        }
    }

    displayBookModal(bookData) {
        const modal = document.getElementById('bookModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');

        modalTitle.textContent = bookData.book.title;

        let modalContent = `
            <div class="book-details">
                <div class="book-cover">
                    ${bookData.book.thumbnail_url ? 
                        `<img src="${bookData.book.thumbnail_url}" alt="${bookData.book.title}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">` :
                        '<i class="fas fa-book"></i>'
                    }
                </div>
                <div class="book-info">
                    <h2>${bookData.book.title}</h2>
                    <p><strong>Authors:</strong> ${bookData.book.authors.join(', ')}</p>
                    <p><strong>Publisher:</strong> ${bookData.book.publisher}</p>
                    <p><strong>Published:</strong> ${bookData.book.published_date}</p>
                    <p><strong>Pages:</strong> ${bookData.book.page_count || 'N/A'}</p>
                    <p><strong>Language:</strong> ${bookData.book.language}</p>
                    <p><strong>ISBN-10:</strong> ${bookData.book.isbn_10 || 'N/A'}</p>
                    <p><strong>ISBN-13:</strong> ${bookData.book.isbn_13 || 'N/A'}</p>
        `;

        if (bookData.book.average_rating) {
            modalContent += `
                <div class="rating">
                    <strong>Rating:</strong> ${this.createStarRating(bookData.book.average_rating)} 
                    (${bookData.book.ratings_count} ratings)
                </div>
            `;
        }

        if (bookData.book.price) {
            modalContent += `<p class="price">Price: $${bookData.book.price} ${bookData.book.currency}</p>`;
        }

        modalContent += `
                    <p><strong>Availability:</strong> ${bookData.book.availability}</p>
                </div>
            </div>
        `;

        if (bookData.book.description) {
            modalContent += `
                <div style="margin-top: 2rem;">
                    <h3>Description</h3>
                    <p>${bookData.book.description}</p>
                </div>
            `;
        }

        if (bookData.price_info && bookData.price_info.length > 0) {
            modalContent += `
                <div style="margin-top: 2rem;">
                    <h3>Price Information</h3>
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
            `;
            bookData.price_info.forEach(price => {
                modalContent += `
                    <div style="border: 1px solid #e9ecef; padding: 1rem; border-radius: 8px;">
                        <h4>${price.store_name}</h4>
                        <p><strong>Price:</strong> $${price.price} ${price.currency}</p>
                        <p><strong>Availability:</strong> ${price.availability}</p>
                        <p><strong>Shipping:</strong> ${price.shipping_info}</p>
                        ${price.url ? `<a href="${price.url}" target="_blank" class="book-link">View on ${price.store_name}</a>` : ''}
                    </div>
                `;
            });
            modalContent += `</div></div>`;
        }

        if (bookData.reviews && bookData.reviews.length > 0) {
            modalContent += `
                <div style="margin-top: 2rem;">
                    <h3>Reviews</h3>
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
            `;
            bookData.reviews.slice(0, 3).forEach(review => {
                modalContent += `
                    <div style="border: 1px solid #e9ecef; padding: 1rem; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong>${review.reviewer_name}</strong>
                            <span>${this.createStarRating(review.rating)}</span>
                        </div>
                        <p style="font-size: 0.9rem; color: #666;">${review.review_text.substring(0, 200)}...</p>
                        <p style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">${review.review_date} - ${review.source}</p>
                    </div>
                `;
            });
            modalContent += `</div></div>`;
        }

        modalBody.innerHTML = modalContent;
        modal.classList.add('show');
    }

    closeModal() {
        document.getElementById('bookModal').classList.remove('show');
    }

    async handleQuickAction(action) {
        let message = '';
        
        switch (action) {
            case 'search':
                message = 'Search for books';
                break;
            case 'recommend':
                message = 'Recommend me some books';
                break;
            case 'bestsellers':
                message = 'Show me bestsellers';
                break;
            case 'new-releases':
                message = 'Show me new releases';
                break;
            case 'price':
                message = 'Check book prices';
                break;
            case 'rating':
                message = 'Check book ratings';
                break;
        }

        if (message) {
            document.getElementById('messageInput').value = message;
            this.sendMessage();
        }
    }

    async loadFeaturedBooks() {
        try {
            const response = await this.callAPI('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: 'bestseller',
                    max_results: 3
                })
            });

            this.displayFeaturedBooks(response.books);

        } catch (error) {
            console.error('Error loading featured books:', error);
        }
    }

    displayFeaturedBooks(books) {
        const featuredBooksContainer = document.getElementById('featuredBooks');
        
        books.forEach(book => {
            const bookCard = document.createElement('div');
            bookCard.className = 'book-card';
            bookCard.innerHTML = `
                <h4>${book.title}</h4>
                <p>by ${book.authors.join(', ')}</p>
                <p>${book.published_date}</p>
                ${book.average_rating ? `
                    <div class="rating">
                        ${this.createStarRating(book.average_rating)}
                        <span>(${book.ratings_count} ratings)</span>
                    </div>
                ` : ''}
            `;
            
            bookCard.addEventListener('click', () => {
                this.showBookDetails(book.title);
            });
            
            featuredBooksContainer.appendChild(bookCard);
        });
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-text">
                        Hello! I'm your personal book assistant. I can help you find books, get recommendations, check prices, ratings, and availability. What would you like to know about books today?
                    </div>
                    <div class="message-time">Just now</div>
                </div>
            </div>
        `;
    }

    newSession() {
        this.sessionId = this.generateSessionId();
        this.clearChat();
        this.addMessage('New session started! How can I help you with books today?', 'bot');
    }

    // Utility method to check if API is available
    async checkAPIStatus() {
        try {
            const response = await this.callAPI('/health');
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (response.status === 'healthy') {
                statusDot.style.background = '#28a745';
                statusText.textContent = 'Online';
            } else {
                statusDot.style.background = '#dc3545';
                statusText.textContent = 'Offline';
            }
        } catch (error) {
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            statusDot.style.background = '#dc3545';
            statusText.textContent = 'Offline';
        }
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new BookChatbot();
    
    // Check API status periodically
    setInterval(() => {
        window.chatbot.checkAPIStatus();
    }, 30000);
    
    // Initial API status check
    window.chatbot.checkAPIStatus();
});

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        window.chatbot.checkAPIStatus();
    }
});

// Handle online/offline events
window.addEventListener('online', () => {
    window.chatbot.checkAPIStatus();
});

window.addEventListener('offline', () => {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    statusDot.style.background = '#dc3545';
    statusText.textContent = 'Offline';
});



