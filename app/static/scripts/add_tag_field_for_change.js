$(document).ready(function () {
    const selectedTags = new Set();
        // Предзаполнение ранее выбранных тегов
    const preselected = $("#selected-tags-input").val();
    if (preselected) {
        preselected.split(",").forEach(tag => {
            selectedTags.add(tag);

            // Отметим выбранный тег визуально
            $(`.tag-option[data-tag="${tag}"]`).addClass("selected");
        });

        // Обновим визуальный вывод
        const display = [...selectedTags].map(t => `<span>${t}</span>`).join(" ");
        $("#selected-tags").html(display);
    }
    $(".tag-option").on("click", function () {
        const tag = $(this).data("tag");

        if ($(this).hasClass("selected")) {
            $(this).removeClass("selected");
            selectedTags.delete(tag);
        } else {
            $(this).addClass("selected");
            selectedTags.add(tag);
        }

        // Обновляем скрытое поле
        $("#selected-tags-input").val([...selectedTags].join(","));

        // Обновляем визуально выбранные теги
        const display = [...selectedTags].map(t => `<span>${t}</span>`).join(" ");
        $("#selected-tags").html(display);
    });
});