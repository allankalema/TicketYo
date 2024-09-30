// File: static/events/create.js

document.addEventListener('DOMContentLoaded', function() {
    // File input handling
    const fileInput = document.getElementById('file-upload');
    
    fileInput.addEventListener('change', function() {
        const fileName = fileInput.files[0] ? fileInput.files[0].name : '';
        
        if (fileName) {
            document.querySelector('.poster-upload span').innerText = fileName;
        }
    });

    // Category selection handling
    const categorySelect = document.getElementById('category');
    const customCategoryInput = document.getElementById('custom-category');

    categorySelect.addEventListener('change', function() {
        if (categorySelect.value === 'Other') {
            customCategoryInput.style.display = 'block'; // Show custom input
        } else {
            customCategoryInput.style.display = 'none'; // Hide custom input
        }
    });
});
