function showNotification(message, status) {

    $.notify({
        icon: "add_alert",
        message: message

    }, {
        type: status,
        timer: 3000,
        placement: {
            from: "top",
            align: "right"
        }
    });
}

function showCreateModal() {
    document.getElementById("create-modal-body").innerHTML = original_modal_content;
    $('#create-modal').modal('show');
}



function sendCreate() {
    // disable button
    document.getElementById("create-button").disabled = true;
    // get form
    let form = document.getElementById("create-form");
    // get data
    let data = new FormData(form);
    // send data
    fetch(form.action + "?json=true", {
        method: form.method,
        body: data
    }).then(response => response.json())
        .then(data => {
            // show notification
            showNotification(data.message, data.status);
            // check if success
            if (data.status === "success") {
                // sleep 1 second
                setTimeout(function () {
                    // reload page
                    location.reload();
                }, 1000);
            }
        });
    // activate button
    document.getElementById("create-button").disabled = false;



}

function sendEdit() {
    // disable button
    document.getElementById("edit-button").disabled = true;
    // get form
    let form = document.getElementById("edit-form");
    // get data
    let data = new FormData(form);
    // send data
    fetch(form.action + "?json=true", {
        method: form.method,
        body: data
    }).then(response => response.json())
        .then(data => {
            // show notification
            showNotification(data.message, data.status);
            // check if success
            if (data.status === "success") {
                // sleep 1 second
                setTimeout(function () {
                    // reload page
                    location.reload();
                }, 1000);
            }
        });
    // activate button
    document.getElementById("edit-button").disabled = false;
}

function readNotifications() {
    // send data
    fetch("/logs/read?json=true", {
        method: "GET"
    }).then(response => response.json())
        .then(data => {
            // show notification
            showNotification("Read all messages.", data.status);
            // check if success
            if (data.status === "success") {
                // sleep 1 second
                setTimeout(function () {
                    // reload page
                    location.reload();
                }, 1000);
            }
        }
    );
}

function previewImage() {
    // get the file input
    let file_input = document.getElementById('picture');

    // get the preview image
    let preview = document.getElementById('picture-preview');

    // get the file
    let file = file_input.files[0];

    // create a FileReader
    let reader = new FileReader();

    // add an event listener to deal with the file when the reader is complete

    reader.addEventListener("load", function () {
        // set the src of the preview image to the data url of the file
        preview.src = reader.result;
    }, false);

    // if there is a file, read it
    if (file) {
        reader.readAsDataURL(file);
    }

    // if there is no file, set the preview image src to nothing
    else {
        preview.src = "";
    }

}