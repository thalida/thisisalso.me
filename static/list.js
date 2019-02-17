document.addEventListener("DOMContentLoaded", function(event) {
    const KEYCODES = { ENTER:13 };
    let posts = document.querySelectorAll('.post');

    for (var i = 0; i < posts.length; i+=1) {
        post = posts[i];
        post.addEventListener('click', navigateLink);
        post.addEventListener('keydown', navigateLink);
    }

    function navigateLink(e) {
        if (e.type === 'click' || e.keyCode === KEYCODES.ENTER) {
            const url = (e.currentTarget) ? e.currentTarget.getAttribute("href") : null;
            if (url) {
                window.open(url,'_self');
            }
        }
    }
});
