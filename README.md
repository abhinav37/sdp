# SDP
Staff Development Program created as part of COMP3297 - Introduction to Software Engineering at HKU. 

Web Application written in Django, HTML, JavaScript and JQuery. 

Install pip if it is not installed. Run ```pip install django-embed-video```
to install ```djanggo-embed-video``` dependency for SDP. If this does not work, please follow the steps mentioned [here](http://django-embed-video.readthedocs.io/en/v1.1.0/installation.html to intall django-embed-video). 

### Important Notes 
  - If the file uploading and rendering does not work, please update the ```MEDIA_ROOT``` in ```sdp\sdp\settings.py``` to the absolute path of the uploads folder.
  - The CSS of the project may not load, and to fix the same, try putting in the absolute path to the static folder in ```STATICFILES_DIRS``` in ```sdp\sdp\settings.py```.


Run ```python manage.py runserver``` in the folder containing manage.py. The application is accessible on ```localhost:8000/main/```
