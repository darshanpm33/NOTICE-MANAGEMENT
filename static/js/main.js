// Main JS for Notice Management System

// Handle logout
document.addEventListener('DOMContentLoaded', () => {
    console.log('Notice management system initialized.');
    
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    // Sidebar toggle for mobile
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    // Add a burger menu for mobile
    if (window.innerWidth <= 768) {
        const burger = document.createElement('div');
        burger.innerHTML = '<i class="fas fa-bars"></i>';
        burger.style.position = 'fixed';
        burger.style.top = '15px';
        burger.style.left = '15px';
        burger.style.zIndex = '2001';
        burger.style.fontSize = '1.5rem';
        burger.style.cursor = 'pointer';
        burger.style.color = '#fff';
        burger.onclick = () => {
            sidebar.classList.toggle('active');
        };
        document.body.appendChild(burger);
    }
});

// Real-time Search functionality for tables
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');

    input.addEventListener('keyup', () => {
        const filter = input.value.toLowerCase();
        for (let i = 1; i < rows.length; i++) {
            const rowText = rows[i].textContent.toLowerCase();
            rows[i].style.display = rowText.includes(filter) ? '' : 'none';
        }
    });
}
