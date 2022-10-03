let original_create_modal_modal_content = document.getElementById("create-modal-body").innerHTML;

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

function showCreateModal() {
    document.getElementById("create-modal-body").innerHTML = original_create_modal_modal_content;
    document.getElementById("create-modal").style.display = "block";
}

function resetModal() {
    // reset modal content
    document.getElementById("create-modal-body").innerHTML = original_create_modal_modal_content;
}
function createEdit(id) {
    // get column data
    const name = document.getElementById("name-" + id).innerHTML;
    const address = document.getElementById("address-" + id).innerHTML;
    const port = document.getElementById("port-" + id).innerHTML;
    const type = document.getElementById("type-" + id).innerHTML;
    const ssl = document.getElementById("ssl-" + id).innerHTML;
    const enabled = document.getElementById("enabled-" + id).innerHTML;

    // get form 
    const form = document.getElementById(type + "-form");
    // change content of modal
    document.getElementById("edit-form").innerHTML = form.innerHTML;
    // set values
    document.getElementById("name").value = name;
    document.getElementById("address").value = address;
    document.getElementById("port").value = port;
    document.getElementById("ssl").value = ssl;
    document.getElementById("enabled").value = enabled;
    // TODO: create edit

}


function changeCreateType() {
    // get type from select
    const type = document.getElementById("type").value;
    // get corresponding form
    const form = document.getElementById(type + "-form");
    // change content of modal
    document.getElementById("create-form").innerHTML = form.innerHTML +
        "<input type='button' id='create-button' onclick='sendCreate()' value='Create' class='btn btn-success' />" +
        "<input type='reset' value='Reset' class='btn btn-danger' />"
}
function sendCreate() {
    console.log("send create");
    // disable button
    document.getElementById("create-button").disabled = true;
    // get form
    const form = document.getElementById("create-form");
    // get data
    const data = new FormData(form);
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

// add event listeners
document.getElementById("type").addEventListener("change", changeCreateType);