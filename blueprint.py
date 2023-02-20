from flask import Blueprint
import sqlalchemy
from flask import Blueprint, request, jsonify
import marshmallow
from flask_bcrypt import check_password_hash

import db_utils
from schemas import *
from models import *

api_blueprint = Blueprint('api', __name__)
StudentID = 5

session = Session()

errors = Blueprint('errors', __name__)


@api_blueprint.route('/hello-world')
def hello_world_ex():
    return 'Hello World!'


@api_blueprint.route(f'/hello-world-{StudentID}')
def hello_world():
    return f'Hello World {StudentID}', 200


@errors.app_errorhandler(sqlalchemy.exc.NoResultFound)
def handle_error(error):
    response = {
        'error': {
            'code': 404,
            'type': 'NOT_FOUND',
            'message': 'No row was found for one()'
        }
    }

    return jsonify(response), 404


@errors.app_errorhandler(sqlalchemy.exc.IntegrityError)
def handle_error(error):
    response = {
        'error': {
            'code': 400,
            'type': 'BAD_REQUEST',
            'message': 'Not enough data'
        }
    }

    return jsonify(response), 400


@errors.app_errorhandler(marshmallow.exceptions.ValidationError)
def handle_error(error):
    response = {
        'error': {
            'code': 400,
            'type': 'Validation',
            'message': str(error.args[0])
        }
    }

    return jsonify(response), 400


@errors.app_errorhandler(KeyError)
def handle_error(error):
    response = {
        'error': {
            'code': 400,
            'type': 'BAD_REQUEST',
            'message': 'Not enough information'
        }
    }

    return jsonify(response), 400


@api_blueprint.route("/user", methods=["POST"])
def create_user():
    user_data = UserCreate().load(request.json)
    user = db_utils.create_entry(User, **user_data)
    return jsonify(UserInfo().dump(user))


@api_blueprint.route("/user/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        user = db_utils.get_entry_by_id(User, user_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404

    return jsonify(UserInfo().dump(user))


@api_blueprint.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = db_utils.get_entry_by_id(User, user_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404

    user_data = UserUpdate().load(request.json)
    user_updated = db_utils.update_entry(User, user_id, **user_data)
    return jsonify(UserInfo().dump(user_updated))


@api_blueprint.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = db_utils.get_entry_by_id(User, user_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404

    db_utils.delete_entry(User, user_id)
    logout_user()
    return jsonify({"code": 200, "message": "OK", "type": "OK"})


@api_blueprint.route("/user/changeStatus/<int:user_id>", methods=["PUT"])
def update_user_status(user_id):
    try:
        user = db_utils.get_entry_by_id(User, user_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404

    user_data = UserChangeStatus().load(request.json)

    if user_data['user_status'] not in (0, 1, 2):
        response = {
            'error': {
                'code': 400,
                'type': 'Validation',
                'message': 'Wrong user status. Must be 0, 1 or 2'
            }
        }

        return jsonify(response), 404

    admins = session.query(User).filter_by(user_status=0).all()
    if len(admins) < 2 and user_id == 1:  # and user_id equals logged in user_id
        response = {
            'error': {
                'code': 400,
                'type': 'Bad request',
                'message': 'You are the last admin'
            }
        }

        return jsonify(response), 404

    user_updated = db_utils.update_entry(User, user_id, **user_data)
    return jsonify(UserInfo().dump(user_updated))


@api_blueprint.route("/user/login", methods=["GET"])
def login_user():
    return jsonify(msg="Not implemented"), 200


@api_blueprint.route("/user/logout", methods=["POST"])
def logout_user():
    return jsonify(msg="Not implemented"), 200


@api_blueprint.route("/article", methods=["POST"])
def create_article():
    article_data = ArticleCreate().load(request.json)
    article_data['version'] = 0
    article_data['creator_id'] = 1  # Change to logged-in user id
    article = db_utils.create_entry(Article, **article_data)
    return jsonify(ArticleInfo().dump(article))


@api_blueprint.route("/article/<int:article_id>", methods=["GET"])
def get_article_by_id(article_id):
    try:
        article = db_utils.get_entry_by_id(Article, article_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Article not found'
            }
        }

        return jsonify(response), 404

    return jsonify(ArticleInfo().dump(article))


@api_blueprint.route("/article/<int:article_id>", methods=["PUT"])
def update_article(article_id):
    try:
        article = db_utils.get_entry_by_id(Article, article_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404

    article_data = ArticleUpdate().load(request.json)
    article_data['version'] = db_utils.get_entry_by_id(Article, article_id).version + 1
    article_updated = db_utils.update_entry(Article, article_id, **article_data)
    return jsonify(ArticleInfo().dump(article_updated))


@api_blueprint.route("/article/<int:article_id>", methods=["DELETE"])
def delete_article(article_id):
    try:
        article = db_utils.get_entry_by_id(Article, article_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Article not found'
            }
        }

        return jsonify(response), 404

    changes = session.query(Change).filter_by(article_id=article_id).all()
    for change in changes:
        review = session.query(Review).filter_by(change_id=change.id).one()
        db_utils.delete_entry(Review, review.id)
        db_utils.delete_entry(Change, change.id)

    db_utils.delete_entry(Article, article_id)
    return jsonify({"code": 200, "message": "OK", "type": "OK"})


@api_blueprint.route("/change", methods=["POST"])
def create_change():
    change_data = ChangeCreate().load(request.json)

    try:
        article = db_utils.get_entry_by_id(Article, change_data['article_id'])
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Article not found'
            }
        }

        return jsonify(response), 404

    change_data['article_version'] = article.version
    change_data['old_text'] = article.text
    change_data['status'] = 'in review'
    change_data['proposer_id'] = 1  # Change to logged-in user id

    change = db_utils.create_entry(Change, **change_data)
    return jsonify(ChangeInfo().dump(change))


@api_blueprint.route("/change/<int:change_id>", methods=["GET"])
def get_change_by_id(change_id):
    try:
        change = db_utils.get_entry_by_id(Change, change_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Change not found'
            }
        }

        return jsonify(response), 404

    return jsonify(ChangeInfo().dump(change))


