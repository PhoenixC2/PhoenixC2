let original_modal_content = document.getElementById("create-modal-body").innerHTML;
let edit_stager_id = null;

function deleteStager(id) {
    fetch("/stagers/" + id + "/remove?json=true", {
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

function resetModal() {
    // reset modal content
    document.getElementById("create-modal-body").innerHTML = original_modal_content;
    changeListener();
}
function changeListener() {
    // get value of select
    let listener_id = document.getElementById("listener").value;
    // get form using listener id
    let listener = listeners[listener_id -1 ];
    // get form
    let form = document.getElementById(listener.type + "-form");
    // change content of modal
    document.getElementById("create-form-content").innerHTML = form.innerHTML;
}