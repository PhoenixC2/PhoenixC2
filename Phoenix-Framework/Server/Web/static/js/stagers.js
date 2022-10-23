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
    let listener = listeners[listener_id - 1];
    // get form
    let form = document.getElementById(listener.type + "-form");
    // change content of modal
    document.getElementById("create-form-content").innerHTML = form.innerHTML;
}
function createEdit(id) {
    if (id == edit_stager_id) {
        // open modal
        $("#edit-modal").modal("show");
        return;
    }
    let stager = stagers[id];

    // get form by type
    const form = document.getElementById(stager.listener.type + "-form");

    // set modal body
    // replace all edit with create
    document.getElementById("edit-form").innerHTML = form.innerHTML.replace(/create/g, "edit");

    // set values
    document.getElementById("id-edit").value = stager.id;
    document.getElementById("name-edit").value = stager.name;
    document.getElementById(stager.payload_type + "-payload_type-edit").selected = true;
    document.getElementById("encoding-edit").value = stager.encoding;
    document.getElementById("random_size-edit").checked = stager.random_size;
    document.getElementById("timeout-edit").value = stager.timeout;
    document.getElementById("delay-edit").value = stager.delay;
    document.getElementById("different-address-edit").value = stager.different_address;
    // set options
    for (let option_name in stager.options) {
        if (Object.prototype.hasOwnProperty.call(stager.options, option_name)) {
            let option = stager.options[option_name];
            console.log(option_name.toLowerCase() + "-edit");
            let element = document.getElementById(option_name.toLowerCase() + "-edit");
            if (element.type === "checkbox") {
                element.checked = option;
            }
            element.value = option;
        }
    }
    edit_stager_id = id;
    // open modal
    $("#edit-modal").modal("show");

}

function copyToClipboard(id, one_liner) {
    let url = "/stagers/" + id + "/download?json=true";
    if (one_liner) {
        url += "&one_liner=true";
    }
    fetch(url, {
        method: "GET"
    }).then(response => response.json())
        .then(data => {
            // check if success
            if (data.status === "success") {
                console.log("penis")
                // show notification
                showNotification("Copied to clipboard.", data.status);
                // copy to clipboard
                navigator.clipboard.writeText(data.stager);
            }
            else {
                showNotification(data.message, data.success)
            }
        });
}

