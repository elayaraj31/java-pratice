// Blog Application JavaScript

class BlogApp {
    constructor() {
        this.currentView = 'home';
        this.editingPostId = null;
        this.deletePostId = null;
        this.posts = [];
        
        this.init();
    }

    init() {
        // Initialize with sample data if localStorage is empty
        this.initializeData();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set default date to today
        this.setDefaultDate();
        
        // Show home view initially
        this.showView('home');
    }

    initializeData() {
        const existingData = localStorage.getItem('blogPosts');
        
        if (!existingData) {
            // Use the provided initial data
            const initialData = [
                {
                    "id": "1",
                    "title": "Getting Started with Nuxt.js",
                    "description": "Learn how to build modern web applications with Nuxt.js, the intuitive Vue.js framework. This comprehensive guide covers everything from setup to deployment.",
                    "image": "",
                    "date": "2025-09-10",
                    "createdAt": "2025-09-10T08:00:00Z"
                },
                {
                    "id": "2", 
                    "title": "Vue.js Best Practices",
                    "description": "Discover the most effective patterns and practices for building scalable Vue.js applications. From component architecture to state management.",
                    "image": "",
                    "date": "2025-09-08",
                    "createdAt": "2025-09-08T14:30:00Z"
                },
                {
                    "id": "3",
                    "title": "Modern Web Development",
                    "description": "Explore the latest trends and technologies in web development. Learn about JAMstack, serverless architecture, and modern deployment strategies.",
                    "image": "",
                    "date": "2025-09-05",
                    "createdAt": "2025-09-05T11:15:00Z"
                }
            ];
            
            localStorage.setItem('blogPosts', JSON.stringify(initialData));
            this.posts = initialData;
        } else {
            this.posts = JSON.parse(existingData);
        }
    }

