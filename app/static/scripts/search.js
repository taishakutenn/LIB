$(document).ready(function () {
    // Перехватываем нажатие на кнопку "Найти"
    $('#search-button').on('click', function (event) {
        event.preventDefault(); // Предотвращаем стандартное поведение кнопки

        // Получаем значение из поля ввода
        var searchWord = $('#ajax-search').val().trim();

        // Если поле пустое, не перенаправляем
        if (!searchWord) {
            alert('Введите текст для поиска'); // Можно заменить на уведомление
            return;
        }

        // Формируем URL с параметром search_word
        var url = `/search?search_word=${encodeURIComponent(searchWord)}`;

        // Перенаправляем пользователя на страницу поиска
        window.location.href = url;
    });
});