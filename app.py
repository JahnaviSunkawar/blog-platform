from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "blogsecretkey"

# ---------------- DATABASE ----------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), nullable=False)

    password = db.Column(db.String(100), nullable=False)


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    content = db.Column(db.Text, nullable=False)

    username = db.Column(db.String(100))


class Comment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.Text, nullable=False)

    username = db.Column(db.String(100))

    post_id = db.Column(db.Integer)

# ---------------- HOME ----------------

@app.route('/')
def home():

    posts = Post.query.all()

    username = session.get('username')

    return render_template(
        'index.html',
        posts=posts,
        username=username
    )

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        email = request.form['email']

        password = request.form['password']

        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:

            session['username'] = user.username

            return redirect('/')

        else:

            return "Invalid Email or Password"

    return render_template('login.html')

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.pop('username', None)

    return redirect('/login')

# ---------------- CREATE POST ----------------

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():

    if 'username' not in session:

        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']

        content = request.form['content']

        new_post = Post(
            title=title,
            content=content,
            username=session['username']
        )

        db.session.add(new_post)

        db.session.commit()

        return redirect('/')

    return render_template('create_post.html')

# ---------------- VIEW POST ----------------

@app.route('/post/<int:id>')
def post(id):

    post = Post.query.get_or_404(id)

    comments = Comment.query.filter_by(post_id=id).all()

    username = session.get('username')

    return render_template(
        'post.html',
        post=post,
        comments=comments,
        username=username
    )

# ---------------- ADD COMMENT ----------------

@app.route('/add-comment/<int:id>', methods=['POST'])
def add_comment(id):

    if 'username' not in session:

        return redirect('/login')

    text = request.form['text']

    comment = Comment(
        text=text,
        username=session['username'],
        post_id=id
    )

    db.session.add(comment)

    db.session.commit()

    return redirect(f'/post/{id}')

# ---------------- EDIT POST ----------------

@app.route('/edit-post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):

    post = Post.query.get_or_404(id)

    if request.method == 'POST':

        post.title = request.form['title']

        post.content = request.form['content']

        db.session.commit()

        return redirect('/')

    return render_template(
        'edit_post.html',
        post=post
    )

# ---------------- DELETE POST ----------------

@app.route('/delete-post/<int:id>')
def delete_post(id):

    post = Post.query.get_or_404(id)

    db.session.delete(post)

    db.session.commit()

    return redirect('/')

# ---------------- CREATE DATABASE ----------------

with app.app_context():

    db.create_all()

# ---------------- RUN APP ----------------

if __name__ == '__main__':

    app.run(debug=True)