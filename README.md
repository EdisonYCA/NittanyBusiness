# Project Structure 
_This guide will highlight how we will develop our application using the file structure displayed in the [main] branch._
## app directory
This directory will store most of our logic for the front-end, back-end, and database. Every directory in app should be a component of our website (with a few exceptions that I'll highlight). For example, **/app/main** is where our landing page will be. **/app/signup** is where our sign-up page will be. Note, that we may have also more a complicated structure where we nest components (i.e. **/app/dashboard/buy**). 
  ### components 
  These "components" are called blueprints in Flask. When we make a component in *app*, Flask doesn't automatically recognize it. This means that you can't just make a component, refresh your page, and go to the URL. Instead, we'll first need to tell Flask our directory is a blueprint. We do this in a file called __init__.py. This is a special file name that all of our component directories should have. Here, we'll create a blueprint using the following code. 
```
from flask import Blueprint

bp = Blueprint('posts', __name__)

from app.posts import routes
```
In __init__.py file, we'll import Blueprint from Flask and make an instance of the object. We'll pass two parameters: the name of our component, and __name__, which is used behind the scenes by Python (i'll do more research on this to provide a better context). Then, we'll import the routes file from the same component directory.
### routes
The routes folder is how we'll register all of our end points with Flask. 
```
from flask import render_template
from app.posts import bp

@bp.route('/')
def index():
    return render_template('posts/index.html')

@bp.route('/categories/')
def categories():
    return render_template('posts/categories.html')
```   

For example, this is within the posts component. Here, we'll import our blueprint and the render_template method from Flask. Utilizing the ```bp.route('url')``` decorator, we can create functions to be run when the endpoint ```url``` is reached. What we'll be telling Flask here is: "when the **app/posts/** endpoint is reached, render the HTML template in **posts/index.html**." 

## templates
The templates directory is one of the "special" directories that will go in **/app**. This directory will hold all of the html/css for our components. Each component will have another directory in the templates. For example, we may have something like **/app/buyers/** which holds all the HTML pages that will be used for the buyers component. The only exception is the main component. Which has its HTML page (index.html) without a subdirectory. **NOTE** by convention, every component in templates has an index.html. This is just the main page for that file.  
