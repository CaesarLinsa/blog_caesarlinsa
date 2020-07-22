import os
from datetime import datetime

from flask import Response
from flask import render_template, request, redirect, url_for
from flask import Blueprint, jsonify
from ..models import Article, Comment, Reply, User, Permission
from .forms import ArticleForm, CommentForm
from flask_login import login_required, current_user
from .. import db
from ..utils.decorators import permission_required
from flask import current_app

main = Blueprint('main', __name__)


@main.route("/")
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get("ARTICLE_PER_PAGE", 10)
    pagination = Article.query.filter_by(auther_id=current_user.id).\
        order_by(Article.created.desc()).paginate(page, per_page=per_page)
    articles = pagination.items
    return render_template("index.html", pagination=pagination, articles=articles)


@main.route("/upload", methods=["POST"])
def upload():
    file = request.files.get('editormd-image-file')
    if not file:
        res = {
            'success': 0,
            'message': '上传失败'
        }
    else:
        ex = os.path.splitext(file.filename)[1]
        filename = os.path.join(current_app.root_path, 'static', 'img', datetime.now().strftime('%Y%m%d%H%M%S') + ex)
        print(filename)
        file.save(filename)
        res = {
            'success': 1,
            'message': '上传成功',
            'url': url_for('.image', name=filename)
        }
    return jsonify(res)


@main.route('/image/<name>')
def image(name):
    with open(name, 'rb') as f:
        resp = Response(f.read(), mimetype="image/jpeg")
    return resp


@main.route('/article/list', methods=['GET'])
@login_required
def article_list():
    return render_template("article/article_list.html")


@main.route('/article/data', methods=['GET'])
@login_required
def article_data():
    res = []
    articles = Article.query.options(db.joinedload("user")).filter_by(auther_id=current_user.id).all()
    for article in articles:
        res.append(
            {
                "id": article.id,
                "title": "<a href='%s' style='cursor:pointer'>%s</a>"
                         % (article.id, article.title),
                "auther": article.user.name,
                'edit': "<a href='edit/%s' style='cursor:pointer' >编辑<a>" % article.id
            }
        )

    return jsonify(res)


@main.route('/article/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.COMMENT)
def comments(id):
    article = Article.query.get_or_404(id)
    form = CommentForm(request.form)

    # 保存评论
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, article_id=id, auther_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for(".comments", id=id))
    article.hit_numers += 1
    return render_template("article/details.html",
                           title=article.title,
                           form=form,
                           article=article)


@main.route('/article/edit', methods=['GET', 'POST'])
@main.route('/article/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id=0):
    """
    :param id: 文章id
    :return: post提交，当id为0时，编辑发布新文章，否则编辑旧博客，发布后更新数据库，
    跳转到.comments将博客和评论一并呈现
             get请求时，将文章输入到编辑框中
    """
    form = ArticleForm(request.form)
    # post提交
    if form.validate_on_submit():
        if id == 0:
            article = Article(user=current_user)
        else:
            article = Article.query.get_or_404(id)
        article.body = form.body.data
        article.title = form.title.data

        db.session.add(article)
        db.session.commit()
        # url_for调用处理函数函数名
        return redirect(url_for('.comments', id=article.id))
    # get 编辑时
    title = u'添加文章'
    if id > 0:
        article = Article.query.get_or_404(id)
        form.body.data = article.body
        form.title.data = article.title
        title = u'编辑 %s' % article.title

    return render_template('article/edit.html',
                           title=title,
                           form=form)


@main.route('/article/delete/<int:id>', methods=['DELETE'])
@permission_required(Permission.WRITE)
def delete_article(id):
    article = Article.query.get(id)
    db.session.delete(article)
    db.session.commit()
    res = {
        'success': 0,
        'message': '删除成功',
    }
    return jsonify(res)


@main.route('/reply/<int:article_id>/<int:comment_id>', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def reply(article_id, comment_id):
    reply = Reply(comment_id=comment_id, auther_id=current_user.id)
    reply.body = request.form.get("values")
    db.session.add(reply)
    db.session.commit()
    ret = {
        "data": reply.body
    }
    return jsonify(ret)


@main.route('/about')
def about():
    return render_template('about.html', title=u'关于')
