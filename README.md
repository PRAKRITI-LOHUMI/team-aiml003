Agentic AI for Cloud Operations
An intelligent assistant that accepts natural language instructions to manage OpenStack cloud resources through conversation.

Features
Natural Language Interface: Parse user requests using intent recognition

Cloud Resource Management: Create, resize, and delete VMs, networks, and volumes

Confirmation Workflow: Explicit confirmation for all resource-modifying operations

Usage Monitoring: Query project resource utilization

Conversation History: All interactions logged to database

Architecture
The system consists of:

NLP Engine: Rule-based parser with OpenHermes model integration

OpenStack API Clients: Nova, Neutron, and Cinder integration

Confirmation Module: Ensures user approval before execution

Web Interface: Chat-based UI for interacting with the agent

Example Commands
text
"Create an S.4 VM named dev-box"
"Resize dev-box to flavor M.8"
"Delete the VM dev-box"
"Create a private network called blue-net"
"Create a 100 GB volume named data-disk"
"What's my project usage?"
Setup and Installation
Prerequisites
Python 3.8 or higher

OpenStack credentials

Git

Installation Steps
Clone the repository:

bash
git clone https://github.com/yourusername/cloud-operations-agent.git
cd cloud-operations-agent
Create a virtual environment:

bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
Install dependencies:

bash
pip install -r requirements.txt
Create a .env file with your OpenStack credentials:

text
OS_AUTH_URL=https://your-openstack-url:5000
OS_USERNAME=your-username
OS_PASSWORD=your-password
OS_PROJECT_ID=your-project-id
OS_USER_DOMAIN_NAME=Default
Initialize the database:

bash
python init_db.py
Start the application:

bash
uvicorn app.main:app --reload
Access the web interface at http://127.0.0.1:8000/static/index.html

Project Structure
text
cloud-operations-agent/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── openstack/                 # OpenStack API clients
│   ├── api/                       # API endpoints
│   ├── models/                    # Database models
│   ├── nlp/                       # Intent recognition
│   └── static/                    # Web interface
├── tests/                         # Automated tests
├── .env                           # Environment variables
├── init_db.py                     # Database initialization
├── requirements.txt               # Dependencies
└── README.md                      # This file
Security
TLS encryption for all API communications

Explicit confirmation for resource-modifying operations

Environment-based credential storage

License
This project is licensed under the MIT License - see the LICENSE file for details.
