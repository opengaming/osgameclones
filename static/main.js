$(function() {
    $(".toggler").click(function() {
        var hidden = $(".screenshots", this.parentNode).toggle().is(':hidden');
        this.innerHTML = hidden ? "&#x25b6;" : "&#x25bc;";
    });
});
