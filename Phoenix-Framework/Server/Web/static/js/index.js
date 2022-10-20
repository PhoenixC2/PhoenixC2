function showNotification(message, status) {

    $.notify({
        icon: "add_alert",
        message: message

    }, {
        type: status,
        timer: 3000,
        placement: {
            from: "top",
            align: "center"
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