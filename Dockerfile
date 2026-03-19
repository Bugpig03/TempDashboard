# Image légère de Python
FROM python:3.11-slim

# Dossier de travail dans le container
WORKDIR /app

# Copier les fichiers de dépendances et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du projet (templates, static, app.py)
COPY . .

# Port utilisé par Flask
EXPOSE 5000

# Commande pour lancer l'app (on utilise Gunicorn pour la prod, ou python app.py)
CMD ["python", "app.py"]