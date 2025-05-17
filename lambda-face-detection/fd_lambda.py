import json
import boto3
import base64
import os
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import io

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)

sqs = boto3.client('sqs', region_name='us-east-1')

SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/476114119085/1229564013-req-queue"

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        img_base64 = body['content']
        request_id = body['request_id']
        filename = body['filename']

        # Decode image from base64
        image_bytes = base64.b64decode(img_base64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = np.array(image)
        image = Image.fromarray(image)

        # Detect face using MTCNN
        face_tensor, prob = mtcnn(image, return_prob=True)

        if face_tensor is not None:
            # Prepare face image for sending
            face_image = face_tensor - face_tensor.min()
            face_image = face_image / face_image.max()
            face_image = (face_image * 255).byte().permute(1, 2, 0).numpy()
            face_pil = Image.fromarray(face_image, mode="RGB")

            # Convert to base64
            buffered = io.BytesIO()
            face_pil.save(buffered, format="JPEG")
            face_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Prepare message for SQS
            message = {
                "request_id": request_id,
                "filename": filename,
                "face_image": face_b64
            }

            sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message)
            )

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Face sent to recognition queue."})
            }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No face detected"})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
