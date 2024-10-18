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

$(document).ready(function () {
    let formCount = $('#id_tickets-TOTAL_FORMS').val(); // Adjusted form count based on management form
    const emptyFormHtml = $('#empty-form').html(); // Get the HTML of the empty form template

    // Function to calculate the total number of tickets from all categories
    function calculateTotalCategoryTickets() {
        let totalTickets = 0;

        // Loop through each category's ticket input field
        $('.ticket-form input[id$="category_tickets_available"]').each(function () {
            let categoryTickets = parseInt($(this).val()) || 0;
            totalTickets += categoryTickets;
        });

        return totalTickets;
    }
    

    // Function to update the total event tickets field
    function updateEventTickets() {
        let totalCategoryTickets = calculateTotalCategoryTickets();
        let eventTicketsField = $('#id_tickets_available'); // Select event tickets available field

        // If total category tickets exceed event tickets, update event tickets
        if (totalCategoryTickets > parseInt(eventTicketsField.val())) {
            eventTicketsField.val(totalCategoryTickets);
        }
    }

    // Attach the event listener for any changes in the category tickets input
    $(document).on('input', 'input[id$="category_tickets_available"]', function () {
        updateEventTickets();
    });

    // Dynamic form addition
    $('#add-more').click(function () {
        const newFormHtml = emptyFormHtml.replace(/__prefix__/g, formCount);
        $('#ticket-categories').append('<div class="ticket-form">' + newFormHtml + '</div>');
        formCount++;
        $('#id_tickets-TOTAL_FORMS').val(formCount); // Update the total form count in the management form

        // Recalculate totals when a new form is added
        updateEventTickets();
    });

    // Remove form functionality
    $(document).on('click', '.remove-form', function () {
        $(this).closest('.ticket-form').remove();
        formCount--;
        $('#id_tickets-TOTAL_FORMS').val(formCount); // Update the total form count in the management form

        // Recalculate totals after a form is removed
        updateEventTickets();
    });

    // Initial calculation when the page loads
    updateEventTickets();
});