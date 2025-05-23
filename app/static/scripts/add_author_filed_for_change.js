$(document).ready(function () {
    let authorIndex = $('#authors-container .author-field').length;

    // Загружаем заранее выбранных авторов (если есть)
    const rawAuthors = $('#selected-authors-data').val();
    if (rawAuthors) {
        const authors = rawAuthors.split('|');
        for (const fullName of authors) {
            addAuthorField(fullName);
        }
    }

    // Добавление нового поля по кнопке
    $('#add-author-btn').click(function () {
        addAuthorField();
    });

    function addAuthorField(fullName = "") {
        const newAuthorHtml = `
            <div class="author-field">
                <label for="authors-${authorIndex}-name" class="form-label">Введите ФИО автора (через пробел)</label>
                <input type="text" name="authors-${authorIndex}-name" id="authors-${authorIndex}-name" class="form-input" value="${fullName}">
            </div>
        `;
        $('#authors-container').append(newAuthorHtml);
        authorIndex++;
    }
});