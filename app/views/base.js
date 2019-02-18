var socket = io('http://0.0.0.0:5002');
socket.on('post_update', function(res) {
    const page = window.location.pathname
    const post = JSON.parse(res);

    if (page.indexOf('edit') >= 0 || page.indexOf('new') >= 0) {
        console.log("Uh, hi... maybe figure out what to do here!?")
    } else {
        const postEl = document.querySelector(`[data-post-id="${post.id}"]`);
        const newPostHTML = (page === '/') ? post['postcard'] : post['postfull']
        const doc = new DOMParser().parseFromString(newPostHTML, 'text/html');
        const newPostEl = doc.body.firstChild
        postEl.parentNode.replaceChild(newPostEl, postEl);
    }
});
