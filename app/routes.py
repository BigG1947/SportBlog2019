import json

from flask_login import login_required, login_user, current_user, logout_user

from app import app, db
from app.models import Photo, Article, Category, User, Comment
from flask import render_template, request, redirect, url_for


@app.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    title = "SportBlog - главная"
    popular = Article.query.filter_by(view=db.session.query(db.func.max(Article.view)).scalar()).limit(4).scalar()
    articles = Article.query.order_by(Article.dateAdd.desc(), Article.id.desc()).paginate(page, 10, False)
    nextUrl = url_for('index', page=articles.next_num) if articles.has_next else None
    prevUrl = url_for('index', page=articles.prev_num) if articles.has_prev else None
    total = articles.pages
    articles = articles.items
    return render_template("index.html", title=title, popular=popular, articles=articles, nextUrl=nextUrl,
                           prevUrl=prevUrl, total=total, page=page)


@app.route("/category")
@app.route("/category/<int:id>")
def category(id=1):
    page = request.args.get('page', 1, type=int)
    title = "SportBlog - Категория"
    popular = Article.query.filter_by(view=db.session.query(db.func.max(Article.view)).scalar()).limit(4).scalar()
    articles = Article.query.order_by(Article.dateAdd.desc(), Article.id.desc()).filter_by(idCategory=id).paginate(page,
                                                                                                                   10,
                                                                                                                   True)
    nextUrl = url_for('category', page=articles.next_num) if articles.has_next else None
    prevUrl = url_for('category', page=articles.prev_num) if articles.has_prev else None
    total = articles.pages
    articles = articles.items
    return render_template("category.html", title=title, popular=popular, articles=articles, nextUrl=nextUrl,
                           prevUrl=prevUrl, total=total, page=page)


@app.route("/article/<int:id>")
def article(id):
    title = "SportBlog - Статья"
    article = Article.query.get(id)
    popular = Article.query.filter_by(view=db.session.query(db.func.max(Article.view)).scalar()).limit(4).scalar()
    return render_template("single.html", title=title, popular=popular, article=article)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/admin")
    title = "Вход"
    if request.method == "POST":
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user is None or not user.checkPasswrod(password):
            return redirect("/login"), 302
        login_user(user)
        next = request.args.get('next', '/admin')
        return redirect(next, )
    return render_template("admin/login.html", title=title)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/'), 302


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    title = "Админ. панель"
    articles = Article.query.all()
    categories = Category.query.all()

    return render_template("admin/index.html", title=title, categories=categories)


@app.route("/addComment", methods=['POST'])
def addComment():
    article_id = request.form['article']
    name = request.form['name']
    email = request.form['email']
    text = request.form['text']

    comment = Comment()
    comment.id_article = article_id
    comment.email = email
    comment.name = name
    comment.text = text
    db.session.add(comment)
    db.session.commit()
    return redirect('/article/{}'.format(article_id))


@login_required
@app.route("/admin/addPost", methods=['GET', 'POST'])
def addPost():
    categories = Category.query.all()
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        text = request.form['text']
        idCategory = request.form['category']
        file = request.files['introImg']
        introImg = app.config['UPLOAD_FOLDER'] + file.filename
        file.save('app' + introImg)
        article = Article()
        article.title = title
        article.idCategory = idCategory
        article.text = text
        article.description = description
        article.introImg = introImg
        db.session.add(article)
        db.session.commit()
        return redirect("/", 302)
    return render_template('admin/post_form.html', post=None, categories=categories)


@login_required
@app.route("/admin/deletePost/<int:id>")
def deletePost(id):
    article = Article.query.get(id)
    db.session.delete(article)
    db.session.commit()
    return redirect("/", 302)


@login_required
@app.route("/admin/editPost/<int:id>", methods=['GET', 'POST'])
def editPost(id):
    categories = Category.query.all()
    article = Article.query.get(id)
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        text = request.form['text']
        idCategory = request.form['category']
        if request.files and request.files['introImg']:
            file = request.files['introImg']
            introImg = app.config['UPLOAD_FOLDER'] + file.filename
            file.save('app' + introImg)
        else:
            introImg = article.introImg
        article.title = title
        article.idCategory = idCategory
        article.text = text
        article.description = description
        article.introImg = introImg
        db.session.commit()
        return redirect("/", 302)
    return render_template('admin/post_form.html', post=article, categories=categories)


@login_required
@app.route("/admin/upload", methods=["POST"])
def upload():
    file = request.files['upload']
    photo = Photo()
    path = app.config["UPLOAD_FOLDER"] + file.filename
    photo.src = path
    file.save("app/" + path)
    db.session.add(photo)
    db.session.commit()
    result = {"upload": True, "url": path, "error": False}
    return json.dumps(result)


@app.errorhandler(404)
def pageNotFound(e):
    popular = Article.query.filter_by(view=db.session.query(db.func.max(Article.view)).scalar()).limit(4).scalar()
    return render_template("404.html", popular=popular), 404
