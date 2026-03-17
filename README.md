# 🌍 Smart Travel Planner AI
[![CI/CD Pipeline](https://github.com/WukerDev/Smart-Travel-Planner/actions/workflows/ci.yml/badge.svg)](https://github.com/WukerDev/Smart-Travel-Planner/actions)

Nowoczesna aplikacja webowa do kompleksowego planowania podróży, wspierana przez lokalne modele wielkojęzyczne (LLM) oraz integrację z zewnętrznymi API turystycznymi.

---

## 🚀 Kluczowe Funkcjonalności
* **AI Itinerary Generator:** Generowanie spersonalizowanych planów zwiedzania (Llama 3.1 via Ollama).
* **Live Flight & Hotel Search:** Integracja z RapidAPI (Sky Scrapper & Booking.com).
* **Interactive Mapping:** Wizualizacja tras lotów i atrakcji (POI) przy użyciu OpenLayers.
* **Real-time Weather:** 5-dniowa prognoza pogody dla wybranej destynacji.
* **AI Travel Assistant:** Interaktywny czat z asystentem podróży działający w 100% lokalnie.
* **Modern UI/UX:** Responsywny interfejs z trybem Dark/Light mode i efektami szklanymi (Glassmorphism).

## 🛠 Stos Technologiczny
### Frontend
* **Vue 3** (Composition API) + **Vite**
* **Vuetify 3** (Material Design Component Library)
* **Pinia** (State Management)
* **OpenLayers** (Mapy wektorowe)

### Backend
* **FastAPI** (Python 3.11+)
* **MongoDB** + **Motor** (Asynchroniczny sterownik bazy danych)
* **Ollama** (Lokalne hostowanie modelu Llama 3.1)
* **Pytest** (Automatyczne testy jednostkowe i integracyjne)

### DevOps & Infrastructure
* **Docker & Docker Compose** (Konteneryzacja usług)
* **GitHub Actions** (Automatyczny pipeline CI/CD)
* **GHCR** (GitHub Container Registry dla obrazów Dockera)

## 🏗 Architektura Projektu
Projekt został zaprojektowany w architekturze mikroserwisowej z wyraźnym odseparowaniem logiki biznesowej od warstwy prezentacji:
1.  **Frontend:** SPA komunikujące się z API poprzez asynchroniczne zapytania HTTP.
2.  **Backend:** REST API z zaimplementowanym mechanizmem **Cache-aside** (buforowanie wyników API w MongoDB) oraz **Fallback mechanism** (generowanie realistycznych danych w przypadku awarii zewnętrznych usług).
3.  **Baza Danych:** NoSQL MongoDB służąca jako cache oraz magazyn słowników lotnisk i destynacji.

graph TD
    User((Użytkownik)) <--> Frontend[Vue 3 + Vuetify SPA]
    Frontend <--> Backend[FastAPI Backend]
    Backend <--> MongoDB[(MongoDB Cache)]
    Backend <--> Ollama[Llama 3.1 LLM]
    Backend <--> RapidAPI[External Travel APIs]
    Backend <--> OpenWeather[Weather API]

## 🚦 Szybki Start
Aby uruchomić projekt lokalnie, wymagany jest zainstalowany Docker oraz Ollama.

```bash
# 1. Sklonuj repozytorium
git clone [https://github.com/WukerDev/Smart-Travel-Planner.git](https://github.com/WukerDev/Smart-Travel-Planner.git)

# 2. Uruchom infrastrukturę
docker-compose up -d
