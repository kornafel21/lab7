from flask_bcrypt import generate_password_hash
from marshmallow import validate, Schema, fields


class UserCreate(Schema):
    username = fields.String()
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String(validate=validate.Email())
    phone = fields.String()


class UserInfo(Schema):
    id = fields.Integer()
    username = fields.Email()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String()
    phone = fields.String()
    user_status = fields.Integer()


class UserChangeStatus(Schema):
    user_status = fields.Integer()


class UserUpdate(Schema):
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email(validate=validate.Email())
    phone = fields.String()


class ArticleCreate(Schema):
    name = fields.String()
    text = fields.String()


class ArticleUpdate(Schema):
    name = fields.String()
    text = fields.String()


class ArticleInfo(Schema):
    id = fields.Integer()
    name = fields.String()
    text = fields.String()
    version = fields.Integer()
    creator_id = fields.String()


class ChangeCreate(Schema):
    article_id = fields.Integer()
    new_text = fields.String()


class ChangeInfo(Schema):
    id = fields.Integer()
    article_id = fields.Integer()
    article_version = fields.Integer()
    old_text = fields.String()
    new_text = fields.String()
    status = fields.String()
    proposer_id = fields.Integer()


class ReviewCreate(Schema):
    change_id = fields.Integer()
    verdict = fields.Boolean()
    comment = fields.String()


class ReviewUpdate(Schema):
    verdict = fields.Boolean()
    comment = fields.String()


class ReviewInfo(Schema):
    id = fields.Integer()
    change_id = fields.Integer()
    verdict = fields.Boolean()
    comment = fields.String()
    reviewer_id = fields.Integer()
