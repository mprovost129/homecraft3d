// Sidebar category tree for product_list.html
// Requires Bootstrap Icons for plus/minus or use Unicode

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.category-toggle').forEach(function(toggle) {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      var target = document.getElementById(this.dataset.target);
      if (target) {
        if (target.style.display === 'none') {
          target.style.display = '';
          this.innerHTML = '&#8722;'; // minus
        } else {
          target.style.display = 'none';
          this.innerHTML = '&#43;'; // plus
        }
      }
    });
  });
});
