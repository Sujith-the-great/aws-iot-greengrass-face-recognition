import json
import base64
import boto3
import numpy as np
import logging
import io
import os
from PIL import Image
from facenet_pytorch import MTCNN
from awscrt import io as awscrt_io, mqtt
from awsiot import mqtt_connection_builder

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FaceDetection")

# AWS Config
REGION = "us-east-1"
SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/476114119085/1229564013-req-queue"
IOT_TOPIC = "clients/1229564013-IoTThing"
ENDPOINT = "a3i8dy55jihsgz-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "MyGreengrassCore"
CERT_PATH = "/greengrass/v2/thingCert.crt"
KEY_PATH = "/greengrass/v2/privKey.key"
ROOT_CA_PATH = "/greengrass/v2/rootCA.pem"

# SQS Client
sqs = boto3.client('sqs', region_name=REGION)

# Face Detector
mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)

# MQTT setup
event_loop_group = awscrt_io.EventLoopGroup(1)
host_resolver = awscrt_io.DefaultHostResolver(event_loop_group)
client_bootstrap = awscrt_io.ClientBootstrap(event_loop_group, host_resolver)

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=CERT_PATH,
    pri_key_filepath=KEY_PATH,
    client_bootstrap=client_bootstrap,
    ca_filepath=ROOT_CA_PATH,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=3600
)

# Message callback
def on_message_received(topic, payload, **kwargs):
    logger.info(f"Received message on topic {topic}")
    try:
        body = json.loads(payload)
        img_base64 = body['encoded']
        request_id = body['request_id']
        filename = body['filename']

        image_bytes = base64.b64decode(img_base64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        face_tensor, prob = mtcnn(image, return_prob=True)

        if face_tensor is not None:
            # Normalize and encode face image
            face_image = face_tensor - face_tensor.min()
            face_image = (face_image / face_image.max() * 255).byte().permute(1, 2, 0).numpy()
            face_pil = Image.fromarray(face_image, mode="RGB")
            buffered = io.BytesIO()
            face_pil.save(buffered, format="JPEG")
            face_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            message = {
                "request_id": request_id,
                "filename": filename,
                "face_image": face_b64
            }

            sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(message))
            logger.info("Face sent to SQS")
        else:
            logger.info("No face detected")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

# Main MQTT connection
connect_future = mqtt_connection.connect()
connect_future.result()
logger.info("Connected to AWS IoT Core",connect_future.result())

subscribe_future, _ = mqtt_connection.subscribe(
    topic=IOT_TOPIC,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=on_message_received
)
subscribe_future.result()
logger.info(f"Subscribed to topic: {IOT_TOPIC} ",subscribe_future.result())

# Keep process alive
try:
    while True:
        pass
except KeyboardInterrupt:
    mqtt_connection.disconnect()
