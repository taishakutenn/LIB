$(document).ready(function () {
    // Обработчик клика по кнопке со стрелкой
    $('.arrow-userinfo-button').on('click', function (event) {
        event.stopPropagation(); // Предотвращаем всплытие события

        // Переключаем видимость выпадающего списка
        $('.user-dropdown-menu').toggle();
    });

    // Закрываем выпадающий список при клике вне его области
    $(document).on('click', function (event) {
        if (!$(event.target).closest('.header-user-container').length) {
            $('.user-dropdown-menu').hide();
        }
    });
});