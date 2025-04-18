import uvicorn
from fastapi import FastAPI, Request
from fastapi import HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
load_dotenv()


provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"{__name__} started")

tracer = trace.get_tracer(__name__)
trace.set_tracer_provider(provider)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/email")
# async def email(request: Request):
#     with tracer.start_as_current_span("send_email") as span:
#         try:
#             messageContents = await request.json()
#             span.set_attribute("email.subject",messageContents["subject"])
#             span.set_attribute("email.from",messageContents["email"])

#             message = Mail(
#                 to_emails=os.environ.get('SENDGRID_TO_EMAIL'),
#                 from_email=os.environ.get('SENDGRID_FROM_EMAIL'),
#                 subject=messageContents["subject"],
#                 html_content= f"{messageContents["message"]}<br />{messageContents["name"]}")
#             message.reply_to = messageContents["email"]

#             sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
#             response = sg.send(message)
#             span.set_attributes("email.status", "success")
#             span.set_status(Status(StatusCode.OK))
#             return response    
#         except Exception as e:
#             span.set_attributes("email.status", "error")
#             span.set_attributes("email.error", str(e))
#             span.set_status(Status(StatusCode.ERROR, str(e)))
#             logger.error(f"Exception:: {e:args}",exc_info=True)
#             return e

@app.post("/email")
async def email(request: Request):
    with tracer.start_as_current_span("send_email") as span:
        try:
            messageContents = await request.json()
            span.set_attribute("email.subject", messageContents["subject"])
            span.set_attribute("email.from", messageContents["email"])

            message = Mail(
                to_emails=os.environ.get('SENDGRID_TO_EMAIL'),
                from_email=os.environ.get('SENDGRID_FROM_EMAIL'),
                subject=messageContents["subject"],
                html_content=f"{messageContents['message']}<br />{messageContents['name']}"
            )
            message.reply_to = messageContents["email"]

            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)

            span.set_attribute("email.status", "success")
            span.set_status(Status(StatusCode.OK))

            return {
                "status": "success",
                "message": "Email sent successfully",
                "status_code": response.status_code
            }

        except Exception as e:
            span.set_attribute("email.status", "error")
            span.set_attribute("email.error", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error(f"Exception: {e}", exc_info=True)

            return {
                "status": "error",
                "message": str(e)
            }, 500

    
app.mount('/', StaticFiles(directory="./dist", html=True), name="src")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)