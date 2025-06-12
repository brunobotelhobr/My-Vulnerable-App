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
    
def code_execution(request):
    if request.method == 'POST':
        first_name = base64.decodestring(request.POST.get('first_name', ''))
        # #BAD -- Allow user to define code to be run.
        # exec("setname('%s')" % first_name)
        #GOOD --Call code directly
        setname(first_name)