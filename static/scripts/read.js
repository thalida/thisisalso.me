document.addEventListener("DOMContentLoaded", function(event) {
    let container = document.querySelector('.ql-container');
    container.addEventListener('dblclick', handleDoubleClick);

    function handleDoubleClick(e) {
        window.open(`${window.location.href}/edit`, '_self');
    }
});
