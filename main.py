from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzy@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'sabrshukr'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(260))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


#VALIDATION

def improper_length(value):
    if len(value) < 3:
        return True

def empty(value):
    if value == "":
        return True


#LOGIN

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

#SIGNUP

@app.route('/signup', methods=['POST', 'GET'])
def signup():
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''
    
        if improper_length(username):
            username_error = "Username should be at least 3 characters."

        if improper_length(password):
            password_error = "Password should be at least 3 characters."
    
        if password != verify:
            verify_error = "Passwords must match."

        if empty(username):
            username_error = "Username cannot be left blank."

        if empty(password):
            password_error = "Password cannot be left blank."

        if empty(verify):
            verify_error = "Verify password cannot be left blank."

        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("You are logged in as {{username}}.")
                return redirect('/blog')
            else:
                flash("That username is already in use. Please choose another username.")
                return render_template('signup.html')

        else:
            return render_template('signup.html',
                username_error = username_error,
                password_error = password_error,
                verify_error = verify_error,
                username = username)

    else:
        return render_template('signup.html')

#VIEW BLOG

@app.route('/blog', methods=['GET'])
def index():

    id = request.args.get('id')
    entries = Blog.query.all()

    if not id:
            
        return render_template('blog.html',title="Build a Blog", 
            entries=entries)

    else:
        entry = Blog.query.filter_by(id=id).first()
        print(entry)
        return render_template('entry.html',title="Build a Blog",
            entry=entry)

#NEW POST

@app.route('/newpost', methods=['GET'])
def form():
    return render_template('newpost.html',title="Add a Blog Entry")


@app.route('/newpost', methods=['POST'])
def newpost():

    blog_title = request.form['title']
    blog_body = request.form['body']
    owner = User.query.filter_by(username=session['username']).first()
    
    title_error = ''
    body_error = ''

    if empty(blog_title):
        title_error = 'Title cannot be empty.'

    if empty(blog_body):
        body_error = 'Body cannot be empty.'

    if not title_error and not body_error:
        new_entry = Blog(blog_title, blog_body, owner)
        db.session.add(new_entry)
        db.session.commit()
        id = new_entry.id
        redir = 'blog?id=' + str(id)
        return redirect(redir)
    else:
        return render_template('newpost.html', blog_title=blog_title, title_error=title_error, 
            blog_body=blog_body, body_error=body_error)
        

# @app.route('/delete-task', methods=['POST'])
# def delete_task():

#     task_id = int(request.form['task-id'])
#     task = Blog.query.get(task_id)
#     task.completed = True
#     db.session.add(task)
#     db.session.commit()

#     return redirect('/')


if __name__ == '__main__':
    app.run()