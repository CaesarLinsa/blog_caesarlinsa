from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField


class ArticleForm(Form):
    title = StringField('标题', [DataRequired(), Length(max=100)])
    body = TextAreaField(label=u'正文', validators=[DataRequired()])


class CommentForm(Form):
    body = PageDownField(label="", validators=[DataRequired()])
    submit = SubmitField(u'提交')


class ReplyForm(Form):
    body = PageDownField(label=u'回复', validators=[DataRequired()])
    submit = SubmitField(u'发表')
