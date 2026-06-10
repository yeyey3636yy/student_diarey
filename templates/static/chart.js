// ==================== КЛАСС ДЛЯ ГРАФИКОВ ====================

class ChartManager {
    constructor() {
        this.charts = {};
    }

    /**
     * Создать круговую диаграмму
     */
    createPieChart(canvasId, data, labels, title = '') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#28a745',
                        '#17a2b8',
                        '#ffc107',
                        '#fd7e14',
                        '#dc3545',
                        '#667eea'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: !!title,
                        text: title
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * Создать столбчатую диаграмму
     */
    createBarChart(canvasId, data, labels, label = 'Значение', title = '') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: 'rgba(102, 126, 234, 0.7)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    borderRadius: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#e0e0e0'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    title: {
                        display: !!title,
                        text: title
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * Создать линейную диаграмму (тренды)
     */
    createLineChart(canvasId, data, labels, label = 'Тренд', title = '') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: 'white',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 5,
                        grid: {
                            color: '#e0e0e0'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: !!title,
                        text: title
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * Создать гистограмму распределения оценок
     */
    createGradeDistributionChart(canvasId, distribution) {
        const grades = [5, 4, 3, 2, 1];
        const counts = grades.map(g => distribution[g] || 0);
        
        return this.createBarChart(canvasId, counts, grades, 'Количество оценок', 'Распределение оценок');
    }

    /**
     * Уничтожить все графики
     */
    destroyAll() {
        for (let key in this.charts) {
            if (this.charts[key]) {
                this.charts[key].destroy();
            }
        }
        this.charts = {};
    }
}

// ==================== УТИЛИТЫ ====================

function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('ru-RU');
}

function showNotification(message, type = 'success') {
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };

    const notification = document.createElement('div');
    notification.className = 'flash-message';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        z-index: 9999;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        cursor: pointer;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
    
    notification.onclick = () => notification.remove();
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ==================== ИНИЦИАЛИЗАЦИЯ ====================

document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое закрытие flash-сообщений
    setTimeout(() => {
        document.querySelectorAll('.flash-message').forEach(msg => {
            msg.style.animation = 'slideIn 0.3s reverse';
            setTimeout(() => msg.remove(), 300);
        });
    }, 3000);
});

// Экспорт (если используется в модулях)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChartManager, formatDate, showNotification, confirmAction };
}