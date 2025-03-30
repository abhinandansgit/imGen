// Toggle Side Menu
function toggleMenu() {
    const sideMenu = document.getElementById('sideMenu');
    sideMenu.classList.toggle('visible');
}

// Debug: Confirm script is loaded
console.log("script.js loaded");

// Custom Cursor and Trailing Dot
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded, initializing custom cursor");

    // Create the main cursor element
    const cursor = document.createElement('div');
    cursor.classList.add('custom-cursor');
    document.body.appendChild(cursor);

    // Create the trailing dot element
    const trail = document.createElement('div');
    trail.classList.add('custom-cursor', 'trail');
    document.body.appendChild(trail);

    // Update cursor position on mouse move
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';

        // Trailing dot follows with a slight delay
        setTimeout(() => {
            trail.style.left = e.clientX + 'px';
            trail.style.top = e.clientY + 'px';
        }, 50);
    });

    // Hide cursor and trail when mouse leaves the window
    document.addEventListener('mouseleave', () => {
        cursor.style.display = 'none';
        trail.style.display = 'none';
    });

    // Show cursor and trail when mouse enters the window
    document.addEventListener('mouseenter', () => {
        cursor.style.display = 'block';
        trail.style.display = 'block';
    });
});

// Show Toast Notification
function showToast(message, category = 'info') {
    const toast = document.getElementById('toast');
    
    // Update the message and apply the category class
    toast.textContent = message;
    toast.className = 'toast show ' + category;

    // Hide the toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        toast.className = 'toast';
    }, 3000);
}

// Real-time Prompt Validation
document.querySelector('#promptInput').addEventListener('input', function() {
    const prompt = this.value.trim();
    const feedback = document.querySelector('#promptFeedback');
    const generateBtn = document.querySelector('.generate-btn');
    if (prompt.length < 5) {
        feedback.style.display = 'block';
        generateBtn.disabled = true;
    } else {
        feedback.style.display = 'none';
        generateBtn.disabled = false;
    }
});

// Form Submission with Validation
document.querySelector('#promptForm').addEventListener('submit', function(e) {
    const prompt = document.querySelector('#promptInput').value.trim();
    if (prompt.length < 5) {
        e.preventDefault(); // Prevent form submission
        showToast('⚠️ Please enter at least 5 characters!', 'danger');
    } else {
        document.getElementById('loader').style.display = 'flex';
    }
});

// Delete Image with Confirmation
function deleteImage(imageName) {
    if (confirm('Are you sure you want to delete this image?')) {
        fetch('/delete/' + imageName, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('✅ Image deleted!', 'success');
                    location.reload();
                } else {
                    showToast('❌ Failed to delete image.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error deleting image:', error);
                showToast('❌ Error deleting image.', 'danger');
            });
    }
}

// Image Preview Modal
function showImagePreview(imageUrl) {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.8)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1002';

    const img = document.createElement('img');
    img.src = imageUrl;
    img.style.maxWidth = '90%';
    img.style.maxHeight = '90%';

    modal.appendChild(img);
    modal.addEventListener('click', () => document.body.removeChild(modal));
    document.body.appendChild(modal);
}