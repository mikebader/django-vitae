.. _getting-started: 

Getting Started
===============

To get started with Django-Vitae, make sure that you have Python_ (version 3.5 or later) installed on your machine. 

.. _Python: http://www.python.org/ 

You might want to work in a `virtual environment`_. If you know what those are, go ahead and set one up; if not, then don't worry it (you may want to learn how to if you end up using Python a lot, but if this is your only project, it's not a big deal).   

.. _`virtual environment`: https://virtualenv.pypa.io/en/stable/

Now you will want to create a directory where you will store all of the files for your CV. Move inside that directory (the ``$`` represents the command line where you enter text, don't include it in what you type):: 

    $ mkdir my_cv
    $ cd my_cv

Once you are in that directory, you will install Django-Vitae. This will also install Django_ and a few other Python packages::

    $ pip install django-vitae

.. _Django: http://www.djangoproject.com

Once you have installed Django-Vitae and all of its dependencies, you will start a `Django project`_. This opens up all of Django's magic to help you create your CV. In the example below, your Django project would be called ``myvitae``, but you can choose any name you wish as long as the name does not conflict with built-in Python module names. After you make the project, you will move into the directory created for the project, which will have the same name as the project (``myvitae`` in this case)::

    $ django-admin.py startproject myvitae
    $ cd myvitae

.. _`Django project`: https://docs.djangoproject.com/en/2.0/intro/tutorial01/#creating-a-project 

Next comes the trickiest part. You will need to edit two different files. Both are in the ``myvitae`` subdirectory. This can be confusing: you will have two layers of directories, both named ``myvitae`` (or whatever you chose to call your project). The files we will be editing are in the directory lower in the hierarchy. 

The first file is called ``settings.py``. Open the file in a text editor of your choice and you will see something that looks like the following::

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]

At the end of that list, you will want to add two lines so that it looks like this (make sure you include the quotes):: 

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_widgets',
        'cv',
    ]

Save the ``settings.py`` file and close it. 

Now, open up the file ``urls.py``. Look for the following line::

    from django.urls import path

and change it to: ::

    from django.urls import path, include

Then, in the same file, you will find the part that looks like this::

    urlpatterns = [
        path('admin/', admin.site.urls),
    ]

and you will change it to look like this::

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('cv.urls', namespace='cv')),
    ]

Save the ``urls.py`` file and close it. The hard part is done!

Now, in your Terminal you will need to run a series of commands from the *top level* ``myvitae`` directory (the one directly under ``my_cv`` if you've used the same names as those used in this guide). These will set up your database (each will produce some text on the screen that you don't need to worry about)::

    $ ./manage.py makemigrations
    $ ./manage.py migrate

After those commands complete you will run another command that will set up a "superuser" that allows you administrative access to your project. Type::

    $ ./manage.py createsuperuser

You will be prompted to enter a username, an email, and a password. 

After you have set all of that up, you will now create a local version of your CV website. To do that, you enter the command::

    $ ./manage.py runserver

Now open your browser of choice go to http://localhost:8000/admin or http://127.0.0.1:8000/admin. You will see, if everything has gone correctly, a login screen asking for your username and password. These are the same as what you just entered to create your superuser. After you successfully log in, you will see an interface where you can edit all of the entries for you CV. After you so so, you can then point your browser to http://localhost:8000/ to see your CV (if you log out from the admin site, you will not see the add and edit buttons). 

And you, my friend, are on your way to making your own vitae!


