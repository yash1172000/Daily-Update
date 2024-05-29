$(document).ready(function () {
    // $('.navbar-toggler').click(function () {
    //     $('.collapse.navbar-collapse').toggle();
    // });
    $(".navbar-toggler-icon").click(function () {
        $(".hide-popup").addClass("open");
    });
    $(".btn-close-ct").click(function () {
        $(".hide-popup").removeClass("open");
    })
});