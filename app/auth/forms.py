from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email


class LoginForm(FlaskForm):
    username = StringField(label=u'用户名', validators=[DataRequired(message="数据不能为空")])
    password = PasswordField(label=u'密码', validators=[DataRequired(message="数据不能为空")])
    submit = SubmitField(u'提交')


class RegisterForm(FlaskForm):
    username = StringField(label=u'用户名',
                           validators=[DataRequired(message="数据不能为空"),
                                       Length(5, 64),
                                       Regexp("^[A-Za-z][A-Za-z0-9_.]*$",
                                              message="以字母开头，数字字母下划线.组成")
                                       ])
    password = PasswordField(label=u'密码', validators=[DataRequired(message="数据不能为空")])
    re_password = PasswordField(label=u'密码确认',
                                validators=[DataRequired(message="数据不能为空"),
                                            EqualTo('password', message=u'密码必须一致')
                                            ])
    email = StringField(label=u'邮箱', validators=[Email(message="不符合邮箱格式")])
    submit = SubmitField(u'注册')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(label=u'原密码', validators=[DataRequired()])
    password = PasswordField(label=u'密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码输入不一致')])
    password2 = PasswordField(label=u'再次输入',
                              validators=[DataRequired()])
    submit = SubmitField(u'提交')


class PasswordResetRequestForm(FlaskForm):
    email = StringField(label=u'邮箱', validators=[DataRequired(), Length(1, 64),
                                                   Email()])
    submit = SubmitField(u'密码重置')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('再次输入密码', validators=[DataRequired()])
    submit = SubmitField('提交')
