function change_current_operation(id){
    fetch('/operations/'+ id + '/change?json=true', {
        method: 'POST',
    }).then(response => {
        return response.json();
    }
    ).then(data => {
        // show notification
        showNotification(data.message, data.status);
        // check if success
        if (data.status === 'success') {
            setTimeout(function () {
                location.reload();
            }, 1000);
        }
    });
}