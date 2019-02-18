let ROUTER = {
    PAGE_NAMES: {
        LIST: 'list',
        READ: 'read',
        EDIT: 'edit',
        NEW: 'new',
    },
};

ROUTER.PAGES = [
    { name: ROUTER.PAGE_NAMES.LIST, path_regex: /^\/$/gmi },
    { name: ROUTER.PAGE_NAMES.READ, path_regex: /^\/(\d+)$/gmi },
    { name: ROUTER.PAGE_NAMES.EDIT, path_regex: /^\/(\d+)\/edit$/gmi },
    { name: ROUTER.PAGE_NAMES.NEW, path_regex: /^\/new$/gmi },
],
ROUTER.CURRENT_PAGE = (function getCurrentPage() {
    const pathname = window.location.pathname;
    const matches = ROUTER.PAGES.filter(page => page.path_regex.test(pathname));
    return matches[0]
})();

const KEYCODES = { ENTER:13 };
const MACY_SETTINGS = {
    container: '[data-posts-container]',
    mobileFirst: true,
    columns: 1,
    margin: 50,
    trueOrder: true,
    breakAt: {
        700: 2,
        1024: 3,
    },
};
let posts_container_el = null;
let socket = io(`http://${window.location.hostname}:5002`);
let macyInstance = null;

function handlePostUpdate(res) {
    if ([ROUTER.PAGE_NAMES.EDIT, ROUTER.PAGE_NAMES.NEW].indexOf(ROUTER.CURRENT_PAGE['name']) >= 0) {
        console.log("Uh, hi... maybe figure out what to do here!?")
        return;
    }

    const post = JSON.parse(res);
    const currPostEl = document.querySelector(`[data-post-id="${post.id}"]`);

    if (ROUTER.CURRENT_PAGE['name'] === ROUTER.PAGE_NAMES.LIST) {
        const newPostHTML = post['postcard'];
        const doc = new DOMParser().parseFromString(newPostHTML, 'text/html');
        const newPostEl = doc.body.firstChild

        if (currPostEl) {
            currPostEl.removeEventListener('click', handleCardNavigate);
            currPostEl.removeEventListener('keydown', handleCardNavigate);
            currPostEl.parentElement.replaceChild(newPostEl, currPostEl);
        } else {
            posts_container_el = (posts_container_el === null) ? document.querySelector('[data-posts-container]') : posts_container_el;
            posts_container_el.prepend(newPostEl);
        }

        newPostEl.addEventListener('click', handleCardNavigate);
        newPostEl.addEventListener('keydown', handleCardNavigate);

        macyInstance.recalculate(true);

        return;
    }

    if (ROUTER.CURRENT_PAGE['name'] === ROUTER.PAGE_NAMES.READ) {
        if (currPostEl === null) {
            return;
        }

        if (post['status'] === 0) {
            window.location.href = '/';
            return;
        }

        const newPostHTML = post['postfull'];
        const doc = new DOMParser().parseFromString(newPostHTML, 'text/html');
        const newPostEl = doc.body.firstChild
        currPostEl.parentElement.replaceChild(newPostEl, currPostEl)

        return;
    }
}

function handleMacyRecalculated() {
    const postsContainerEl = document.querySelector('[data-posts-container]');
    postsContainerEl.style.display = 'block';
}

function handleCardNavigate(e) {
    if (e.type === 'click' || e.keyCode === KEYCODES.ENTER) {
        const url = (e.currentTarget) ? e.currentTarget.getAttribute("href") : null;
        if (url) {
            window.open(url,'_self');
        }
    }
}

function bindPostcardClick() {
    let posts = document.querySelectorAll('[data-postcard]');
    for (let i = 0; i < posts.length; i+=1) {
        postEl = posts[i];
        postEl.addEventListener('click', handleCardNavigate);
        postEl.addEventListener('keydown', handleCardNavigate);
    }
}

document.addEventListener("DOMContentLoaded", function(event) {
    if (ROUTER.CURRENT_PAGE['name'] === ROUTER.PAGE_NAMES.LIST) {
        macyInstance = Macy(MACY_SETTINGS);
        macyInstance.on(macyInstance.constants.EVENT_RECALCULATED, handleMacyRecalculated);
    }
    socket.on('post_update', handlePostUpdate);
    bindPostcardClick()
});
