/**
 * Document Library JavaScript
 * 
 * This script provides enhanced functionality for the document library page,
 * including view switching, filtering, and improved document interaction.
 */

class DocumentLibrary {
    constructor() {
        // Initialize when document is ready
        document.addEventListener('DOMContentLoaded', () => this.initialize());
        
        // View state
        this.currentView = 'grid'; // 'grid' or 'list'
        this.filters = {
            search: '',
            types: ['all']
        };
    }
    
    initialize() {
        // Set up view switchers
        this.setupViewSwitchers();
        
        // Set up type filters
        this.setupTypeFilters();
        
        // Set up document manager integration
        this.setupDocumentManagerIntegration();
    }
    
    setupViewSwitchers() {
        const viewButtons = document.querySelectorAll('.view-btn');
        
        viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remove active class from all buttons
                viewButtons.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                btn.classList.add('active');
                
                // Update current view
                this.currentView = btn.getAttribute('data-view');
                
                // Update document list view
                this.updateDocumentListView();
            });
        });
    }
    
    setupTypeFilters() {
        const typeCheckboxes = document.querySelectorAll('.filter-type');
        const allTypeCheckbox = document.getElementById('typeAll');
        
        typeCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (checkbox.id === 'typeAll' && checkbox.checked) {
                    // If "All Types" is checked, uncheck others
                    typeCheckboxes.forEach(cb => {
                        if (cb.id !== 'typeAll') {
                            cb.checked = false;
                        }
                    });
                    
                    this.filters.types = ['all'];
                } else {
                    // If any other type is checked, uncheck "All Types"
                    if (checkbox.checked && allTypeCheckbox.checked) {
                        allTypeCheckbox.checked = false;
                    }
                    
                    // Update filters
                    this.filters.types = Array.from(typeCheckboxes)
                        .filter(cb => cb.checked)
                        .map(cb => cb.value);
                    
                    // If no filters selected, select "All Types"
                    if (this.filters.types.length === 0) {
                        allTypeCheckbox.checked = true;
                        this.filters.types = ['all'];
                    }
                }
                
                // Apply filters
                this.applyFilters();
            });
        });
        
        // Set up search filter
        const searchInput = document.getElementById('documentSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filters.search = e.target.value.trim().toLowerCase();
                this.applyFilters();
            });
        }
    }
    
    setupDocumentManagerIntegration() {
        // Wait for document manager to be initialized
        const checkDocumentManager = setInterval(() => {
            if (window.documentManager) {
                clearInterval(checkDocumentManager);
                
                // Override document list rendering
                const originalRenderDocumentList = window.documentManager.renderDocumentList;
                
                window.documentManager.renderDocumentList = () => {
                    originalRenderDocumentList.call(window.documentManager);
                    
                    // Apply our custom view
                    this.updateDocumentListView();
                    
                    // Apply filters
                    this.applyFilters();
                };
            }
        }, 100);
    }
    
    updateDocumentListView() {
        const listContainer = document.getElementById('documentList');
        
        if (!listContainer) return;
        
        // Update container class
        if (this.currentView === 'grid') {
            listContainer.classList.remove('document-list-view');
            listContainer.classList.add('document-grid');
        } else {
            listContainer.classList.remove('document-grid');
            listContainer.classList.add('document-list-view');
        }
        
        // Update document cards if needed
        const cards = listContainer.querySelectorAll('.document-card');
        
        cards.forEach(card => {
            if (this.currentView === 'list') {
                card.classList.add('list-view');
            } else {
                card.classList.remove('list-view');
            }
        });
    }
    
    applyFilters() {
        const listContainer = document.getElementById('documentList');
        
        if (!listContainer || !window.documentManager) return;
        
        const cards = listContainer.querySelectorAll('.document-card');
        
        cards.forEach(card => {
            const docId = card.getAttribute('data-id');
            const doc = window.documentManager.documents.find(d => d.id === docId);
            
            if (doc) {
                let visible = true;
                
                // Apply type filter
                if (!this.filters.types.includes('all')) {
                    if (!this.filters.types.includes(doc.type)) {
                        const isOther = !['pdf', 'text', 'image'].includes(doc.type);
                        
                        if (!(isOther && this.filters.types.includes('other'))) {
                            visible = false;
                        }
                    }
                }
                
                // Apply search filter
                if (visible && this.filters.search) {
                    const nameMatch = doc.name.toLowerCase().includes(this.filters.search);
                    const tagsMatch = (doc.tags || []).some(tag => tag.toLowerCase().includes(this.filters.search));
                    
                    if (!nameMatch && !tagsMatch) {
                        visible = false;
                    }
                }
                
                card.style.display = visible ? '' : 'none';
            }
        });
    }
}

// Initialize document library
const documentLibrary = new DocumentLibrary();
