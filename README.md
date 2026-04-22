# Cinema Microservices

## Opis procesu

System obsługi platformy kinowej oparty na architekturze mikroserwisów. Proces obejmuje przesyłanie filmów przez studio, automatyczne przetwarzanie metadanych i transcodingu, oraz zbieranie recenzji i ocen od użytkowników z automatycznym generowaniem rekomendacji.

---

## Architektura

System składa się z **5 niezależnych mikroserwisów** komunikujących się przez brokera wiadomości RabbitMQ działającego w środowisku chmurowym (CloudAMQP).

### Mikroserwisy

| Serwis | Port | Odpowiedzialność |
|---|---|---|
| `film_upload_service` | 8001 | Odbiera plik od użytkownika, loguje nazwę i rozszerzenie, publikuje `FilmUploadedEvent` |
| `metadata_service` | 8002 | Konsumuje `FilmUploadedEvent`, zapisuje metadane filmu |
| `transcoding_service` | 8003 | Konsumuje `FilmUploadedEvent`, tworzy job transcodingu |
| `review_service` | 8004 | Odbiera recenzje od użytkownika, zapisuje do bazy |
| `rating_service` | 8005 | Odbiera oceny, generuje rekomendacje na podstawie wyniku |

### Przepływ zdarzeń

```
[POST /films/upload]
        │
        ▼ FilmUploadedEvent (RabbitMQ fanout)
   ┌────┴──────────────────────────┐
   ▼                               ▼
metadata_service            transcoding_service
(zapisuje metadane)         (tworzy job transcodingu)




[POST /reviews/]
        │
        ▼ ReviewSubmittedEvent (RabbitMQ)




[POST /ratings]
        │
        ▼ RatingSubmittedEvent (RabbitMQ)
        │ (self-consume)
        ▼
RecommendationGeneratedEvent
(zapisuje rekomendację do bazy)
```

---

## Clean Architecture (Onion Architecture)

Każdy mikroserwis jest zbudowany zgodnie z Clean Architecture. Warstwy zależą tylko od warstw wewnętrznych:

```
service/
├── domain/
│   ├── entities/               ← czyste dataclassy, zero zależności zewnętrznych
│   └── repositories/           ← interfejsy repozytoriów (Protocol)
├── application/
│   └── services/               ← logika biznesowa
├── infrastructure/
│   ├── persistence/            ← SQLAlchemy ORM, baza SQLite
│   └── messaging/              ← publishery i consumery RabbitMQ
└── presentation/               ← tylko w serwisach z REST API
    └── api/                    ← FastAPI routes, schematy Pydantic
```

> `metadata_service` i `transcoding_service` **nie posiadają warstwy presentation** — są serwisami czysto wewnętrznymi, komunikują się wyłącznie przez RabbitMQ.

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

### Presentation tylko gdzie potrzeba
Warstwa `presentation/` istnieje tylko w serwisach które wystawiają REST API dla użytkownika (`film_upload_service`, `review_service`, `rating_service`). Serwisy wewnętrzne (`metadata_service`, `transcoding_service`) komunikują się wyłącznie przez RabbitMQ.

### Fanout Exchange
`FilmUploadedEvent` publikowany jest na exchange typu `fanout` — jeden event trafia jednocześnie do `metadata_service` i `transcoding_service` bez konieczności znajomości adresatów przez publishera.

---

## Uruchomienie

### Wymagania
- Docker Desktop
- Konto CloudAMQP (plan free: Little Lemur)

### Konfiguracja
Utwórz plik `.env` w głównym folderze projektu:
```
AMQP_URL=amqps://user:password@host.cloudamqp.com/vhost
```

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

---

## Testy REST API w Postmanie

Zaimportuj plik `Cinema_Microservices_Postman.json` do Postmana.

| # | Test | Metoda | Endpoint | Asercje |
|---|---|---|---|---|
| 1 | Upload Film File | POST | `/films/upload` | status 201, pole `id`, poprawne `extension` |
| 2 | List All Films | GET | `/films/` | status 200, tablica niepusta |
| 3 | Submit Review | POST | `/reviews/` | status 201, pole `id` |
| 4 | List Reviews for Film | GET | `/reviews/Inception` | status 200, tablica |
| 5 | Submit Rating | POST | `/ratings` | status 201, `score == 9.2` |
| 6 | List All Ratings | GET | `/ratings` | status 200, tablica niepusta |
| 7 | List Recommendations | GET | `/recommendations` | status 200, tablica |

### Kolejność testowania
1. Uruchom **TEST 1** ręcznie — wymaga wskazania pliku w polu `file`
2. Odczekaj 2-3 sekundy na propagację eventów przez RabbitMQ
3. Uruchom pozostałe testy — w Postmanie: **Run Collection**

---

## Logger

Każdy mikroserwis korzysta ze wspólnego loggera (`shared/logger.py`). Każda metoda loguje swoje wywołanie:

```
film_upload_service | FilmService.upload_film() - filename=film.mp4
film_upload_service | FilmService.upload_film() - detected extension: .mp4
film_upload_service | FilmRepository.save() - film.mp4
film_upload_service | BasePublisher.publish() - FilmUploadedEvent: {...}
metadata_service    | FilmUploadedConsumer.handle() - {'title': 'Inception'...}
metadata_service    | MetadataService.save_from_event() - title=Inception
transcoding_service | TranscodingService.create_job_from_event() - title=Inception
```

---

## Weryfikacja działania brokera

1. Zaloguj się na **cloudamqp.com**
2. Otwórz **RabbitMQ Manager**
3. Zakładka **Connections** — aktywne połączenia serwisów
4. Zakładka **Queues** — kolejki konsumerów (tworzone przy starcie)
5. Zakładka **Exchanges** — exchange'e typu fanout (`FilmUploadedEvent`, `RatingSubmittedEvent`)
6. Zakładka **Overview** — wykres przepływu wiadomości w czasie rzeczywistym
