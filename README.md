# 🤖 The AI Personal Assistant: A Python-based Generative AI Model for Content Creation

## 🚀 Overview

The AI Personal Assistant it's an application of intelligence artificial that uses the Langchain library, streamlit and the Groq Free API to generated a high-quality text based on user input. Developed in Python, this project aims to facilitate faster and more efficient content creation.

## 📚 Dependencies & Requirements

For the project to work well, the following requirements are necessary:

### Minimum System Requirements

* **OS**: Windows or Linux (preferred)
* **Minimum Memory**: 2 GB
* **Minimum Storage**: 10 GB

### Dependencies

* **Python**: >=3.12
* **Docker**
* **Groq API Key**
* **Env Variable**: ```GROQ_API_KEY=<your_api_key>```

To get all Python dependencies, you can cat the **pyproject.toml** or **requirements.txt** files and see all the required dependencies.

## ⚙️ Installation & Configs

### Using Makefile (Linux only)

* ```make build```: Build the docker image and containers
* ```make destroy```: Remove the docker image and containers

For Windows System, you need to run the following commands in the terminal:

```bash
# Build
docker build --rm --no-cache -f docker/Dockerfile -t chatbot:latest .
docker compose -f docker/docker-compose.yml up -d

# Destroy
docker compose -f docker/docker-compose.yml down
docker rmi chatbot
docker builder prune -f
```

### Accessing the Application

After the installation, access the application via the URL ```http:\\localhost:8501```.

## 🛠️ Usage & Functionalities

The AI Personal Assistant called **Kronos**, can be used to create a various styles and formats of text's, such as:

* Generating text summaries from PDF or CSV files.
* Creating creative text for stories and poems
* Help develop new skills and improve abilities

### Customiztion

You can define some settings, such as:

* **AI model**: Choose an AI model to generate text according to your needs.
* **Temperature**: The parameter that controls the model's creativity.
* **Max Tokens**: Sets the maximum number of tokens that the model can use to generate text.
* **Response language**: Chooses the response language between Português-BR or English-US.

This way, it is possible to define the best settings for each need.

### Example Use Case

For example, you can use the AI Personal Assistant to generate a summary of a long article or help you understand an article based on a specific topic.

## ▶️ Demo

Below is an demo of application usage:

![demo](docs/demo.gif)
