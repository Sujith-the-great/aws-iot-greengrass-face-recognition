# AWS IoT Greengrass Edge Face Recognition Pipeline

**Repository:** `aws-iot-greengrass-face-recognition`
<img width="569" alt="image" src="https://github.com/user-attachments/assets/2e5a6203-481a-4c9d-bc9b-3c7355d1e26d" />

---

## 🚀 Project Overview

**Motivation**  
Modern IoT applications demand real-time inference, privacy preservation, and scalable back-end processing. This project demonstrates how to offload compute-intensive face detection to the edge (AWS IoT Greengrass) while leveraging AWS Lambda for scalable face recognition.

**Abstract**  
1. **Edge (Greengrass Core)**  
   - Subscribes to MQTT topic `clients/<ASU-ID>-IoTThing`.  
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
