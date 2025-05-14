$(document).ready(function () {
    // Функция для показа уведомления
    function showNotification(message) {
        const notification = $("#notification");
        const notificationText = $("#notification-text");

        // Устанавливаем текст уведомления
        notificationText.text(message);

        // Показываем уведомление
        notification.fadeIn();

        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            notification.fadeOut();
        }, 5000);
    }

    const errorMessage = "{{ error_message }}"; // Передаём сообщение из Jinja2
    if (errorMessage) {
        showNotification(errorMessage);
    }
});