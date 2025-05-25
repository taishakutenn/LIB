$(document).ready(function () {
    // Привязка события keyup
    $('#ajax-search').on('keyup', function () {
        // Получаем текущее значение инпута
        var inputVal = $(this).val().trim();

        // Очищаем подсказки, если поле пустое
        if (inputVal === "") {
            $('#suggestions-box').empty();
            return;
        }

        $.ajax({
            url: '/ajax_search',
            type: 'GET',
            data: {
                search_request: inputVal,
            },
            success: function (response) {
                // Очищаем предыдущие подсказки
                $('#suggestions-box').empty();

                // Проверяем, есть ли результаты
                if (!response || (response.books.length === 0 && response.authors.length === 0 && response.tags.length === 0)) {
                    $('#suggestions-box').append('<div class="suggestion-item no-results">Ничего не найдено</div>');
                    return;
                }

                // Отображаем книги
                if (response.books.length > 0) {
                    response.books.forEach(function (book) {
                        $('#suggestions-box').append(`
                            <div class="suggestion-item" data-type="book" data-id="${book.id}">
                                ${book.title}
                            </div>
                        `);
                    });
                }

                // Отображаем авторов
                if (response.authors.length > 0) {
                    response.authors.forEach(function (author) {
                        $('#suggestions-box').append(`
                            <div class="suggestion-item" data-type="author" data-id="${author.id}">
                                ${author.full_name}
                            </div>
                        `);
                    });
                }

                // Отображаем теги
                if (response.tags.length > 0) {
                    response.tags.forEach(function (tag) {
                        $('#suggestions-box').append(`
                            <div class="suggestion-item" data-type="tag" data-id="${tag.id}">
                                ${tag.name}
                            </div>
                        `);
                    });
                }
            },
            error: function (error) {
                console.error('Ошибка:', error);
                $('#suggestions-box').empty();
                $('#suggestions-box').append('<div class="suggestion-item error">Произошла ошибка при загрузке подсказок</div>');
            }
        });
    });

    // Скрываем подсказки при клике вне поля ввода
    $(document).on('click', function (event) {
        if (!$(event.target).closest('#ajax-search').length) {
            $('#suggestions-box').empty();
        }
    });

    // Обработка выбора подсказки
    $('#suggestions-box').on('click', '.suggestion-item', function () {
        var selectedValue = $(this).text().trim(); // Убираем лишние пробелы
        var type = $(this).data('type');          // Тип элемента (book, author, tag)
        var id = $(this).data('id');              // ID элемента

        // Устанавливаем текст в поле ввода
        $('#ajax-search').val(selectedValue);

        // Очищаем подсказки
        $('#suggestions-box').empty();

        console.log(`Выбран элемент: тип=${type}, id=${id}`);
    });
});