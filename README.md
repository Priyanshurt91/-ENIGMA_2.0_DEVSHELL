[Cancer pre]

📌 Project Overview

This project is an advanced AI-powered medical imaging platform designed to detect multiple cancers and generate clinically structured reports using deep learning, explainable AI (Grad-CAM), Retrieval-Augmented Generation (RAG), and Large Language Models.

The system integrates:

Deep Learning Models (.pt / .h5)

Grad-CAM for model explainability

RAG using ChromaDB medical knowledge base

Gemini LLM for clinical report generation

React (Frontend)

FastAPI (Backend)

🔄 Complete System Workflow
Image Upload
      ->
Model Inference (.pt / .h5)
      ->
Grad-CAM Heatmap Generation
      ->
RAG (ChromaDB Medical Knowledge Retrieval)
      ->
Gemini API (Clinical Report Generation)
      ->
Final Result Display (Prediction + Heatmap + AI Report)
🧠 AI Models Used
1️⃣ Blood Cancer Detection

Model: MobileNetV2 (.h5)

Input: Blood smear images

Output: Cancer classification

2️⃣ Spleen Cancer Detection

Model: 3D U-Net (.pt)

Input: 3D CT/MRI volumetric scans

Output: Tumor segmentation mask

3️⃣ Lung Cancer Detection

Model: ResNet (.pt)

Input: CT scan images

Output: Cancer classification

4️⃣ Brain Tumor Detection

Model: ResNet (.pt)

Input: MRI scans

Output: Tumor classification

🔥 Explainable AI – Grad-CAM

To enhance transparency and trust:

Grad-CAM is applied to classification models.

Generates heatmaps highlighting important regions.

Overlays heatmap on original scan.

Helps visualize tumor activation areas.

This improves clinical interpretability and model explainability.

📚 RAG (Retrieval-Augmented Generation)
🔹 Vector Database: ChromaDB

The system uses ChromaDB to store:

Medical research papers

Cancer treatment guidelines

Clinical knowledge summaries

WHO / oncology reference material

🔹 How RAG Works

Model prediction is structured into query format.

Relevant medical knowledge is retrieved from ChromaDB.

Retrieved context is passed along with prediction to Gemini.

Gemini generates context-aware clinical reports.

This ensures reports are:

Fact-grounded

Clinically relevant

Context-aware

Not purely hallucinated by LLM

🤖 Clinical Report Generation – Gemini API

After RAG retrieval:

Structured findings + retrieved medical context

Sent to Gemini LLM

Gemini generates:

Diagnostic summary

Tumor description

Risk assessment

Suggested next steps

Clinical disclaimer

🏗️ System Architecture
React Frontend
      ->
FastAPI Backend
      ->
Model Layer (.pt/.h5)
      ->
Grad-CAM Engine
      -> 
ChromaDB (RAG)
      ->
Gemini API
      ->
Frontend Result Display
🌐 Tech Stack
Frontend

React (JSX)

Axios

HTML / CSS

Backend

FastAPI

Python

Uvicorn

Pydantic

Deep Learning

PyTorch (.pt models)

TensorFlow/Keras (.h5 models)

OpenCV

NumPy

Explainability

Grad-CAM

RAG

ChromaDB

Sentence Transformers (Embeddings)

LLM

Gemini API (Google Generative AI)
Project Interface
<img width="1599" height="715" alt="image" src="https://github.com/user-attachments/assets/afdc4287-ff6d-4ede-b0be-076ec10b773d" />
<img width="1591" height="713" alt="image" src="https://github.com/user-attachments/assets/69061c78-40e5-4e3e-b698-2b2a68024fba" />
<img width="1590" height="690" alt="image" src="https://github.com/user-attachments/assets/251ab58d-fdf7-4911-9f02-8cbde3196234" />
<img width="1588" height="529" alt="image" src="https://github.com/user-attachments/assets/8ff89849-da8b-4a0f-915f-a38a0bfd2434" />


System Architecture

<img width="1719" height="347" alt="image" src="https://github.com/user-attachments/assets/b7c5c8f4-68a8-4951-9a43-888a73b7a68c" />





