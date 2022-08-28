from flask import Response, jsonify, redirect, flash
def generate_response(use_json:bool, alert:str, text:str, redirect_location:str, response_code: int=200) -> Response:
    """Generate the Endpoint Response"""
    if use_json:
        return jsonify({"status": alert, "message": text}), response_code
    flash(text, alert)
    return redirect("/" + redirect_location)
