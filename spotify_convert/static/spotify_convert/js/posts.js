function updateMenu() {
    var type_menu = document.getElementById("platform-select").value;
    var tag = document.getElementById("tag-select").value;
    var metric = document.getElementById("metric-select-" + type_menu).value;
    var days_ago = document.getElementById("days-select").value;
    var page_id = document.getElementById(type_menu + "-select").value;

    Array.from(document.getElementsByClassName("type-menu")).forEach( function (item) {
        item.style.display = "none";
    });

    document.getElementById(type_menu + "-group").style.display = "block";

    Array.from(document.getElementsByClassName("metric-menu")).forEach( function (item) {
        item.style.display = "none";
    });
    document.getElementById("metric-select-" + type_menu + "-group").style.display = "block";

    var new_path = base_posts_url + type_menu + "/?page_id=" + page_id;

    if (tag != 'all') {
        new_path += "&tag=" + tag;
    }

    new_path += '&metric=' + metric + "&days_ago=" + days_ago;
    document.getElementById("update-button").href = new_path;
}