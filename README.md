# Django REST Framework Chat Application

This project is a chat application built with Django REST Framework, designed for real-time messaging between users. It leverages WebSocket for instant chat updates and JWT (JSON Web Token) for secure authentication and authorization. The project is containerized using Docker, making it easy to deploy and scale.

## Features

- **Real-Time Messaging**: Built with WebSocket support for instant message delivery.
- **Secure Authentication**: Utilizes JWT for robust user authentication and authorization.
- **Dockerized Deployment**: Easy setup and scalability with Docker and Docker Compose.
- **Predefined API Requests**: API requests are organized in a Postman collection for testing convenience.

## Prerequisites

Ensure you have the following installed on your system:
- **Docker**
- **Docker Compose**

## Getting Started

To set up and run the project locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mehran-sfz/Chat-Project.git
2. **Navigate to Project Directory:**
   ```bash
   cd chat_project/chatapi/
3. **Set Permissions for Entrypoint Script: Ensure the entrypoint script is executable:**
   ```bash
   chmod +x entrypoint.sh

4. **Build and Start the Application: Use Docker Compose to build and run the application in detached mode:**
   ```bash
   docker-compose up -d --build

5. **Testing the API: You can now access and test the application’s API. A Postman collection with predefined API requests is provided for convenience.**


## API Documentation

The API endpoints are documented in a Postman collection, located at:
- `chat_project/Postman/`

You can import this collection into Postman to easily explore and test all available endpoints.

## Troubleshooting

If you encounter any issues, check the logs for each container to help diagnose the problem:
```bash
docker-compose logs
