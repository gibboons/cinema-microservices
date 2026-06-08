# Cinema Microservices

## Overview

A cinema platform system built on microservices architecture. The process covers film uploads by studios (with file storage on AWS S3), automatic metadata and transcoding processing, and collecting reviews and ratings from users with automatic recommendation generation.

---

## Architecture

The system consists of **5 independent microservices** communicating through a RabbitMQ message broker running in the cloud (CloudAMQP).

### Microservices

| Service | Port | Responsibility |
|---|---|---|
| `film_upload_service` | 8001 | Receives file from user, saves it to AWS S3, publishes `FilmUploadedEvent` |
| `metadata_service` | 8002 | Consumes `FilmUploadedEvent`, saves film metadata |
| `transcoding_service` | 8003 | Consumes `FilmUploadedEvent`, creates transcoding job |
| `review_service` | 8004 | Receives reviews from user, saves to database |
| `rating_service` | 8005 | Receives ratings, saves to database, generates recommendation and publishes events |

### Event Flow

```
[POST /films/upload]  (title, studio, file)
        │
        ├── upload file → AWS S3
        │
        ▼ FilmUploadedEvent (RabbitMQ fanout)
   ┌────┴──────────────────────────┐
   ▼                               ▼
metadata_service            transcoding_service
(saves metadata)            (creates transcoding job)


[POST /reviews/]  (film_title, reviewer, review_text)
        │
        ▼ ReviewSubmittedEvent (RabbitMQ fanout)


[POST /ratings]  (film_title, user, score)
        │
        ├── saves rating to database
        ├── ▼ RatingSubmittedEvent (RabbitMQ fanout)
        ├── generates recommendation (score ≥ 7.0 → "highly rated", otherwise "moderate")
        └── ▼ RecommendationGeneratedEvent (RabbitMQ fanout)
```

---

## Clean Architecture + CQRS (Onion Architecture)

Each microservice is built according to Clean Architecture and CQRS pattern (using the `diator` library). Layers depend only on inner layers:

```
service/
├── domain/
│   ├── entities/               ← pure dataclasses, zero external dependencies
│   ├── commands/               ← CQRS commands (write operations)
│   ├── queries/                ← CQRS queries (read operations)
│   └── repositories/           ← repository interfaces (Protocol)
├── application/
│   ├── command_handlers/       ← command handlers (write business logic)
│   └── query_handlers/         ← query handlers (read business logic)
├── infrastructure/
│   ├── persistence/            ← SQLAlchemy ORM / boto3 DynamoDB
│   ├── messaging/              ← RabbitMQ publishers and consumers
│   └── storage/                ← AWS S3 client (film_upload_service only)
└── presentation/               ← only in services with REST API
    └── api/                    ← FastAPI routes, Pydantic schemas
```

> `metadata_service` and `transcoding_service` **do not have a presentation layer** — they are purely internal services, communicating only through RabbitMQ. FastAPI serves as a process host (starts the consumer in the background via `lifespan`).

---

## Technologies

| Technology | Usage |
|---|---|
| **FastAPI** | REST API framework — automatic Swagger UI, Pydantic validation |
| **SQLAlchemy** | ORM for communication with RDS PostgreSQL databases |
| **AWS RDS PostgreSQL** | Database for film_upload_service, metadata_service, rating_service |
| **AWS DynamoDB** | Database for review_service, transcoding_service |
| **Pika** | Python library for RabbitMQ communication (AMQP) |
| **RabbitMQ / CloudAMQP** | Cloud-based message broker |
| **Pydantic** | Input and output data validation in API |
| **Python Protocol** | Repository interfaces (structural subtyping) |
| **Diator** | CQRS/Mediator library — binding commands and queries to handlers |
| **Boto3 / AWS S3** | Film file storage in the cloud; presigned URL for downloading |
| **Docker / Docker Compose** | Containerization and local execution of all services |
| **AWS ECR** | Private Docker image registry in the cloud |
| **AWS ECS Fargate** | Running containers in the cloud without managing servers |
| **AWS ALB** | Application Load Balancer — routing traffic to microservices |
| **Terraform** | Infrastructure as Code — automated AWS infrastructure provisioning |
| **AWS CloudWatch** | Collecting and viewing logs from containers |

---

## Design Decisions

### Database per Service
Each microservice owns its own isolated database in AWS. No service accesses another service's database. The database type is matched to the nature of the data:

