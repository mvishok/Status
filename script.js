$(function () {
    $('[data-toggle="popover"]').popover();
});

var pricenet = new Date().getTime();

var pricenet = new Date().getTime();

$.get("https://api.vishok.me/pricenet", function (data) {
    const pricenetTaken = new Date().getTime() - pricenet;

    if (data.status == "succes") {
        if (pricenetTaken < 100) {
            $(".pricenet-active").show();
        } else {
            $(".pricenet-busy").show();
        }
    } else {
        $(".pricenet-inactive").show();
    }
}).fail(function () {
    $(".pricenet-inactive").show();
});

$("#lastcheck").text("Last checked: " + new Date().toLocaleString());