Plan funkcjonalny (podzielony na aplikacje)

Users (auth, profil, konto)
- [x] Profil: GET /api/users/profile/ (avatar, HP, EXP, poziom, bonusy, bez e‑maila).
- [x] Rejestracja/logowanie/odświeżenie/wylogowanie.
- [x] Zmiana hasła; aktualizacja profilu (avatar, e‑mail opcjonalny).
- [x] Polityka haseł i throttling dla endpointów auth.

Tasks (habits, dailies, todos)
- Listy: nawyki (słabe/mocne), codzienne (dzisiejsze/nieaktywne), do zrobienia (aktywne/zaplanowane/wykonane).
- Filtrowanie po statusach; opcjonalnie siła nawyków.

Inventory (ekwipunek)
- Wyposażenie, skrzynia, narzędzia (budowa posiadłości).
- Relacje z użytkownikiem, flaga „equipped”, wpływ na statystyki.

Estate / Homestead (posiadłość)
- Widok posiadłości: Dom, tartak, kamieniołom, kopalnia żelaza, obiekty do treningu.
- Bonusy przechowywane elastycznie (JSONField), endpointy: GET /homestead/, POST /build/.
- Generowanie zasobów/bonusów w tle (Celery).

Shop / Economy (sklep i waluty)
- Targowisko, zbrojownia; filtrowanie itemów wg typu/rarity.
- Transakcje atomiczne; integracja z zasobami użytkownika (coins, wood, stone, iron).

Quests
- Dzienne, tygodniowe: zwyczajne/ rzadkie/ legendarne.
- Filtracja wg rodzaju i czasu; reset cykliczny (Celery).

Challenges
- Własne i sugerowane; integracja z zadaniami i rankingami.

Support
- Pomoc/FAQ i kontakt (SMTP/Celery), proste endpointy statyczne.

Core (dashboard, zasoby, standardy API)
- Dashboard: GET /api/core/dashboard/ (waluty, zasoby, statystyki, liczba zadań, budynki, itemy).
- Model Resource per user (coins, wood, stone, iron) do użycia w shop/homestead/quests.
- Paginacja globalna, wersjonowanie API, dokumentacja (OpenAPI).

Media
- [x] Upload avatarów (limity rozmiaru i typów), opcjonalna weryfikacja formatu (Pillow).
- [ ] Plan na produkcję: django-storages (np. S3).

Security / Auth / Rate limiting
- [x] JWT globalnie wymagany; wyjątki publiczne: register/login/refresh.
- [x] Scoped throttling dla kluczowych endpointów auth.
- [x] Prywatność profilu (bez e‑maila w „profile”).

Konfiguracja środowisk / Deploy
- [x] Ustawienia z env: SECRET_KEY, DEBUG, ALLOWED_HOSTS, DB.
- [ ] Prod: DEBUG=False, ALLOWED_HOSTS ustawione, HSTS i secure cookies.
- [ ] (Opcjonalnie) CORS i CSRF_TRUSTED_ORIGINS dla frontu na innym originie.

Asynchroniczne zadania
- Celery + Redis: reset nawyków/questów, generowanie zasobów, bonusy z posiadłości.
- Harmonogram (celery beat) o stałych porach.

Testy / CI/CD
- pytest-django: testy auth (rejestracja/login/refresh/change-password), profil, unikalność e‑mail/username (różne wielkości liter), walidacja avatarów.
- docker-compose dla dev; CI do testów/lintu/deployu (GitHub Actions / GitLab CI).

Struktura (aktualna)

HT_RPG/
├─ manage.py
├─ .gitignore
├─ media/
│  └─ avatars/
│     └─ Obraz1.png
├─ habit_tracker_rpg/
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ users/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ signals.py
│  ├─ urls.py
│  └─ views.py
├─ tasks/
├─ inventory/
├─ estate/
├─ economy/
├─ quests/
├─ challenges/
└─ support/

Notatki do implementacji
- JSONField w posiadłości/questach ułatwia dodawanie nowych bonusów/nagród.
- ATOMIC_REQUESTS=True dla spójności transakcji.
- API-first: frontend (web/mobile) korzysta z endpointów DRF.
- Rozszerzalność: łatwo dodać PvP, gildie, marketplace.