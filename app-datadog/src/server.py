from sanic import Sanic
from sanic.response import json

import os

service_name = os.getenv('DD_SERVICE')
app = Sanic(name=service_name)

@app.route('/')
async def test(request):
    param = request.args.get("param")
    if param == "error":
        raise ValueError("forced server error")
    return json({'hello': param})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,auto_reload=True)