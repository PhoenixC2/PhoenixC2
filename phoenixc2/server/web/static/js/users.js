let edit_user_id = null;


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