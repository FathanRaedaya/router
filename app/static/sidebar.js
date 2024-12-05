// Get reference to the sidebar toggle button and the sidebar itself
const btn = document.querySelector('#sidebar-btn');
const sidebar = document.querySelector('.sidebar');

// Toggle the 'active' class of the sidebar when the button is clicked
btn.onclick = function() {
    sidebar.classList.toggle('active');
}
