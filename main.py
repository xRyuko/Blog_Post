from cProfile import label

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from dotenv import load_dotenv
load_dotenv()
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(app)
ckeditor = CKEditor(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

class AddForm(FlaskForm):
    title = StringField(label="Blog Post Title", validators=[DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[DataRequired()])
    author = StringField(label="Your Name", validators=[DataRequired()])
    image_url = StringField(label="Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField(label="Blog Content", validators=[DataRequired()])
    submit = SubmitField(label="SUBMIT POST")

@app.route('/')
def get_all_posts():
    # Query the database for all the posts. Convert the data to a python list.
    posts = []
    with app.app_context():
        results = db.session.execute(db.select(BlogPost))
        posts = results.scalars().all()
    return render_template("index.html", all_posts=posts)

# Add a route for individual posts.
@app.route('/post/<int:post_id>')
def show_post(post_id):
    # Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


# Create a new blog post
@app.route('/new_post', methods=['GET', 'POST'])
def add_post():
    form = AddForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=date.today().strftime('%B %d, %Y'),
            body=form.body.data,
            author=form.author.data,
            img_url=form.image_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form)

# Change an existing blog post
@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    edit_form = AddForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        body=requested_post.body,
        author=requested_post.author,
        img_url=requested_post.img_url
    )
    if edit_form.validate_on_submit():
        requested_post.title=edit_form.title.data
        requested_post.subtitle=edit_form.subtitle.data
        requested_post.body=edit_form.body.data
        requested_post.author=edit_form.author.data
        requested_post.img_url=edit_form.image_url.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=requested_post.id))
    return render_template('make-post.html', post=requested_post, form=edit_form)

# To remove a blog post from the database
@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=False, port=5003)
