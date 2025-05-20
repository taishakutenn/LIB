$(document).ready(function () {
    const selectedTags = new Set();

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