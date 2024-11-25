document.addEventListener('DOMContentLoaded', () => {
    // Dropdown menu toggle
    const dropdownButton = document.querySelector('.welcome-message');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownButton && dropdownMenu) {
        dropdownButton.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
        });

        window.addEventListener('click', () => {
            dropdownMenu.style.display = 'none';
        });
    }

   
    // Search bar filtering
    const searchBar = document.querySelector('.search-bar');
    if (searchBar) {
        searchBar.addEventListener('input', () => {
            const query = searchBar.value.toLowerCase();
            const rows = document.querySelectorAll('.inventory-table tbody tr');

            rows.forEach(row => {
                const cells = Array.from(row.children);
                const matches = cells.some(cell => cell.textContent.toLowerCase().includes(query));
                row.style.display = matches ? '' : 'none';
            });
        });
    }

    // Delete confirmation
    const deleteLinks = document.querySelectorAll('.action-link[href*="delete_shoe"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to delete this shoe?')) {
                e.preventDefault();
            }
        });
    });
});
