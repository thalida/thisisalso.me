var icons = Quill.import('ui/icons');
var Delta = Quill.import('delta');
var BlockEmbed = Quill.import('blots/block/embed');
var forceSave = false;
var isSaving = false;

// Store accumulated changes
var change = new Delta();
var selectedTheme = null;

class DividerBlot extends BlockEmbed { }
DividerBlot.blotName = 'divider';
DividerBlot.tagName = 'hr';
Quill.register(DividerBlot);

icons.header[3] = `
<svg width="17px" height="12px" viewBox="0 0 17 12" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
        <g id="h3" fill="currentColor">
            <path d="M1.992,12.728 C1.81066576,12.9093342 1.58966797,13 1.329,13 C1.06833203,13 0.84733424,12.9093342 0.666,12.728 C0.48466576,12.5466658 0.394,12.325668 0.394,12.065 L0.394,1.525 C0.394,1.26433203 0.48466576,1.04333424 0.666,0.862 C0.84733424,0.68066576 1.06833203,0.59 1.329,0.59 C1.58966797,0.59 1.81066576,0.68066576 1.992,0.862 C2.17333424,1.04333424 2.264,1.26433203 2.264,1.525 L2.264,5.503 C2.264,5.60500051 2.31499949,5.656 2.417,5.656 L7.381,5.656 C7.48300051,5.656 7.534,5.60500051 7.534,5.503 L7.534,1.525 C7.534,1.26433203 7.62466576,1.04333424 7.806,0.862 C7.98733424,0.68066576 8.20833203,0.59 8.469,0.59 C8.72966797,0.59 8.95066576,0.68066576 9.132,0.862 C9.31333424,1.04333424 9.404,1.26433203 9.404,1.525 L9.404,12.065 C9.404,12.325668 9.31333424,12.5466658 9.132,12.728 C8.95066576,12.9093342 8.72966797,13 8.469,13 C8.20833203,13 7.98733424,12.9093342 7.806,12.728 C7.62466576,12.5466658 7.534,12.325668 7.534,12.065 L7.534,7.271 C7.534,7.16899949 7.48300051,7.118 7.381,7.118 L2.417,7.118 C2.31499949,7.118 2.264,7.16899949 2.264,7.271 L2.264,12.065 C2.264,12.325668 2.17333424,12.5466658 1.992,12.728 Z M11.32,7.07 C11.1666659,7.07 11.0333339,7.0133339 10.92,6.9 C10.8066661,6.7866661 10.75,6.6533341 10.75,6.5 L10.75,6.27 C10.75,6.1166659 10.8066661,5.9833339 10.92,5.87 C11.0333339,5.7566661 11.1666659,5.7 11.32,5.7 L15.05,5.7 C15.2033341,5.7 15.3366661,5.7566661 15.45,5.87 C15.5633339,5.9833339 15.62,6.1166659 15.62,6.27 L15.62,6.5 C15.62,6.8800019 15.4733348,7.1899988 15.18,7.43 L13.67,8.68 L13.67,8.69 C13.67,8.6966667 13.6733333,8.7 13.68,8.7 L13.8,8.7 C14.3800029,8.7 14.8449983,8.8799982 15.195,9.24 C15.5450018,9.6000018 15.72,10.0866636 15.72,10.7 C15.72,11.4733372 15.4833357,12.0666646 15.01,12.48 C14.5366643,12.8933354 13.8566711,13.1 12.97,13.1 C12.436664,13.1 11.8966694,13.0366673 11.35,12.91 C11.1899992,12.8699998 11.0583339,12.7816674 10.955,12.645 C10.8516662,12.5083327 10.8,12.3533342 10.8,12.18 L10.8,11.84 C10.8,11.706666 10.8549995,11.6016671 10.965,11.525 C11.0750006,11.448333 11.196666,11.4299998 11.33,11.47 C11.9033362,11.6566676 12.4033312,11.75 12.83,11.75 C13.2166686,11.75 13.5166656,11.6600009 13.73,11.48 C13.9433344,11.2999991 14.05,11.0500016 14.05,10.73 C14.05,10.4033317 13.9266679,10.173334 13.68,10.04 C13.4333321,9.906666 12.9733367,9.8366667 12.3,9.83 C12.1466659,9.83 12.0133339,9.77500055 11.9,9.665 C11.7866661,9.55499945 11.73,9.4233341 11.73,9.27 L11.73,9.25 C11.73,8.8766648 11.8733319,8.5666679 12.16,8.32 L13.58,7.09 L13.58,7.08 C13.58,7.0733333 13.5766667,7.07 13.57,7.07 L11.32,7.07 Z" id="Shape" fill-rule="nonzero"></path>
        </g>
    </g>
</svg>`;

icons.divider = `
<svg width="16px" height="16px" viewBox="0 0 17 12" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
        <g id="h3" fill="currentColor">
            <rect x="0" y="6" width="100" height="2" />
        </g>
    </g>
</svg>`;

var toolbarOptions = [
  [{ 'header': 1 }, { 'header': 2 }, { 'header': 3 }],
  ['bold', 'italic', 'underline', 'strike', 'code'],
  ['blockquote', 'code-block', 'divider'],
  ['link', 'image', 'video'],
  [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }],
  [{ 'indent': '-1'}, { 'indent': '+1' }],
  [{ 'align': 'center' }, {'align': 'right'}],
  ['clean'],
  [{'post-theme': null}, {'post-theme': 1}, {'post-theme': 2}, {'post-theme': 3}, {'post-theme': 4}, {'post-theme': 5}],
];

var quill = new Quill('[data-quill-container]', {
  modules: {
    clipboard: true,
    toolbar: {
        container: toolbarOptions,
        handlers: {
            'post-theme': function(themeId) {
                selectedTheme = themeId
                $('[data-quill-container]').attr('data-theme', selectedTheme);
                forceSave = true;
            },
            'divider': function() {
                let range = this.quill.getSelection(true);
                this.quill.insertText(range.index, '\n', Quill.sources.USER);
                this.quill.insertEmbed(range.index + 1, 'divider', true, Quill.sources.USER);
                this.quill.setSelection(range.index + 2, Quill.sources.SILENT);
            },
        },
    },
  },
  scrollingContainer: '[data-quill-container]',
  placeholder: 'Type here...',
  theme: 'snow'
});

$('.ql-post-theme').each(function(i, el) {
    var $el = $(el);
    $el.attr('data-theme', $el.val());
});

function getHTML(delta) {
    var tempQuill = new Quill(document.createElement("div"));
    tempQuill.setContents(delta);
    return tempQuill.root.innerHTML;
}

quill.on('text-change', function(delta) {
  change = change.compose(delta);
});

// Save periodically
setInterval(function() {
    if (!isSaving && (change.length() > 0 || forceSave)) {
        isSaving = true;

        $.ajax({
            method: "POST",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            url: "/api/post/upsert",
            data: JSON.stringify({
                id: post.id,
                theme: selectedTheme,
                contents: getHTML(quill.getContents()),
            }),
        })
        .done(function( res ) {
            post = res;
            isSaving = false;
            forceSave = false;
        });

        change = new Delta();
    }
}, 3*1000);

// Check for unsaved data
window.onbeforeunload = function() {
  if (change.length() > 0) {
    return 'There are unsaved changes. Are you sure you want to leave?';
  }
}