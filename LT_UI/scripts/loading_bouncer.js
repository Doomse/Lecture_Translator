(function (win, doc) {
    'use strict';
    if (!doc.getElementById || !win.addEventListener) {
        // doesn't cut the mustard.
        return;
    }
    var form = doc.getElementById('post-form'),
        checkForm = function (ev) {
            this.appendChild(doc.createElement('progress'));
            doc.getElementById('submit-button').setAttribute('disabled', "true")
        };
    form.addEventListener('submit', checkForm, false);
    
}(this, this.document));