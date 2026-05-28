# Cinema Microservices

## Opis procesu

System obsługi platformy kinowej oparty na architekturze mikroserwisów. Proces obejmuje przesyłanie filmów przez studio (z zapisem pliku na AWS S3), automatyczne przetwarzanie metadanych i transcodingu, oraz zbieranie recenzji i ocen od użytkowników z automatycznym generowaniem rekomendacji.

---

## Architektura

System składa się z **5 niezależnych mikroserwisów** komunikujących się przez brokera wiadomości RabbitMQ działającego w środowisku chmurowym (CloudAMQP).

### Mikroserwisy

| Serwis | Port | Odpowiedzialność |
|---|---|---|
| `film_upload_service` | 8001 | Odbiera plik od użytkownika, zapisuje go na AWS S3, publikuje `FilmUploadedEvent` |
| `metadata_service` | 8002 | Konsumuje `FilmUploadedEvent`, zapisuje metadane filmu |
| `transcoding_service` | 8003 | Konsumuje `FilmUploadedEvent`, tworzy job transcodingu |
| `review_service` | 8004 | Odbiera recenzje od użytkownika, zapisuje do bazy |
| `rating_service` | 8005 | Odbiera oceny, zapisuje do bazy, generuje rekomendację i publikuje eventy |

### Przepływ zdarzeń

```
[POST /films/upload]  (title, studio, file)
        │
        ├── upload pliku → AWS S3
        │
        ▼ FilmUploadedEvent (RabbitMQ fanout)
   ┌────┴──────────────────────────┐
   ▼                               ▼
metadata_service            transcoding_service
(zapisuje metadane)         (tworzy job transcodingu)


[POST /reviews/]  (film_title, reviewer, review_text)
        │
        ▼ ReviewSubmittedEvent (RabbitMQ fanout)


[POST /ratings]  (film_title, user, score)
        │
        ├── zapisuje ocenę do bazy
        ├── ▼ RatingSubmittedEvent (RabbitMQ fanout)
        ├── generuje rekomendację (score ≥ 7.0 → "wysoko oceniony", inaczej "umiarkowanie")
        └── ▼ RecommendationGeneratedEvent (RabbitMQ fanout)
```

---

## Clean Architecture + CQRS (Onion Architecture)

Każdy mikroserwis jest zbudowany zgodnie z Clean Architecture i wzorcem CQRS (biblioteka `diator`). Warstwy zależą tylko od warstw wewnętrznych:

```
service/
├── domain/
│   ├── entities/               ← czyste dataclassy, zero zależności zewnętrznych
│   ├── commands/               ← komendy CQRS (operacje zapisu)
│   ├── queries/                ← zapytania CQRS (serwisy z REST API)
│   └── repositories/           ← interfejsy repozytoriów (Protocol)
├── application/
│   ├── command_handlers/       ← handlery komend (logika biznesowa zapisu)
│   └── query_handlers/         ← handlery zapytań (serwisy z REST API)
├── infrastructure/
│   ├── persistence/            ← SQLAlchemy ORM, baza SQLite
│   ├── messaging/              ← publishery i consumery RabbitMQ
│   └── storage/                ← klient AWS S3 (tylko film_upload_service)
└── presentation/               ← tylko w serwisach z REST API
    └── api/                    ← FastAPI routes, schematy Pydantic
```

> `metadata_service` i `transcoding_service` **nie posiadają warstwy presentation** — są serwisami czysto wewnętrznymi, komunikują się wyłącznie przez RabbitMQ. FastAPI pełni w nich rolę hosta procesu (uruchamia consumer w tle przez `lifespan`).

---

## Technologie

| Technologia | Zastosowanie |
|---|---|
| **FastAPI** | Framework REST API — automatyczny Swagger UI, walidacja przez Pydantic |
| **SQLAlchemy** | ORM do komunikacji z bazą danych |
| **SQLite** | Baza danych — każdy serwis ma własny plik `.db` |
| **Pika** | Biblioteka Python do komunikacji z RabbitMQ (AMQP) |
| **RabbitMQ / CloudAMQP** | Broker wiadomości działający w chmurze |
| **Pydantic** | Walidacja danych wejściowych i wyjściowych w API |
| **Python Protocol** | Interfejsy repozytoriów (structural subtyping) |
| **Diator** | Biblioteka CQRS/Mediator — wiązanie komend i zapytań z handlerami |
| **Boto3 / AWS S3** | Przechowywanie plików filmowych w chmurze; presigned URL do pobierania |
| **Docker / Docker Compose** | Konteneryzacja i uruchomienie wszystkich serwisów |

---

## Decyzje projektowe

### Database per Service
Każdy mikroserwis posiada własną, niezależną bazę danych. Żaden serwis nie sięga do bazy innego.

| Serwis | Plik bazy |
|---|---|
| film_upload_service | `film_upload.db` |
| metadata_service | `metadata.db` |
| transcoding_service | `transcoding.db` |
| review_service | `reviews.db` |
| rating_service | `ratings.db` |

### WAL Mode (Write-Ahead Log)
SQLite skonfigurowany z WAL mode aby uniknąć konfliktów między wątkiem HTTP (FastAPI) a wątkiem consumera RabbitMQ przy jednoczesnym zapisie do bazy.

