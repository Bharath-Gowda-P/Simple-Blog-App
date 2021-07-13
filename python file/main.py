from enum import unique
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect
from flask_login import LoginManager, UserMixin, login_manager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)


app.config['SECRET_KEY'] = "nothingggg"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    author = db.Column(db.String(25), nullable=False, default="N.A")
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return 'BLOGPOST' + str(self.id)


class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def get_id(self):
        return (self.user_id)

    def __repr__(self):
        return 'USER' + str(self.id)


@app.route('/')
def welcome():
    return render_template('welcome_page.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        ueamil = request.form['mail']
        uname = request.form['username']
        upass = request.form['password']
        hpass = generate_password_hash(upass, method='sha256')
        new_user = User(username=uname, email=ueamil, password=hpass)
        db.session.add(new_user)
        db.session.commit()
        flash("Account Created. Please Login.")
        return redirect('/')
    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        pw = request.form['password']
        user = User.query.filter_by(username=name).first()
        if user:
            if check_password_hash(user.password, pw):
                login_user(user)
                return redirect('/home')
            else:
                flash("INVALID PASSWORD")
                return render_template('login.html')
        else:
            flash("INVALID USERNAME")
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    all_posts = BlogPost.query.all()
    return render_template('home.html', posts=all_posts)


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        post_title = request.form['title']
        post_author = request.form['author']
        post_content = request.form['content']
        new_post = BlogPost(
            title=post_title, author=post_author, content=post_content)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/home')
    else:
        return render_template('add.html')


@app.route('/home/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/home')


@app.route('/home/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    post = BlogPost.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/home')
    else:
        return render_template('edit.html', post=post)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
