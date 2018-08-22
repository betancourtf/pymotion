# pymotion
Sample Django REST API that consumes Microsoft's Face API to get emotions from user's uploaded images.

## End points
The API has three end points

* /mood/
The post method is used to send the user data (latitude, longitude and image in base 64) as a json object. This will create an entry in the database
The get method will list the users captured moods of the last 30 days
* /histogram/
The get method will return a json object with a histogram of moods for the last 30 days
* /happyplaces/
The get method uses query parameters (latitude, longitude, lat_offset, lon_offset) to return a list of happy places and it's distances. The happy places are searched within the rectangle created by latitude ± lat_offset and longitude ± lon_offset

## How to run
To run the project clone the repository and install the requirements (use of a virtual env is suggested). You must use python 3 for your virtual env. Project was tested in python 3.5 and 3.6.

```
mkvirtualenv pymotion
workon pymotion
git clone https://github.com/francisco-betancourt/pymotion.git
cd pymotion
pip3 install -r requirements.py
```

Once you have cloned and installed the requirements you must set 3 shell environment variables:

* DJANGO_MEDIA_ROOT='/Users/your-user/path-to-cloned-project/pymotion/uploads/'
* DJANGO_SECRET_KEY='replace-for-some-secret-key'
* EMOTIONS_API_KEY='your-face-api-key-from-azure'

To get the required key for the Face API go to this page:
https://azure.microsoft.com/en-us/try/cognitive-services/
And click on the Get Key button. Complete the procedure (it's free though you might need to add a credit card to validate your user). Replace the key you get for the EMOTIONS_API_KEY above.

For bash the file should look like this:
```
export DJANGO_MEDIA_ROOT='/Users/fbetancourt/python-projects/pymotion/uploads/'
export DJANGO_SECRET_KEY='**************************************************'
export EMOTIONS_API_KEY='********************************'
```

Remeber to source the file before running the project or you can manually set the variables each time you want to run the project if you prefer.

Once this variables are setup you need to create the database. For dev purposes the settings will use sqlite as the database. In production we suggest running a full-fledged DBMS like PostgreSQL. To create the db and table structure you have to run the following commands:

```
python manage.py makemigrations api
python manage.py migrate
```

To create your first user and test user you can run

```
python manage.py createsuperuser
python manage.py shell
```

Once you're in the app shell use the following commands to create a Token for your user

```
from django.contrib.auth.models import User
u = User.objects.get(email="email.used.above@domainusedabove.com")
from rest_framework.authtoken.models import Token
Token.objects.create(user=u)
```

Finally to start the development server you can simply do:
```
python manage.py runserver
```

## Test cases
The folder ```test``` of the project includes an export of several test cases for the project. The format is compatible with postman or RESTer (a Firefox and Chrome add-on that allow you to test APIs). In RESTer click on Organize and then on the Import Requests button and select the file to setup the test cases. You will need to update the Authorization header with the Token created for you user above. Once that is done you can send the request to test the project. You can replace the images in the sample mood requests for any image in base64. To turn an image into base64 you can use a web app like this https://www.base64-image.de/. It will even allow you to upload multiple images and give you it's base64 representation. 

If you send an image with no face or the service doesn't detect a face the row in the db will not have the is_recognized boolean set to True and will be ignored. Because of time constraints error handling has been not throughly tested. 