### Sesja per wiadomość
Consumer tworzy nową sesję bazy danych dla każdej odebranej wiadomości i zamyka ją natychmiast po przetworzeniu. Zapobiega to długo żyjącym sesjom które blokowałyby bazę.

### Python Protocol zamiast ABC
Interfejsy repozytoriów zdefiniowane jako `Protocol` z modułu `typing` — klasy implementujące nie muszą dziedziczyć, wystarczy że posiadają odpowiednie metody (duck typing z formalnym kontraktem).

### CQRS z Diator
Komendy (zapis) i zapytania (odczyt) rozdzielone przez wzorzec Mediator. Każdy handler rejestrowany w `SimpleContainer` — własnym lekkim kontenerze DI kompatybilnym z interfejsem Diatora.

### Presentation tylko gdzie potrzeba
Warstwa `presentation/` istnieje tylko w serwisach które wystawiają REST API dla użytkownika (`film_upload_service`, `review_service`, `rating_service`). Serwisy wewnętrzne (`metadata_service`, `transcoding_service`) uruchamiają consumer RabbitMQ przez FastAPI `lifespan`.

### Fanout Exchange
Każdy event publikowany jest na exchange typu `fanout` — jeden event trafia jednocześnie do wszystkich subskrybentów bez konieczności znajomości adresatów przez publishera.

### Pliki w AWS S3
`film_upload_service` zapisuje przesłany plik bezpośrednio do bucketu S3. Endpoint pobierania zwraca presigned URL ważny przez 1 godzinę — plik nigdy nie jest przepuszczany przez serwer.

---

## Uruchomienie

### Wymagania
- Docker Desktop
- Konto CloudAMQP (plan free: Little Lemur)
- Konto AWS z bucketem S3 i kluczami IAM

### Konfiguracja
Utwórz plik `.env` w głównym folderze projektu:
```
AMQP_URL=amqps://user:password@host.cloudamqp.com/vhost

AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-north-1
AWS_S3_BUCKET=your-bucket-name
```

> **Uwaga:** plik `.env` zawiera poufne dane — nigdy nie commituj go do repozytorium.

### Docker Compose
```bash
docker-compose up --build
```

### Lokalnie (bez Dockera)
W każdym katalogu serwisu:
```bash
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

---

## API: Swagger UI

Po uruchomieniu dostępne pod adresami:
- **http://localhost:8001/docs** — Film Upload Service
- **http://localhost:8004/docs** — Review Service
- **http://localhost:8005/docs** — Rating Service

### Endpoints

#### Film Upload Service (`/films`)
| Metoda | Endpoint | Opis |
|---|---|---|
| POST | `/films/upload` | Przesyła plik (multipart: `file`, `title`, `studio`), zapisuje na S3 |
| GET | `/films/` | Lista wszystkich filmów |
| GET | `/films/{film_id}/download` | Zwraca presigned URL do pobrania pliku z S3 (ważny 1h) |

#### Review Service (`/reviews`)
| Metoda | Endpoint | Opis |
|---|---|---|
| POST | `/reviews/` | Dodaje recenzję (`film_title`, `reviewer`, `review_text`) |
| GET | `/reviews/` | Lista wszystkich recenzji |
| GET | `/reviews/{film_title}` | Recenzje dla konkretnego filmu |

#### Rating Service
| Metoda | Endpoint | Opis |
|---|---|---|
| POST | `/ratings` | Dodaje ocenę (`film_title`, `user`, `score`) i generuje rekomendację |
| GET | `/ratings` | Lista wszystkich ocen |
| GET | `/recommendations` | Lista wszystkich rekomendacji |

---

## Logger

Każdy mikroserwis korzysta ze wspólnego loggera (`shared/logger.py`). Każda metoda loguje swoje wywołanie:

```
film_upload_service | routes.upload_film() - file=film.mp4, title=Inception
film_upload_service | S3StorageService.upload_file() - key=uploads/film.mp4, size=104857600
film_upload_service | BasePublisher.publish() - FilmUploadedEvent: {...}
metadata_service    | FilmUploadedConsumer.handle() - {'title': 'Inception', 'studio': 'Warner'}
metadata_service    | SaveMetadataCommandHandler.handle() - title=Inception
transcoding_service | FilmUploadedConsumer.handle() - creating job for: Inception
rating_service      | SubmitRatingCommandHandler.handle() - film=Inception, score=9.2
rating_service      | SubmitRatingCommandHandler.handle() - recommendation generated
```

---

## Weryfikacja działania brokera

1. Zaloguj się na **cloudamqp.com**
2. Otwórz **RabbitMQ Manager**
3. Zakładka **Connections** — aktywne połączenia serwisów
4. Zakładka **Queues** — kolejki konsumerów (tworzone przy starcie)
5. Zakładka **Exchanges** — exchange'e typu fanout (`FilmUploadedEvent`, `ReviewSubmittedEvent`, `RatingSubmittedEvent`, `RecommendationGeneratedEvent`)
6. Zakładka **Overview** — wykres przepływu wiadomości w czasie rzeczywistym
