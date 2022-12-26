let edit_user_id = null;
function previewImage() {
    // get the file input
    let file_input = document.getElementById('profile-picture');

    // get the preview image
    let preview = document.getElementById('profile-picture-preview');

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

function deleteUser(id) {
    fetch("/users/" + id + "/remove?json=true", {
        method: "DELETE"
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
}

function createEdit(id) {
    if (id == edit_user_id) {
        // open modal
        $("#edit-modal").modal("show");
        return;
    }
    let user = users[id];

    // get form
    let form = document.getElementById("edit-form");

    // set values
    form.elements["username"].value = user.username;

}