@api_blueprint.route("/change/<int:change_id>", methods=["DELETE"])
def delete_change(change_id):
    try:
        change = db_utils.get_entry_by_id(Change, change_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Change not found'
            }
        }

        return jsonify(response), 404

    review = session.query(Review).filter_by(change_id=change.id).first()
    if review is not None:
        db_utils.delete_entry(Review, review.id)

    db_utils.delete_entry(Change, change.id)
    return jsonify({"code": 200, "message": "OK", "type": "OK"})


@api_blueprint.route("/mychanges", methods=["GET"])
def my_changes():
    user_id = 2  # change to logged-in user id

    changes = session.query(Change).filter_by(proposer_id=user_id).all()
    return jsonify(ChangeInfo().dump(changes, many=True))


@api_blueprint.route("/changesInReview", methods=["GET"])
def changes_in_review():
    changes = session.query(Change).filter_by(status='in review').all()
    return jsonify(ChangeInfo().dump(changes, many=True))


@api_blueprint.route("/review", methods=["POST"])
def create_review():
    review_data = ReviewCreate().load(request.json)

    try:
        change = db_utils.get_entry_by_id(Change, review_data['change_id'])
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Change not found'
            }
        }

        return jsonify(response), 404

    if len(session.query(Review).filter_by(change_id=change.id).all()) > 0:
        response = {
            'error': {
                'code': 400,
                'type': 'BAD_REQUEST',
                'message': 'Review already exist'
            }
        }

        return jsonify(response), 400

    review_data['reviewer_id'] = 1  # Change to logged-in user id
    review_data['comment']

    review = db_utils.create_entry(Review, **review_data)

    if review.verdict is True:
        change_article(change)
    else:
        change_data = {'status': 'denied'}
        db_utils.update_entry(Change, change.id, **change_data)

    return jsonify(ReviewInfo().dump(review))


@api_blueprint.route("/review/<int:change_id>", methods=["GET"])
def get_review_by_change_id(change_id):
    review = session.query(Review).filter_by(change_id=change_id).first()
    if review is None:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Review not found'
            }
        }

        return jsonify(response), 404

    return jsonify(ReviewInfo().dump(review))


@api_blueprint.route("/review/<int:change_id>", methods=["PUT"])
def update_review(change_id):
    review = session.query(Review).filter_by(change_id=change_id).first()
    if review is None:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Review not found'
            }
        }

        return jsonify(response), 404

    if review.verdict is True:
        response = {
            'error': {
                'code': 400,
                'type': 'BAD_REQUEST',
                'message': 'Nothing can be done. Changes already applied.'
            }
        }

        return jsonify(response), 400

    review_data = ReviewUpdate().load(request.json)
    if review_data['verdict'] is False:
        response = {
            'error': {
                'code': 400,
                'type': 'BAD_REQUEST',
                'message': 'You can`t change verdict to denied'
            }
        }

        return jsonify(response), 400

    review_updated = db_utils.update_entry(Review, review.id, **review_data)

    change = db_utils.get_entry_by_id(Change, review.change_id)
    change_article(change)

    return jsonify(ReviewInfo().dump(review_updated))


@api_blueprint.route("/myReviews", methods=["GET"])
def get_my_reviews():
    user_id = 2  # change to logged-in user id

    reviews = session.query(Review).filter_by(reviewer_id=user_id).all()
    return jsonify(ReviewInfo().dump(reviews, many=True))


@api_blueprint.route("/myChangesReviewed", methods=["GET"])
def get_my_changes_reviewed():
    user_id = 1  # change to logged-in user id

    reviews = []

    changes = session.query(Change).filter_by(proposer_id=user_id).all()
    for change in changes:
        review = session.query(Review).filter_by(change_id=change.id).first()
        if review is not None:
            reviews.append(review)

    return jsonify(ReviewInfo().dump(reviews, many=True))


def change_article(change):
    article_data = {'text': change.new_text,
                    'version': db_utils.get_entry_by_id(Article, change.article_id).version + 1}
    db_utils.update_entry(Article, change.article_id, **article_data)

    change_data = {'status': 'accepted'}
    db_utils.update_entry(Change, change.id, **change_data)
    changes_to_decline = session.query(Change).filter_by(status='in review', article_id=change.article_id,
                                                         article_version=change.article_version).all()

    change_data['status'] = 'denied'
    for decline in changes_to_decline:
        db_utils.update_entry(Change, decline.id, **change_data)
