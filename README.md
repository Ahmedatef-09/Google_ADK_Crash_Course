# Agent Development Kit (ADK) Crash Course
This repository contains examples for learning Google's Agent Development Kit (ADK), a powerful framework for building LLM-powered agents.

Getting Started
Setup Environment
You only need to create one virtual environment for all examples in this course. Follow these steps to set it up:

1. Create a virtual environment:
python -m venv .venv
2. Activate the virtual environment:
# On Windows
.venv\Scripts\activate
# On macOS and Linux
source .venv/bin/activate


# Install dependencies
pip install -r requirements.txt

Once set up, this single environment will work for all examples in the repository.

Setting Up API Keys
Create an account in Google Cloud https://cloud.google.com/?hl=en
Create a new project
Go to https://aistudio.google.com/apikey
Create an API key
Assign key to the project


GOOGLE_API_KEY=your_api_key_here