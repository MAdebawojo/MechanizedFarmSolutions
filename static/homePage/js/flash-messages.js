$(document).ready(function () {
    // Close flash messages when clicking on them
    $('#flash-messages').on('click', '.flash li', function () {
        $(this).fadeOut('fast');
    });

    // Automatically hide flash messages after a certain time (e.g., 5 seconds)
    setTimeout(function () {
        $('.flash li').fadeOut('fast');
    }, 5000);
});