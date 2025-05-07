$(function () {
                $('input[name="role"]').change(function () {
                    if ($(this).val() === 'admin') {
                        $('#admin-code-group').slideDown();
                    } else {
                        $('#admin-code-group').slideUp();
                    }
                });

                // Проверка начального состояния
                if ($('input[name="role"]:checked').val() === 'admin') {
                    $('#admin-code-group').show();
                }
            });