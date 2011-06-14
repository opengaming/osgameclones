$(function() {
    $(".toggler").click(function() {
        var screenshots = $("script", this.parentNode);
        if(screenshots.length) {
            $('<div class="screenshots" style="display: none">')
                .html(screenshots.text()).appendTo(this.parentNode);
            screenshots.remove()
        }
        var hidden = $(".screenshots", this.parentNode).toggle().is(':hidden');
        this.innerHTML = hidden ? "&#x25b6;" : "&#x25bc;";
    });
});
