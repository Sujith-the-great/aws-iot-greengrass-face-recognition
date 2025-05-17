# AWS IoT Greengrass Edge Face Recognition Pipeline

**Repository:** `aws-iot-greengrass-face-recognition`
<img width="569" alt="image" src="https://github.com/user-attachments/assets/2e5a6203-481a-4c9d-bc9b-3c7355d1e26d" />

---

## 🚀 Project Overview

**Motivation**  
Modern IoT applications demand real-time inference, privacy preservation, and scalable back-end processing. This project demonstrates how to offload compute-intensive face detection to the edge (AWS IoT Greengrass) while leveraging AWS Lambda for scalable face recognition.

**Abstract**  
1. **Edge (Greengrass Core)**  
   - Subscribes to MQTT topic `clients/1229564013-IoTThing`.  
   - Decodes incoming Base64-encoded frames.  
   - Detects faces using MTCNN (facenet-pytorch).  
   - Crops & re-encodes detected faces, then sends them to an SQS “request” queue.

2. **Cloud (AWS Lambda)**  
   - Triggered by “request” SQS.  
   - Loads pretrained FaceNet (InceptionResnetV1).  
   - Computes embeddings, matches against stored database embeddings.  
   - Publishes recognition results (name + request ID) to an SQS “response” queue.

**Key Benefits**  
- **Low Latency**: On-device detection minimizes round-trip time.  
- **Privacy & Bandwidth**: Only face crops travel to the cloud.  
- **Scalability**: Lambda + SQS handle recognition at scale.

---

## 🛠️ Skills & Technologies

- **AWS Services:** IoT Core, Greengrass v2, Lambda, SQS, IAM, ECR  
- **Edge Runtime:** AWS IoT Greengrass custom components  
- **Messaging:** MQTT, SQS triggers  
- **Machine Learning:** Python, facenet-pytorch (MTCNN & InceptionResnetV1)  
- **DevOps:** Docker (for Lambda via ECR), CI/CD patterns, bash scripting  
- **Security:** IAM roles/policies, token exchange, certificate management  

---

## 📦 Repository Structure

```txt
aws-iot-greengrass-face-recognition/
├── README.md
├── greengrass-core/
│   ├── recipes/
│   │   └── com.clientdevices.FaceDetection-1.0.0.json
│   └── artifacts/
│       └── com.clientdevices.FaceDetection/1.0.0/
│           ├── fd_component.py
│           └── facenet_pytorch/      # vendored MTCNN code
├── lambda-face-recognition/
│   ├── Dockerfile                  # Part I ECR approach
│   └── fr_lambda.py                # FaceNet handler
└── Project Requirements/
    └── Project 2 Part I (ECR approach).pdf
    └── Project 2 Part II.pdf
```
# Description

Our application uses AWS IoT Greengrass and AWS Lambda to implement a distributed pipeline to recognize faces in video frames collected from Internet of Things (IoT) devices such as smart cameras.


1. **Frame Capture & Publish:** An IoT device sends video frames to a Greengrass Core device using MQTT.
2. **Edge Face Detection:** A Greengrass component running MTCNN on the Core device processes incoming frames and detects faces.
3. **Queue Request:** Detected face crops are sent to an SQS request queue, triggering the face-recognition Lambda.
4. **Cloud Recognition:** The AWS Lambda function loads a FaceNet model to perform recognition and outputs identified labels.
5. **Response Delivery:** Recognition results are posted to an SQS response queue, which the IoT device retrieves for downstream use.

