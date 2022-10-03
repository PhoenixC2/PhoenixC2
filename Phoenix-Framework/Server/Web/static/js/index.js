let original_create_modal_modal_content = document.getElementById("create-modal-body").innerHTML;
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

function resetModal() {
    // reset modal content
    document.getElementById("create-modal-body").innerHTML = original_create_modal_modal_content;
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
            // reset modal
            resetModal();
            
            // close modal
            $('#create-modal').modal('hide');
            
            // sleep 1 second
            setTimeout(function() {
                // reload page
                location.reload();
            }   , 1000);
        });
    // activate button
    document.getElementById("create-button").disabled = false;



}
function createEdit() { }

// add event listeners
document.getElementById("type").addEventListener("change", changeCreateType);