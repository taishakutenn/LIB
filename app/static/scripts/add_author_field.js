$(document).ready(function () {
    let authorIndex = $('#authors-container .author-field').length;

    $('#add-author-btn').click(function () {
        const newAuthorHtml = `
            <div class="author-field">
                <label for="authors-${authorIndex}-name" class="form-label">Введите ФИО автора (через пробел)</label>
                <input type="text" name="authors-${authorIndex}-name" id="authors-${authorIndex}-name" class="form-input">
            </div>
        `;

        $('#authors-container').append(newAuthorHtml);
        authorIndex++;
    });
});