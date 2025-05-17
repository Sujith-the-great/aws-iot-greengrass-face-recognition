import json
import boto3
import torch
import base64
import numpy as np
from PIL import Image
import io
from facenet_pytorch import InceptionResnetV1

sqs = boto3.client('sqs', region_name='us-east-1')

RESPONSE_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/476114119085/1229564013-resp-queue"

resnet = InceptionResnetV1(pretrained='vggface2').eval()
saved_data = torch.load('resnetV1_video_weights.pt')
embedding_list = saved_data[0]
name_list = saved_data[1]

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            message = json.loads(record['body'])
            request_id = message['request_id']
            face_b64 = message['face_image']

            # Decode image
            image_bytes = base64.b64decode(face_b64)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            face_numpy = np.array(image, dtype=np.float32) / 255.0
            face_numpy = np.transpose(face_numpy, (2, 0, 1))
            face_tensor = torch.tensor(face_numpy, dtype=torch.float32)

            # Get embedding
            emb = resnet(face_tensor.unsqueeze(0)).detach()
            distances = [torch.dist(emb, db_emb).item() for db_emb in embedding_list]
            min_idx = distances.index(min(distances))
            result = name_list[min_idx]

            # Send result to SQS
            response = {
                "request_id": request_id,
                "result": result
            }

            sqs.send_message(
                QueueUrl=RESPONSE_QUEUE_URL,
                MessageBody=json.dumps(response)
            )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Face recognition complete."})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
