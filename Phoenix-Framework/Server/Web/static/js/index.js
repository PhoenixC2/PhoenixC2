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