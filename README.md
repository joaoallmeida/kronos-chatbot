# 🤖 Kronos - The AI Personal Assistant

![Static Badge](https://img.shields.io/badge/Author-joaoallmeida-red?style=flat-square&color=5B1647)
![Static Badge](https://img.shields.io/badge/Generative-AI-blue?style=flat-square&color=93073E)
![GitHub License](https://img.shields.io/github/license/joaoallmeida/kronos-chatbot?style=flat-square&color=C90035&label=License)
![GitHub Repo stars](https://img.shields.io/github/stars/joaoallmeida/kronos-chatbot?style=flat-square&color=ff5627&label=Stars)
![GitHub contributors](https://img.shields.io/github/contributors/joaoallmeida/kronos-chatbot?style=flat-square&color=ffc400&label=Contributors)
![GitHub top language](https://img.shields.io/github/languages/top/joaoallmeida/kronos-chatbot?style=flat-square&color=1b4f72)

## 🚀 Overview

Kronos - AI Personal Assistant, is a Python-based artificial intelligence application that uses the Langchain library, streamlit, and the Groq Free API to generate high-quality text based on user input. This project aims to facilitate faster and more efficient content creation.

## 📚 Dependencies & Requirements

For the project to work well, the following requirements are necessary:

### Minimum System Requirements

* **OS**: Windows or Linux (preferred)
* **Minimum Memory**: 4 GB
* **Minimum Storage**: 5 GB

### Dependencies

* **Python**: >=3.12
* **Docker**
* **Groq API Key**

### Environment Variables

```bash
GROQ_API_KEY=<your_api_key>
```

To get all Python dependencies, you can cat the **pyproject.toml** or **requirements.txt** files and see all the required dependencies.

## ⚙️ Installation & Configs

### Using Makefile (Linux only)

* ```make build```: Build the docker image and containers
* ```make destroy```: Remove the docker image and containers

### Docker Commands

For Windows system or if you prefer, you can run the following commands in the terminal:

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

## 📝 Authors

* joaoallmeida 😎

## 🔑 License

This project is licensed under the MIT License - See the [LICENSE](LICENSE) file for more details.
