from globals import *


def routes_endpoints():
    routes = Blueprint("routes", __name__, url_prefix="/auth")
    @routes.route("/home")
    @routes.route("/index")
    @routes.route("/")
    def index():
        return render_template("index.html")
    
    
    return routes
