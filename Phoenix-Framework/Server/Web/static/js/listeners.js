let original_create_modal_modal_content = document.getElementById("create-modal-body").innerHTML;
let edit_listener_id = null;

function deleteListener(id) {
    fetch("/listeners/" + id + "/remove?json=true", {
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

function startListener(id) {
    fetch("/listeners/" + id + "/start?json=true", {
        method: "POST"
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

function restartListener(id) {
    showNotification(`Restarting listener ${id}.`, "info");
    fetch("/listeners/" + id + "/restart?json=true", {
        method: "POST"
    }).then(response => response.json())
        .then(data => {
            // show notification
            showNotification(data.message, data.status);
        });
}

function stopListener(id) {
    fetch("/listeners/" + id + "/stop?json=true", {
        method: "POST"
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
    if (id == edit_listener_id) {
        // open modal
        $("#edit-modal").modal("show");
        return;
    }
    let listener = listeners[id];
    // get form by type
    const form = document.getElementById(listener.type + "-form");

    // get modal body
    const modal_body = document.getElementById("edit-modal-body");

    // set modal body
    // replace all create with form
    modal_body.innerHTML = form.innerHTML.replace(/create/g, "edit");

    // set values
    document.getElementById("name-edit").value = listener.name;
    document.getElementById(listener.address + "-address-edit").selected = true;
    document.getElementById("port-edit").value = listener.port;
    document.getElementById("ssl-edit").checked = listener.ssl;
    document.getElementById("enabled-edit").checked = listener.enabled;
    document.getElementById("limit-edit").value = listener.limit;

    // set options
    for (let option_name in listener.options) {
        if (Object.prototype.hasOwnProperty.call(listener.options, option_name)) {
            let option = listener.options[option_name];
            let element = document.getElementById(option_name.toLowerCase() + "-edit");
            if (element.type === "checkbox") {
                element.checked = option;
            }
            element.value = option;
        }
    }

    // open modal
    $("#edit-modal").modal("show");
    console.log("lol");
}


// add event listeners
document.getElementById("type").addEventListener("change", changeCreateType);
console.log(listeners)