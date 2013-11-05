# Vosae backend application

> This is the [Vosae](https://www.vosae.com/) backend app.  
> It exposes Vosae resources though an API. A graphic web-interface is available on Github repo [naeka/vosae-web](https://github.com/Naeka/vosae-web/).

---

| Branch | Travis-CI build status |
| :--- | --- |
| master (ready for production) | [![Build Status](https://travis-ci.org/Naeka/vosae-app.png?branch=master)](https://travis-ci.org/Naeka/vosae-app) |
| develop | [![Build Status](https://travis-ci.org/Naeka/vosae-app.png?branch=develop)](https://travis-ci.org/Naeka/vosae-app) |

---

The Vosae backend application is powered by our favorite language, **Python**, and relies on these amazing technologies:

 - **Python**
 - **Django**
 - **MongoDB**
 - **Elasticsearch**
 - Celery
 - Redis
 - sqlite (or Mysql)
 - Websockets (through Pusher)
 - Memcached


## Install the application


You need to meet these requirements before installing the Vosae backend application:
 
 - MongoDB ([official documentation](http://docs.mongodb.org/manual/installation/))
 - Elasticsearch ([official documentation](http://www.elasticsearch.org/guide/))
 - Redis ([official documentation](http://redis.io/download))
 - Memcached ([official documentation](https://code.google.com/p/memcached/wiki/NewStart))
 - libevent (or libevent-dev) ([official documentation](http://libevent.org/))


#### First, clone the repository:

```bash
$ git clone git@github.com:Naeka/vosae-app.git
$ cd vosae-app/
```

#### Build the virtualenv

*Using [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/) - recommanded:*

```bash
$ mkvirtualenv vosae-app
```

*Or simply with the [virtualenv tool](http://www.virtualenv.org/):*

    $ virtualenv --python=python2.7 --distribute ./
    $ source bin/activate
    
    
#### Install Python requirements **in the virtualenv**:

```bash
(vosae-app)$ pip install -r requirements.txt
```


#### Initialize the database and create a superuser

```bash
(vosae-app)$ ./manage.py syncdb --migrate
(vosae-app)$ ./manage.py createsuperuser
```

> This will be the user you should use to connect the first time.  
> It has access to Django admin (available on vosae-app, `/admin/`)


## Manage static files

The Vosae backend application handle static files with [Grunt](http://gruntjs.com/).
There isn't a lot of static files in this app, just a few to handle the authentication process.


You need to have Node.js and Node Package Manager (npm) on your system.
**If Node isn't on your system, [install it now](http://nodejs.org/download/)!**


#### First, install grunt dependencies on your system:

```bash
$ gem install compass
$ gem install sass
$ gem install sass-rails
$ gem install bootstrap-sass
```

#### Install Grunt:

```bash
$ npm install -g grunt-cli
```
    
#### Finally, on the root of vosae-app:

```bash
$ npm install
```
    
> if it doesn't work (on MacOS), add '/usr/local/share/npm/bin' to /etc/paths
    
    
##### Now you can generate static files
    
Build files for dev and watch directories for changes

```bash
$ grunt
```
    
**Only** build files for development

```bash
$ grunt build-dev
```


## Launch the app server

#### Settings

Prior to launch the server, a web endpoint (Ember.JS client) settings must be defined.
The `VOSAE_WEB_ENDPOINT` environment variable is used for this purpose.

For development, it can be more convenient to set this in a local settings file (not tracked by Git).  
In this case, create a `local.py` file in the `settings` module and fill with:


```python
# -*- coding:Utf-8 -*-

WEB_ENDPOINT = 'http://localhost:8001'
```


#### Launch the database

```bash
$ cd www/
$ mkdir databases
$ ./mongodb.sh start
```

#### Launch Redis if not automatically started by your system

```bash
$ redis-server
```

#### Launch elasticsearch

```bash
$ elasticsearch -f
```
    
#### Activate the virtualenv and launch the dev server

```bash
(vosae-app)$ ./manage.py runserver
```
    

#### Launch Celery (within the virtualenv)

```bash
(vosae-app)$ ./manage.py celeryd -v 2 -B -s celery -E -l INFO
```



## Feature branches naming 

Feature branches are branches used when developing a specific feature. It is used thanks to [gitflow](https://github.com/nvie/gitflow).

To install gitflow, follow [gitflow instructions](https://github.com/nvie/gitflow#installing-git-flow).


## Code conventions 

#### Django

*   **Use of SPACES for indentation** - 4-spaces equivalency
*   Class definitions and top methods separated by **2** blank lines, methods inside a class separated by **1** blank line
*   No maximum line length but try to be clear and align on multiple lines
*   Avoid parentheses use when possible for conditional and loop statements


#### Templates

*   **Use of SPACES for indentation** - 4-spaces equivalency
