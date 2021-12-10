# Lecture Translator Webpage

## Prerequisites
- A Unix System
- Python 3.7 or above
- ffmpeg for audio conversion
- Java for Segmentation

## Local Development Setup
1. Clone the repository
3. Create and activate a virtual environment and install packages with `pip install -r requirements.txt`
4. Copy the file `LT_UI/setup_templates/localsettings_template.py` to `LT_UI/LT_UI/localsettings.py` next to `settings.py`
5. In `LT_UI/tasks/workers.py` enter dummy content in the variables and methods. Examples are given in the comments for each.
6. Navigate into `LT_UI/` where `manage.py` resides
7. Generate a new secret key using `python manage.py newsecretkey` and put it into your `localsettings.py`
8. Run `python manage.py makemigrations users`
9. Run `python manage.py makemigrations tasks`
10. Run `python manage.py migrate`
11. Start the local development server with `python manage.py runserver`
