from typing import Literal
import requests
from flask import Flask, request

app = Flask(import_name=__name__)

@app.route(rule="/full_ssrf")
def full_ssrf() -> None:
    target = request.args["target"]

    # BAD: user has full control of URL
    resp: requests.Response = requests.get("https://" + target + ".example.com/data/")

    # # GOOD: `subdomain` is controlled by the server.
    # subdomain: Literal['europe'] | Literal['world'] = "europe" if target == "EU" else "world"
    # resp = requests.get(url="https://" + subdomain + ".example.com/data/")