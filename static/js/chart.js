
document.addEventListener('DOMContentLoaded', function() {
	console.log('Chart.js loaded and DOM ready');
	// Sales Chart (dummy data)
	const salesCtx = document.getElementById('salesChart').getContext('2d');
	new Chart(salesCtx, {
		type: 'line',
		data: {
			labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
			datasets: [{
				label: 'Sales ($)',
				data: [1200, 1500, 1800, 1700, 2100, 2500],
				borderColor: 'rgba(54, 162, 235, 1)',
				backgroundColor: 'rgba(54, 162, 235, 0.2)',
				fill: true,
				tension: 0.3
			}]
		},
		options: {
			responsive: true,
			plugins: { legend: { display: true } }
		}
	});

	// User Growth Chart (dummy data)
	const userCtx = document.getElementById('userChart').getContext('2d');
	new Chart(userCtx, {
		type: 'bar',
		data: {
			labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
			datasets: [{
				label: 'New Users',
				data: [10, 15, 20, 18, 25, 30],
				backgroundColor: 'rgba(255, 99, 132, 0.6)',
				borderColor: 'rgba(255, 99, 132, 1)',
				borderWidth: 1
			}]
		},
		options: {
			responsive: true,
			plugins: { legend: { display: true } }
		}
	});
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('Chart.js loaded and DOM ready');
    // Sales Chart (dynamic data)
    const salesCtx = document.getElementById('salesChart').getContext('2d');
    new Chart(salesCtx, {
        type: 'line',
        data: {
            labels: typeof salesLabels !== 'undefined' ? salesLabels : [],
            datasets: [{
                label: 'Sales ($)',
                data: typeof salesData !== 'undefined' ? salesData : [],
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: true } }
        }
    });

    // User Growth Chart (dynamic data)
    const userCtx = document.getElementById('userChart').getContext('2d');
    new Chart(userCtx, {
        type: 'bar',
        data: {
            labels: typeof userLabels !== 'undefined' ? userLabels : [],
            datasets: [{
                label: 'New Users',
                data: typeof userData !== 'undefined' ? userData : [],
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: true } }
        }
    });
});
