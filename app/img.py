from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
import pymysql


# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class UploadForm(FlaskForm):
    user_id = StringField('编号', validators=[DataRequired()])
    file = FileField('上传头像', validators=[DataRequired()])
    submit = SubmitField('上传')