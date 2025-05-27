$(document).ready(function () {
        // Закрытие flash-сообщения при клике на кнопку
        $(".close-flash-message").on("click", function () {
            $(this).closest(".flash-message").fadeOut(300, function () {
                $(this).remove();
            });
        });

        // Автоматическое исчезновение через 5 секунд
        $(".flash-message").each(function () {
            setTimeout(() => {
                $(this).fadeOut(300, function () {
                    $(this).remove();
                });
            }, 5000);
        });
    });