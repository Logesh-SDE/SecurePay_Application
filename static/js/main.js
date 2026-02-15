// Flash message auto-hide
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// OTP input auto-formatting
const otpInput = document.getElementById('otp');
if (otpInput) {
    otpInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
}

// Mobile number validation
const mobileInputs = document.querySelectorAll('input[type="tel"]');
mobileInputs.forEach(input => {
    input.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
});

// Table search functionality
function addTableSearch() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        const searchContainer = document.createElement('div');
        searchContainer.style.marginBottom = '1rem';
        searchContainer.innerHTML = `
            <input type="text" 
                   placeholder="Search..." 
                   style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px;"
                   class="table-search">
        `;
        
        table.parentElement.insertBefore(searchContainer, table);
        
        const searchInput = searchContainer.querySelector('.table-search');
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = tbody.querySelectorAll('tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    });
}

// Initialize table search on pages with tables
if (document.querySelector('.data-table')) {
    addTableSearch();
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form validation enhancement
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        const inputs = this.querySelectorAll('input[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderColor = '#dc3545';
            } else {
                input.style.borderColor = '#e0e0e0';
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('Please fill in all required fields');
        }
    });
});

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    });
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'alert alert-success';
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 2000);
}

// Add copy functionality to transaction IDs
document.querySelectorAll('.data-table code').forEach(code => {
    code.style.cursor = 'pointer';
    code.title = 'Click to copy';
    code.addEventListener('click', function() {
        copyToClipboard(this.textContent);
    });
});

// Mobile menu toggle (for responsive design)
function createMobileMenu() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    const menuToggle = document.createElement('button');
    menuToggle.className = 'mobile-menu-toggle';
    menuToggle.innerHTML = '☰';
    menuToggle.style.display = 'none';
    menuToggle.style.background = 'none';
    menuToggle.style.border = 'none';
    menuToggle.style.color = 'white';
    menuToggle.style.fontSize = '24px';
    menuToggle.style.cursor = 'pointer';
    
    const navMenu = navbar.querySelector('.nav-menu');
    if (navMenu) {
        navbar.querySelector('.nav-container').insertBefore(menuToggle, navMenu);
        
        menuToggle.addEventListener('click', () => {
            navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
        });
        
        // Show menu toggle on mobile
        if (window.innerWidth <= 768) {
            menuToggle.style.display = 'block';
            navMenu.style.display = 'none';
        }
    }
}

createMobileMenu();

// Window resize handler
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        const menuToggle = document.querySelector('.mobile-menu-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (menuToggle && navMenu) {
            if (window.innerWidth > 768) {
                menuToggle.style.display = 'none';
                navMenu.style.display = 'flex';
            } else {
                menuToggle.style.display = 'block';
                navMenu.style.display = 'none';
            }
        }
    }, 250);
});

console.log('SecurePay application loaded successfully');
