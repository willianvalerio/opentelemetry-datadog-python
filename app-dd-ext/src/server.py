from sanic import Sanic
from sanic.response import json

from opentelemetry import trace
from opentelemetry.exporter.datadog import (
    DatadogExportSpanProcessor,
    DatadogSpanExporter,
)
from opentelemetry.exporter.datadog.propagator import DatadogFormat
from opentelemetry.propagators import get_global_textmap, set_global_textmap
from opentelemetry.propagators.composite import CompositeHTTPPropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

import os

service_name = os.getenv('DD_SERVICE')
dd_agent = os.getenv('DD_AGENT_HOST')
app = Sanic(name=service_name)


resource = Resource.create({"service.name": service_name})
trace.set_tracer_provider(TracerProvider(resource=resource))

trace.get_tracer_provider().add_span_processor(
    DatadogExportSpanProcessor(
        DatadogSpanExporter(
            agent_url="http://"+dd_agent+":8126", service=service_name
        )
    )
)

global_textmap = get_global_textmap()
if isinstance(global_textmap, CompositeHTTPPropagator) and not any(
    isinstance(p, DatadogFormat) for p in global_textmap._propagators
):
    set_global_textmap(
        CompositeHTTPPropagator(
            global_textmap._propagators + [DatadogFormat()]
        )
    )
else:
    set_global_textmap(DatadogFormat())

tracer = trace.get_tracer(__name__)

@app.route('/')
async def test(request):
    param = request.args.get("param")
    with tracer.start_as_current_span("hello-world"):
        if param == "error":
            raise ValueError("forced server error")
        return json({'hello': param})

if __name__ == '__main__':
    with tracer.start_as_current_span("start"):
        print("Hello world!")
    app.run(host='0.0.0.0', port=5000,auto_reload=True)