let salesChart, lowStockChart;

// Initialize Sales Chart (Bar chart)
function initializeSalesChart(days, salesValues) {
    const ctxSales = document.getElementById('salesChart').getContext('2d');
    salesChart = new Chart(ctxSales, {
        type: 'bar',  // Bar chart for sales data
        data: {
            labels: days,
            datasets: [{
                label: 'Total Sales (₱)',
                data: salesValues,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return '₱' + value;
                        }
                    }
                }
            }
        }
    });
}

// Initialize Low Stock Chart (Bar chart)
function initializeLowStockChart(labels, data) {
    const ctxLowStock = document.getElementById('lowStockChart').getContext('2d');
    lowStockChart = new Chart(ctxLowStock, {
        type: 'bar',  // Bar chart for stock levels
        data: {
            labels: labels,
            datasets: [{
                label: 'Stock Level',
                data: data,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Update Charts with AJAX
function updateDashboardData() {
    $.ajax({
        url: '{% url "dashboard_api" %}',  // Replace with your API URL
        method: 'GET',
        success: function (data) {
            // Update stats
            $('#total-sales-today').text(`₱${data.total_sales_today}`);
            $('#top-selling-shoe').text(data.top_selling_shoe.name || 'N/A');
            $('#top-selling-quantity').text(`${data.top_selling_shoe.total_sold || 0} sold`);

            let lowStockList = '';
            data.low_stock_shoes.forEach(function (shoe) {
                lowStockList += `<li>${shoe.name} (Stock: ${shoe.stock})</li>`;
            });
            $('#low-stock-list').html(`<ul>${lowStockList}</ul>`);

            // Update sales chart
            salesChart.data.labels = data.days;
            salesChart.data.datasets[0].data = data.sales_values;
            salesChart.update();

            // Update low stock chart
            lowStockChart.data.labels = data.low_stock_shoes_names;
            lowStockChart.data.datasets[0].data = data.low_stock_shoes_stocks;
            lowStockChart.update();
        },
        error: function () {
            console.error('Failed to fetch dashboard data.');
        }
    });
}

$(document).ready(function () {
    initializeSalesChart({{ days|safe }}, {{ sales_values|safe }});
    initializeLowStockChart({{ low_stock_shoes_names|safe }}, {{ low_stock_shoes_stocks|safe }});

    // Periodically update the charts (e.g., every 5 seconds)
    setInterval(updateDashboardData, 5000);
});
