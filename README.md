System
You are a senior backend engineer expert in Python, Django, and Docker. Generate a complete, production‑ready, containerized Django project with Nginx, following best practices. Provide only the file and directory structure and code; do not write explanatory text.
User Requirements
1. **Framework & Environment**
   * Python 3.10
   * Django 4.x
   * Django REST Framework
   * drf‑spectacular (or drf‑yasg) for Swagger/OpenAPI docs
   * PyPDF2 for PDF manipulation
   * Gunicorn as the WSGI server
   * Docker multi‑stage build for production image
   * Nginx as a reverse proxy for static/media and API paths
2. **Endpoints**
   * **POST** `/api/create_embedded_pdf/`
      * Accepts a JSON body with two Base64‑encoded byte fields:
         * `host_pdf`: the PDF to embed into
         * `attachments`: a list of PDFs to embed
      * Uses in‑memory `BytesIO` to read `host_pdf`, loops over `attachments`, and embeds each via `PdfWriter.add_attachment()`
      * Returns the modified PDF as raw binary (`application/pdf`) with proper headers
   * **POST** `/api/extract_embedded_pdf/`
      * Accepts raw PDF bytes (`application/pdf` request)
      * Uses `BytesIO` and `PdfReader` to load the PDF, extracts all embedded attachments, and returns either:
         * A multipart/mixed response with each PDF attachment
         * Or a single ZIP archive containing all extracted PDFs
3. **Swagger Documentation**
   * Serve Swagger UI at `/swagger/` using drf‑spectacular or drf‑yasg
   * Generate an accurate OpenAPI 3 schema reflecting binary payloads
4. **Containerization**
   * **Dockerfile** (multi‑stage build):
      1. **Builder stage**
         * Install Python dependencies
         * Copy project source
      2. **Runner stage**
         * Use a minimal base image
         * Copy only the installed packages and project code
         * `CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]`
   * **docker-compose.yml**
      * Services: `web` (Django/Gunicorn), `nginx`
      * Volume mounts for `static/`, `media/`, and code
      * Network config so Nginx proxies `/api/` and `/swagger/` to `web:8000`
   * **nginx.conf**
      * Define `upstream web { server web:8000; }`
      * Serve `/static/` and `/media/` from local volumes
      * Proxy `/api/` and `/swagger/` to the Gunicorn backend
5. **Project Structure**

```bash
project/
├── app/
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── pdf_utils.py
├── project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── requirements.txt
└── manage.py
```

```sh
#!/bin/bash

# Create the project structure
django-admin startproject api_project
cd api_project
python manage.py startapp app

# Create the directory structure
mkdir -p nginx

# Create empty files
touch app/views.py
touch app/serializers.py
touch app/urls.py
touch app/pdf_utils.py
touch api_project/settings.py
touch api_project/urls.py
touch api_project/wsgi.py
touch Dockerfile
touch docker-compose.yml
touch nginx/nginx.conf
touch requirements.txt

echo "Api_project structure created successfully!"
```