| Service | Database | Reason |
|---|---|---|
| `film_upload_service` | RDS PostgreSQL | Structured relational data |
| `metadata_service` | RDS PostgreSQL | Structured relational data |
| `rating_service` | RDS PostgreSQL | Relational data with aggregations |
| `review_service` | DynamoDB | Independent document-style records |
| `transcoding_service` | DynamoDB | Simple key-value job entries |

### Fanout Exchange
Events are published to a `fanout` exchange — a single event reaches all subscribers simultaneously without the publisher knowing who they are.

### Files in AWS S3
Uploaded files are stored directly in S3. The download endpoint returns a presigned URL valid for 1 hour — files are never proxied through the application server.

---

## AWS Infrastructure (Terraform)

Deployment split into two Terraform stages following the principle of separating infrastructure from application.

```
terraform/
├── infrastructure/     ← Stage 1 – foundations (created once)
│   ├── vpc.tf          VPC, subnets, Internet Gateway
│   ├── security_groups.tf  firewalls for ALB, ECS, RDS
│   ├── ecr.tf          private Docker image repositories
│   ├── iam.tf          IAM roles for ECS
│   ├── rds.tf          3 RDS PostgreSQL instances
│   ├── dynamodb.tf     2 DynamoDB tables
│   └── s3.tf           S3 bucket for film files
└── services/           ← Stage 2 – application (deployed on every change)
    ├── ecs_cluster.tf  ECS Fargate cluster
    ├── alb.tf          Load Balancer with path-based routing
    ├── cloudwatch.tf   log groups
    └── ecs_services.tf 5 task definitions + 5 ECS services
```

### Deployment Steps

```bash
# 0. Create S3 bucket for Terraform state (once)
aws s3 mb s3://YOUR_STATE_BUCKET --region eu-north-1

# Stage 1 – infrastructure
cd terraform/infrastructure
terraform init \
  -backend-config="bucket=YOUR_STATE_BUCKET" \
  -backend-config="region=eu-north-1"
terraform apply

# Build and push Docker images to ECR
cd ..
./build_and_push.sh latest

# Stage 2 – service deployment
cd services
cp terraform.tfvars.example terraform.tfvars   # fill in secrets
terraform init \
  -backend-config="bucket=YOUR_STATE_BUCKET" \
  -backend-config="region=eu-north-1"
terraform apply
```

---

## Local Setup

### Requirements
- Docker Desktop (with Swarm support)
- CloudAMQP account (free plan: Little Lemur)
- AWS account with S3 bucket, RDS instances and IAM keys

### Configuration
Create a `.env` file in the root project folder:
```
AMQP_URL=amqps://user:password@host.cloudamqp.com/vhost

AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-north-1
AWS_S3_BUCKET=your-bucket-name

FILM_UPLOAD_DB_HOST=your-rds-endpoint
FILM_UPLOAD_DB_PORT=5432
FILM_UPLOAD_DB_NAME=film_upload_db
FILM_UPLOAD_DB_USER=postgres
FILM_UPLOAD_DB_PASSWORD=your-password

METADATA_DB_HOST=your-rds-endpoint
METADATA_DB_PORT=5432
METADATA_DB_NAME=metadata_db
METADATA_DB_USER=postgres
METADATA_DB_PASSWORD=your-password

RATING_DB_HOST=your-rds-endpoint
RATING_DB_PORT=5432
RATING_DB_NAME=rating_db
RATING_DB_USER=postgres
RATING_DB_PASSWORD=your-password

DYNAMODB_REVIEWS_TABLE=reviews
DYNAMODB_TRANSCODING_TABLE=transcoding_jobs
```

> **Note:** the `.env` file contains sensitive data — never commit it to the repository.

### Docker Compose (local dev)
```bash
docker-compose up --build
```

---

## Docker Swarm

The `docker-compose.yml` is configured for Docker Swarm with the following setup:

| Service | Replicas |
|---|---|
| `film_upload_service` | 2 |
| `metadata_service` | 1 |
| `transcoding_service` | 1 |
| `review_service` | 3 |
| `rating_service` | 4 |

All services share an **overlay network** (`cinema-network`) and are configured with:
- **Restart policy** — `on-failure`, max 3 attempts, 5s delay
- **Resource limits** — 0.50 CPU, 512MB RAM per container
- **Resource reservations** — 0.25 CPU, 256MB RAM per container
- **Rolling updates** — 1 replica at a time, 10s delay between updates

### Running with Docker Swarm

```bash
# Build images
docker-compose build

# Initialize Swarm (once)
docker swarm init

# Load environment variables and deploy
export $(cat .env | xargs)
docker stack deploy -c docker-compose.yml cinema
```

