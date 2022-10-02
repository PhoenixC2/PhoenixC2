let original_create_modal_modal_content = document.getElementById("create-modal-body").innerHTML;
function showNotification(message, type) {

    $.notify({
        icon: "add_alert",
        message: message
  
    },{
        type: type,
        timer: 3000,
        placement: {
            from: "top",
            align: "center"
        }
    });
  }

function resetModal(){
    // reset modal content
    document.getElementById("create-modal-body").innerHTML = original_create_modal_modal_content;
}
function changeCreateType() {
    // get type from select
    const type = document.getElementById("type").value;
    // get corresponding form
    const form = document.getElementById(type + "-form");
    // change content of modal
    document.getElementById("create-modal-body").innerHTML = "<form id='create-form' action='/listeners/add' method='POST'>" + form.innerHTML + "</form>";

}

function createEdit(){}