    setupEventListeners() {
        // Add form submission
        const addForm = document.getElementById('add-form');
        if (addForm) {
            addForm.addEventListener('submit', (e) => this.handleAddPost(e));
        }

        // Edit form submission
        const editForm = document.getElementById('edit-form');
        if (editForm) {
            editForm.addEventListener('submit', (e) => this.handleEditPost(e));
        }

        // Image upload handlers
        const imageInput = document.getElementById('image');
        if (imageInput) {
            imageInput.addEventListener('change', (e) => this.handleImageUpload(e, 'image-preview'));
        }

        const editImageInput = document.getElementById('edit-image');
        if (editImageInput) {
            editImageInput.addEventListener('change', (e) => this.handleImageUpload(e, 'edit-image-preview'));
        }

        // Modal backdrop click
        const modalBackdrop = document.querySelector('.modal-backdrop');
        if (modalBackdrop) {
            modalBackdrop.addEventListener('click', () => this.closeDeleteModal());
        }

        // Confirm delete button
        const confirmDeleteBtn = document.getElementById('confirm-delete');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', () => this.confirmDelete());
        }
    }

    setDefaultDate() {
        const today = new Date().toISOString().split('T')[0];
        const dateInput = document.getElementById('date');
        const editDateInput = document.getElementById('edit-date');
        
        if (dateInput) dateInput.value = today;
        if (editDateInput) editDateInput.value = today;
    }

    showView(viewName, postId = null) {
        try {
            // Hide all views
            const views = document.querySelectorAll('.view');
            views.forEach(view => {
                view.classList.add('hidden');
                view.classList.remove('fade-in');
            });

            // Show target view
            const targetView = document.getElementById(`${viewName}-view`);
            if (targetView) {
                targetView.classList.remove('hidden');
                targetView.classList.add('fade-in');
            }

            this.currentView = viewName;

            // Handle specific view logic
            switch (viewName) {
                case 'home':
                    this.renderPosts();
                    break;
                case 'add':
                    this.resetAddForm();
                    break;
                case 'edit':
                    if (postId) {
                        this.editingPostId = postId;
                        this.populateEditForm(postId);
                    }
                    break;
                case 'detail':
                    if (postId) {
                        this.renderPostDetail(postId);
                    }
                    break;
            }
        } catch (error) {
            console.error('Error in showView:', error);
            this.showToast('Navigation error occurred', 'error');
        }
    }

    renderPosts() {
        try {
            const postsGrid = document.getElementById('posts-grid');
            const emptyState = document.getElementById('empty-state');

            if (!postsGrid || !emptyState) {
                console.error('Required elements not found');
                return;
            }

            if (this.posts.length === 0) {
                postsGrid.style.display = 'none';
                emptyState.classList.remove('hidden');
                return;
            }

            emptyState.classList.add('hidden');
            postsGrid.style.display = 'grid';

            // Sort posts by date (newest first)
            const sortedPosts = [...this.posts].sort((a, b) => new Date(b.date) - new Date(a.date));

            postsGrid.innerHTML = sortedPosts.map(post => `
                <div class="blog-card" onclick="window.app.showView('detail', '${post.id}')" tabindex="0">
                    <div class="blog-card-image ${post.image ? '' : 'no-image'}">
                        ${post.image ? 
                            `<img src="${post.image}" alt="${this.escapeHtml(post.title)}">` : 
                            '<span>No image</span>'
                        }
                    </div>
                    <div class="blog-card-content">
                        <h3 class="blog-card-title">${this.escapeHtml(post.title)}</h3>
                        <div class="blog-card-meta">
                            <span class="blog-card-date">${this.formatDate(post.date)}</span>
                        </div>
                        <p class="blog-card-description">${this.escapeHtml(post.description)}</p>
                        <div class="blog-card-actions" onclick="event.stopPropagation()">
                            <button class="btn btn--small btn--outline" onclick="window.app.showView('edit', '${post.id}')">
                                Edit
                            </button>
                            <button class="btn btn--small btn--danger" onclick="window.app.showDeleteModal('${post.id}')">
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error rendering posts:', error);
            this.showToast('Error loading posts', 'error');
        }
    }

    renderPostDetail(postId) {
        try {
            const post = this.posts.find(p => p.id === postId);
            if (!post) {
                this.showView('home');
                return;
            }

            const detailContainer = document.querySelector('.post-detail');
            if (!detailContainer) {
                console.error('Post detail container not found');
                return;
            }

            detailContainer.innerHTML = `
                <div class="post-detail-header">
                    <h1 class="post-detail-title">${this.escapeHtml(post.title)}</h1>
                    <div class="post-detail-meta">
                        <span class="post-detail-date">${this.formatDate(post.date)}</span>
                    </div>
                    <div class="post-detail-actions">
                        <button class="btn btn--outline" onclick="window.app.showView('home')">← Back to Posts</button>
                        <button class="btn btn--outline" onclick="window.app.showView('edit', '${post.id}')">Edit Post</button>
                        <button class="btn btn--danger" onclick="window.app.showDeleteModal('${post.id}')">Delete Post</button>
                    </div>
                </div>
                ${post.image ? `<img src="${post.image}" alt="${this.escapeHtml(post.title)}" class="post-detail-image">` : ''}
                <div class="post-detail-content">
                    <p>${this.escapeHtml(post.description).replace(/\n/g, '<br>')}</p>
                </div>
            `;
        } catch (error) {
            console.error('Error rendering post detail:', error);
            this.showToast('Error loading post details', 'error');
        }
    }

    resetAddForm() {
        try {
            const form = document.getElementById('add-form');
            if (form) {
                form.reset();
            }
            this.setDefaultDate();
            this.hideImagePreview('image-preview');
            this.clearErrors();
        } catch (error) {
            console.error('Error resetting add form:', error);
        }
    }

    populateEditForm(postId) {
        try {
            const post = this.posts.find(p => p.id === postId);
            if (!post) return;

            const titleInput = document.getElementById('edit-title');
            const descInput = document.getElementById('edit-description');
            const dateInput = document.getElementById('edit-date');

            if (titleInput) titleInput.value = post.title;
            if (descInput) descInput.value = post.description;
            if (dateInput) dateInput.value = post.date;

            if (post.image) {
                this.showImagePreview('edit-image-preview', post.image, 'Current image');
            } else {
                this.hideImagePreview('edit-image-preview');
            }

            this.clearErrors();
        } catch (error) {
            console.error('Error populating edit form:', error);
            this.showToast('Error loading post for editing', 'error');
        }
    }

    handleAddPost(e) {
        e.preventDefault();
        
        try {
            const formData = this.getFormData('add');
            
            if (!this.validateForm(formData, 'add')) {
                return;
            }

            const newPost = {
                id: this.generateId(),
                title: formData.title,
                description: formData.description,
                image: formData.image,
                date: formData.date,
                createdAt: new Date().toISOString()
            };

            this.posts.push(newPost);
            this.savePosts();
            this.showToast('Post created successfully!');
            this.showView('home');
        } catch (error) {
            console.error('Error adding post:', error);
            this.showToast('Error creating post', 'error');
        }
    }

    handleEditPost(e) {
        e.preventDefault();
        
        try {
            const formData = this.getFormData('edit');
            
            if (!this.validateForm(formData, 'edit')) {
                return;
            }

            const postIndex = this.posts.findIndex(p => p.id === this.editingPostId);
            if (postIndex === -1) return;

            this.posts[postIndex] = {
                ...this.posts[postIndex],
                title: formData.title,
                description: formData.description,
                image: formData.image,
                date: formData.date
            };

            this.savePosts();
            this.showToast('Post updated successfully!');
            this.showView('home');
        } catch (error) {
            console.error('Error editing post:', error);
            this.showToast('Error updating post', 'error');
        }
    }

    getFormData(type) {
        const prefix = type === 'add' ? '' : 'edit-';
        
        const titleEl = document.getElementById(`${prefix}title`);
        const descEl = document.getElementById(`${prefix}description`);
        const dateEl = document.getElementById(`${prefix}date`);
        
        return {
            title: titleEl ? titleEl.value.trim() : '',
            description: descEl ? descEl.value.trim() : '',
            image: this.getImageFromPreview(`${prefix}image-preview`),
            date: dateEl ? dateEl.value : ''
        };
    }

    validateForm(formData, type) {
        let isValid = true;
        this.clearErrors();

        if (!formData.title) {
            this.showError(`${type === 'add' ? '' : 'edit-'}title-error`, 'Title is required');
            isValid = false;
        } else if (formData.title.length > 100) {
            this.showError(`${type === 'add' ? '' : 'edit-'}title-error`, 'Title must be less than 100 characters');
            isValid = false;
        }

        if (!formData.description) {
            this.showError(`${type === 'add' ? '' : 'edit-'}description-error`, 'Description is required');
            isValid = false;
        } else if (formData.description.length > 500) {
            this.showError(`${type === 'add' ? '' : 'edit-'}description-error`, 'Description must be less than 500 characters');
            isValid = false;
        }

        if (!formData.date) {
            this.showError(`${type === 'add' ? '' : 'edit-'}date-error`, 'Date is required');
            isValid = false;
        }

        return isValid;
    }

    showError(errorId, message) {
        const errorElement = document.getElementById(errorId);
        if (!errorElement) return;
        
        const inputElement = errorElement.previousElementSibling;
        
        errorElement.textContent = message;
        errorElement.classList.add('show');
        if (inputElement) inputElement.classList.add('error');
    }

    clearErrors() {
        const errorElements = document.querySelectorAll('.error-message');
        const inputElements = document.querySelectorAll('.form-control');
        
        errorElements.forEach(el => {
            el.classList.remove('show');
            el.textContent = '';
        });
        
        inputElements.forEach(el => el.classList.remove('error'));
    }

    handleImageUpload(e, previewId) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showToast('Please select a valid image file', 'error');
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.showToast('Image size must be less than 5MB', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.showImagePreview(previewId, e.target.result, file.name);
        };
        reader.readAsDataURL(file);
    }

    showImagePreview(previewId, src, filename) {
        const preview = document.getElementById(previewId);
        if (!preview) return;
        
        preview.innerHTML = `
            <img src="${src}" alt="Preview">
            <div class="image-preview-info">
                <span>${filename}</span>
                <button type="button" class="btn btn--small" onclick="window.app.removeImage('${previewId}')">Remove</button>
            </div>
        `;
        preview.classList.add('show');
    }

    hideImagePreview(previewId) {
        const preview = document.getElementById(previewId);
        if (!preview) return;
        
        preview.innerHTML = '';
        preview.classList.remove('show');
    }

    removeImage(previewId) {
        this.hideImagePreview(previewId);
        
        // Clear the file input
        const inputId = previewId.replace('-preview', '');
        const input = document.getElementById(inputId);
        if (input) input.value = '';
    }

    getImageFromPreview(previewId) {
        const preview = document.getElementById(previewId);
        if (!preview) return '';
        
        const img = preview.querySelector('img');
        return img ? img.src : '';
    }

    showDeleteModal(postId) {
        this.deletePostId = postId;
        const modal = document.getElementById('delete-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    closeDeleteModal() {
        const modal = document.getElementById('delete-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
        this.deletePostId = null;
    }

    confirmDelete() {
        if (!this.deletePostId) return;

        try {
            const postIndex = this.posts.findIndex(p => p.id === this.deletePostId);
            if (postIndex !== -1) {
                this.posts.splice(postIndex, 1);
                this.savePosts();
                this.showToast('Post deleted successfully!');
                
                // If we're viewing the deleted post, go back to home
                if (this.currentView === 'detail') {
                    this.showView('home');
                } else if (this.currentView === 'home') {
                    this.renderPosts();
                }
            }

            this.closeDeleteModal();
        } catch (error) {
            console.error('Error deleting post:', error);
            this.showToast('Error deleting post', 'error');
        }
    }

    savePosts() {
        try {
            localStorage.setItem('blogPosts', JSON.stringify(this.posts));
        } catch (error) {
            console.error('Error saving posts:', error);
            this.showToast('Error saving data', 'error');
        }
    }

    generateId() {
        return Date.now().toString() + Math.random().toString(36).substr(2, 9);
    }

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (error) {
            return dateString;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toast-message');
        
        if (!toast || !toastMessage) return;
        
        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.remove('hidden');
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 300);
        }, 3000);
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.app = new BlogApp();
        console.log('Blog app initialized successfully');
    } catch (error) {
        console.error('Failed to initialize blog app:', error);
    }
});

// Add keyboard navigation support
document.addEventListener('keydown', (e) => {
    try {
        // Close modal on Escape key
        if (e.key === 'Escape') {
            const modal = document.getElementById('delete-modal');
            if (modal && !modal.classList.contains('hidden')) {
                window.app.closeDeleteModal();
            }
        }
        
        // Enter key on blog cards
        if (e.key === 'Enter' && e.target.classList.contains('blog-card')) {
            e.target.click();
        }
    } catch (error) {
        console.error('Keyboard event error:', error);
    }
});

// Handle browser back/forward buttons (basic SPA behavior)
window.addEventListener('popstate', () => {
    try {
        if (window.app) {
            window.app.showView('home');
        }
    } catch (error) {
        console.error('Popstate event error:', error);
    }
});