# Project Structure 
_This guide will help us understand our project structure so that we can stay organized in our project._ I'll highlight the purpose of each directory and file so everyone understands Flasks structure. Keep in mind, I'm a beginner to Flask so some things may be poorly explained. In case you guys are interested, I used [this website](https://www.digitalocean.com/community/tutorials/how-to-structure-a-large-flask-application-with-flask-blueprints-and-flask-sqlalchemy) to make this guide.
## directory 1: app
This directory will store all of our front-end, back-end, and database code. Every directory in app should be a _component_ (I'll explain this later) of our website (with a few exceptions). A component corresponds to an endpoint in our website. For example, **/app/signup** is where our sign-up page will be, making **/app/signup** a component. Flask calls these blueprints, so I'll refer to it as that. 
When you want to make a new blueprint, the first step will be to create a new directory **/app/[blueprint_name].**
### coding a blueprint
Every blueprint will have at-least two files within it: ```__init__.py``` and ```routes.py```. ```__init__.py``` is a special python file that basically allows you to treat the directory it's in as a module. The most important thing is that within ```__init__.py``` we have this code:
```
from flask import Blueprint

bp = Blueprint('[our_blueprint_name]', __name__)

from app.[our_blueprint_name] import routes
```
this is where we'll create an instance of the Flask Blueprint object. Also, we will import our ```routes.py``` file.
In __init__.py file, we'll import Blueprint from Flask and make an instance of the object. We'll pass two parameters: the name of our component, and __name__, which is used behind the scenes by Python (i'll do more research on this to provide a better context). Then, we'll import the routes file from the same component directory.
The routes file in our blueprint directory is how we'll register all of our end points associated with our blueprint.
```
from flask import render_template
from app.[our_blueprint_name] import bp

@bp.route('/')
def index():
    return render_template('[our_blueprint_name]/index.html')

@bp.route('/[new_end_point_name]/')
def [handle_end_point_func]():
    return render_template('[our_blueprint_name]/[endpoint_page].html')
```
in ```routes.py``` we will have import our blueprint, and use flask function decorators to route any request for the endpoint to our function(s). We can add as many endpoints to our blueprint by using the code above. 
Apartment from these two files, we can add any back-end files within this folder to run within our end-point functions. 

## directory 2: templates
You may have noticed the render_template functions within ```routes.py```. Typically, for every endpoint we'll want to render a page. These pages go within the templates directory. Templates is one of those directories that are exceptions I mentioned above that _isn't_ a blueprint. Templates will hold all of our front-end code. Everytime you make a blueprint that needs a page, go into templates and create the same directory. Except, instead of having the files
```__init__.py``` and ```routes.py```, it'll hold ```index.html``` and any other HTML pages needed for our routes. **NOTE** ```index.html``` is the "home" folder of our blueprint.

## directory 3: static
Static is another one of those directories that are exceptions I mentioned above that _isn't_ a blueprint. It should hold all of our static files, like images.

## directory 4: models
Static is another one of those directories that are exceptions I mentioned above that _isn't_ a blueprint. It should hold all of our database logic. 

## file 1: config
This file will contain all our Flask configurations. For example, I put Flask in development mode by adding the ```FLASK_ENV = 'development'``` variable in the class Config. Although, for some reason this shit isn't working. I made it a note for one of us to fix it on Trello. 

## file 2: __init__.py
This file is pretty important because this is our root Flask app. In here, we'll have to make sure to register our blueprints, add our configurations, and maybe initializing our database as well.

# That's pretty much it boys. Hopefully this is clear to understand. Feel more then free to add / revise anything in this guide. 

