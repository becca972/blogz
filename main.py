from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzy@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(260))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, owner, title, body):
        self.owner = owner
        self.title = title
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(25))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

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


@app.route('/newpost', methods=['GET'])
def form():
    return render_template('newpost.html',title="Add a Blog Entry")
    
def empty(value):
    if value == "":
        return True

@app.route('/newpost', methods=['POST'])
def newpost():

    blog_title = request.form['title']
    blog_body = request.form['body']
    
    title_error = ''
    body_error = ''

    if empty(blog_title):
        title_error = 'Title cannot be empty.'

    if empty(blog_body):
        body_error = 'Body cannot be empty.'

    if not title_error and not body_error:
        new_entry = Blog(blog_title, blog_body)
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