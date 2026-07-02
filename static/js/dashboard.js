new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
        labels: ['1월', '2월', '3월', '4월', '5월'],
        datasets: [{
            label: '매출',
            data: [10, 18, 7, 9, 6],
            borderColor: '#c084fc',
            tension: 0.3
        }]
    }
});

new Chart(document.getElementById('doughnutChart'), {
    type: 'doughnut',
    data: {
        labels: ['게임', '아이템', '캐시', '기타'],
        datasets: [{
            data: [30, 40, 20, 10],
            backgroundColor: ['#e9d5ff', '#d9f99d', '#fef3c7', '#ddd6fe']
        }]
    }
});

new Chart(document.getElementById('barChart'), {
    type: 'bar',
    data: {
        labels: ['10대', '20대', '30대', '40대', '50대'],
        datasets: [{
            label: '회원 수',
            data: [120, 200, 80, 110, 60],
            backgroundColor: ['#ccfbf1', '#fbcfe8', '#bfdbfe', '#d9f99d', '#bbf7d0']
        }]
    },
    options: {
        indexAxis: 'y'
    }
});

new Chart(document.getElementById('pieChart'), {
    type: 'pie',
    data: {
        labels: ['PC', 'Mobile', 'Tablet'],
        datasets: [{
            data: [55, 35, 10],
            backgroundColor: ['#c7d2fe', '#bbf7d0', '#fef3c7']
        }]
    }
});