### Useful Swarm commands

```bash
# List all services and replica status
docker service ls

# Show all tasks (replicas) for a specific service
docker service ps cinema_rating_service

# Scale a service up or down
docker service scale cinema_film_upload_service=5

# View logs from a service
docker service logs cinema_film_upload_service

# Show overlay network details
docker network inspect cinema_cinema-network

# Remove the entire stack
docker stack rm cinema
```

---

## API: Swagger UI

Available locally at:
- **http://localhost:8001/docs** — Film Upload Service
- **http://localhost:8004/docs** — Review Service
- **http://localhost:8005/docs** — Rating Service

Available on AWS via ALB:
- **http://cinema-alb-935001998.eu-north-1.elb.amazonaws.com/films/**
- **http://cinema-alb-935001998.eu-north-1.elb.amazonaws.com/reviews/**
- **http://cinema-alb-935001998.eu-north-1.elb.amazonaws.com/ratings**

### Endpoints

#### Film Upload Service (`/films`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/films/upload` | Uploads file (multipart: `file`, `title`, `studio`), saves to S3 |
| GET | `/films/` | List all films |
| GET | `/films/{film_id}/download` | Returns presigned URL to download file from S3 (valid 1h) |

#### Review Service (`/reviews`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/reviews/` | Adds review (`film_title`, `reviewer`, `review_text`) |
| GET | `/reviews/` | List all reviews |
| GET | `/reviews/{film_title}` | Reviews for a specific film |

#### Rating Service
| Method | Endpoint | Description |
|---|---|---|
| POST | `/ratings` | Adds rating (`film_title`, `user`, `score`) and generates recommendation |
| GET | `/ratings` | List all ratings |
| GET | `/recommendations` | List all recommendations |

---

## Postman REST API Tests

Import the `Cinema_Microservices_Postman.json` file into Postman.

| # | Test | Method | Endpoint | Assertions |
|---|---|---|---|---|
| 1 | Upload Film File | POST | `/films/upload` | status 201, fields `id`, `s3_key`, correct `extension` |
| 2 | List All Films | GET | `/films/` | status 200, non-empty array |
| 3 | Download Film | GET | `/films/1/download` | status 200, field `presigned_url` |
| 4 | Submit Review | POST | `/reviews/` | status 201, field `id` |
| 5 | List Reviews for Film | GET | `/reviews/Inception` | status 200, array |
| 6 | Submit Rating | POST | `/ratings` | status 201, `score == 9.2` |
| 7 | List All Ratings | GET | `/ratings` | status 200, non-empty array |
| 8 | List Recommendations | GET | `/recommendations` | status 200, non-empty array |

### Testing Order
1. Run **TEST 1** manually — requires selecting a file in the `file` field and filling in `title` and `studio`
2. Wait 2-3 seconds for event propagation through RabbitMQ
3. Run remaining tests — in Postman: **Run Collection**

---

## Logger

Each microservice uses a shared logger (`shared/logger.py`). Each method logs its invocation:

```
film_upload_service | routes.upload_film() - file=film.mp4, title=Inception
film_upload_service | FilmUploadDB - connected to RDS PostgreSQL successfully
film_upload_service | S3StorageService.upload_file() - key=uploads/film.mp4, size=104857600
film_upload_service | BasePublisher.publish() - FilmUploadedEvent: {...}
metadata_service    | MetadataDB - connected to RDS PostgreSQL successfully
metadata_service    | FilmUploadedConsumer.handle() - {'title': 'Inception', 'studio': 'Warner'}
metadata_service    | SaveMetadataCommandHandler.handle() - title=Inception
transcoding_service | TranscodingDB - connected to DynamoDB successfully
transcoding_service | FilmUploadedConsumer.handle() - creating job for: Inception
rating_service      | RatingDB - connected to RDS PostgreSQL successfully
rating_service      | SubmitRatingCommandHandler.handle() - film=Inception, score=9.2
rating_service      | SubmitRatingCommandHandler.handle() - recommendation generated
```

---

## Verifying the Message Broker

1. Log in to **cloudamqp.com**
2. Open **RabbitMQ Manager**
3. **Connections** tab — active service connections
4. **Queues** tab — consumer queues (created on startup)
5. **Exchanges** tab — fanout exchanges (`FilmUploadedEvent`, `ReviewSubmittedEvent`, `RatingSubmittedEvent`, `RecommendationGeneratedEvent`)
6. **Overview** tab — real-time message flow chart
