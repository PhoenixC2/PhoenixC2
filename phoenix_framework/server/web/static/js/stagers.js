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
function changePayload(type) {
    // get the payload value
    let payload = document.getElementById(`${type}-payload_type`).value;

    // get content of payload div
    let payload_div = document.getElementById("payload-div");

}
function changeListener() {
    let listener_id = document.getElementById("listener").value;
    let listener = listeners[listener_id - 1];
    let form = document.getElementById(listener.type + "-form");
    document.getElementById("create-form-content").innerHTML = form.innerHTML;
}
function createEdit(id) {
    if (id == edit_stager_id) {
        // open modal
        $("#edit-modal").modal("show");
        return;
    }
    let stager = stagers[id];
    let stager_type = stager_types[stager.listener.type];

    // create object of uneditable options
    let uneditable_options = [];
    for (let option of stager_type.options) {
        if (option.editable === false) {
            uneditable_options.push(option.real_name);
        }
    }
    const form = document.getElementById(stager.listener.type + "-form");

    document.getElementById("edit-form").innerHTML = form.innerHTML.replace(/create/g, "edit");

    document.getElementById("id-edit").value = stager.id;
    document.getElementById("name-edit").value = stager.name;
    document.getElementById(stager.payload_type + "-payload_type-edit").selected = true;
    document.getElementById("encoding-edit").value = stager.encoding;
    document.getElementById("random_size-edit").checked = stager.random_size;
    document.getElementById("timeout-edit").value = stager.timeout;
    document.getElementById("delay-edit").value = stager.delay;
    document.getElementById("different_address-edit").value = stager.different_address;


    for (let option_name in stager.options) {
        if (Object.prototype.hasOwnProperty.call(stager.options, option_name)) {
            let option = stager.options[option_name];
            let element = document.getElementById(option_name.toLowerCase() + "-edit");
            if (element.type === "checkbox") {
                element.checked = option;
            }
            element.value = option;
        }
        // check if option is not editable
        if (uneditable_options.includes(option_name)) {
            document.getElementById(option_name.toLowerCase() + "-edit").disabled = true;
        }

    }
    edit_stager_id = id;

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
                // copy to clipboard
                try {
                    navigator.clipboard.writeText(data.stager);
                    showNotification("Failed to copy to clipboard", "danger");
                }
                catch (err) {
                    console.log(err);
                    showNotification("Failed to copy to clipboard", "danger");
                }
            }
            else {
                showNotification(data.message, data.success)
            }
        });
}

