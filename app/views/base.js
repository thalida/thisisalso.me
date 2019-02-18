const KEYCODES = { ENTER:13 };
var socket = io('http://0.0.0.0:5002');

function handlePostUpdate(res) {
    const page = window.location.pathname
    const post = JSON.parse(res);

    if (page.indexOf('edit') >= 0 || page.indexOf('new') >= 0) {
        console.log("Uh, hi... maybe figure out what to do here!?")
        return;
    }

    const isIndexPage = page === '/';
    const postEl = document.querySelector(`[data-post-id="${post.id}"]`);

    if (!isIndexPage) {
        if (postEl === null) {
            return;
        } else if (post['status'] === 0) {
            window.location.href = '/';
            return;
        }
    }

    const newPostHTML = (isIndexPage) ? post['postcard'] : post['postfull']
    const doc = new DOMParser().parseFromString(newPostHTML, 'text/html');
    const newPostEl = doc.body.firstChild
    const parent = (postEl !== null) ? postEl.parentNode : document.querySelector('[data-posts-container]')

    parent.prepend(newPostEl)
    newPostEl.addEventListener('click', handleCardNavigate);
    newPostEl.addEventListener('keydown', handleCardNavigate);

    if (postEl !== null) {
        postEl.removeEventListener('click', handleCardNavigate);
        postEl.removeEventListener('keydown', handleCardNavigate);
        postEl.remove()
    }


}

function handleCardNavigate(e) {
    if (e.type === 'click' || e.keyCode === KEYCODES.ENTER) {
        const url = (e.currentTarget) ? e.currentTarget.getAttribute("href") : null;
        if (url) {
            window.open(url,'_self');
        }
    }
}

function bindClickEvent() {
    let posts = document.querySelectorAll('[data-postcard]');

    for (var i = 0; i < posts.length; i+=1) {
        postEl = posts[i];
        postEl.addEventListener('click', handleCardNavigate);
        postEl.addEventListener('keydown', handleCardNavigate);
    }
}

document.addEventListener("DOMContentLoaded", function(event) {
    socket.on('post_update', handlePostUpdate);
    bindClickEvent()
});
