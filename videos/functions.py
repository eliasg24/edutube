# Django
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile

# Models
from users.models import User, Profile
from videos.models import Video

# Utils
import requests
import random as rm
from bs4 import BeautifulSoup
from pytube import YouTube
import sqlite3
import os

def is_valid_image(file):
    if not isinstance(file, UploadedFile):
        return False
    if file.size > 5 * 1024 * 1024:
        return False

    # Obtener la extensión del archivo
    _, ext = os.path.splitext(file.name)
    ext = ext.lower()

    # Verificar si la extensión corresponde a PNG, JPG o JPEG
    if ext not in [".png", ".jpg", ".jpeg"]:
        return False

    # Verificar si el archivo es una imagen leyendo los primeros bytes
    header = file.read(11)
    file.seek(0)

    image_formats = [b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A",  # PNG
                     b"\xFF\xD8\xFF",  # JPEG/JPG
                     b"\xFF\xD9"]  # JPEG/JPG

    for format in image_formats:
        if header.startswith(format):
            return True

    return False


def extract_youtube_id(url):
    import re
    # Define a regex pattern to match the video ID
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None


data=list()

def get_video_info(video_url, channel, grade, type_value):
    # Obtener el HTML de la página del video

    try:
        profile = Profile.objects.get(user__username=channel)
    except:
        user = User.objects.create(username=channel)
        profile = Profile.objects.create(user=user)

    response = requests.get(video_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Usar pytube para obtener información adicional del video
    yt = YouTube(video_url)
    
    # Obtener el título del video
    title = yt.title
    
    # Obtener la descripción del video
    description = yt.description
    
    # Obtener el número de vistas
    views = yt.views
    rating= rm.uniform(3.5, 5.0)
    rating=round(rating,1)
    # Obtener el número de likes y dislikes
    likes = yt.rating
    # No se puede obtener el número de dislikes directamente con pytube o BeautifulSoup debido a cambios en la API de YouTube
    link_acortadoa=""
    xx=0
    # Obtener la fecha de publicación
    publish_date = yt.publish_date
    for i in video_url:
        if xx==1:
            link_acortadoa+=i
        if i == "=":
            xx=1
    dislikes=0
    indiferente=1
    indiferente2=1
    modified="2024-05-26 02:25:50"
    # Mostrar la información obtenida
    print(f"URL: {link_acortadoa}")
    print(f"Título: {title}")
    print(f"Descripción: {description}")
    print(f"Vistas: {views}")
    print(f"Likes: {likes}")
    print(f"Dislike:{dislikes}")
    print(f"El rating: {rating}")
    print(f"INdiferente: {indiferente}")
    print(f"Fecha de lanzamiento: {str(publish_date)[0:10]}")
    print(f"indifernete2: {indiferente2}")
    print(f"Modified:{modified}")

    video = Video.objects.create(
        uu_id=extract_youtube_id(video_url),
        title=title,
        profile=profile,
        views=views,
        rating=rating,
        created=publish_date,
        modified=publish_date,
        sector="Educación Libre",
        type=type_value,
        grade=grade,
    )
    data2=tuple([(i) for i in (link_acortadoa,title,description,views,likes,dislikes,rating,indiferente,str(publish_date)[0:10], indiferente2, modified)])
    return data2