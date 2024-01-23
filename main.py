from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(app)

# Cafe model


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# Home route


@app.route('/cafes')
def cafes():
    all_cafes = Cafe.query.all()
    cafes_data = [cafe.to_dict() for cafe in all_cafes]

    # Diagnostic print statement
    print("Cafes data:", cafes_data)

    return render_template('cafes.html', cafes=cafes_data)


@app.route("/")
def home():
    all_cafes = Cafe.query.all()
    cafes_data = [cafe.to_dict() for cafe in all_cafes]
    return render_template("cafes.html", cafes=cafes_data)


# Get random cafe


@app.route("/random")
def get_random_cafe():
    all_cafes = Cafe.query.all()
    if all_cafes:
        random_cafe = random.choice(all_cafes)
        return jsonify(cafe=random_cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "No cafes available."}), 404


@app.route("/all")
def get_all_cafes():
    all_cafes = Cafe.query.order_by(Cafe.name).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafes1 = Cafe.query.filter_by(location=query_location).all()
    if cafes1:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes1])
    else:
        return jsonify(error={"Not Found": "No cafe at that location."}), 404


@app.route("/add", methods=["POST"])
def post_new_cafe():
    print(request.form)
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        seats=request.form.get("seats"),
        has_toilet=request.form.get("toilet") in ['true', 'True'],
        has_wifi=request.form.get("wifi") in ['true', 'True'],
        has_sockets=request.form.get("sockets") in ['true', 'True'],
        can_take_calls=request.form.get("calls") in ['true', 'True'],
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = Cafe.query.get_or_404(cafe_id)
    cafe.coffee_price = new_price
    db.session.commit()
    return jsonify(response={"success": "Successfully updated the price."})

# Delete cafe


# @app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
# def delete_cafe(cafe_id):
#     api_key = request.args.get("api-key")
#     if api_key == "TopSecretAPIKey":
#         cafe = Cafe.query.get_or_404(cafe_id)
#         db.session.delete(cafe)
#         db.session.commit()
#         return jsonify(response={"success": "Successfully deleted the cafe."})
#     else:
#         return jsonify(error={"Forbidden": "Invalid API key."}), 403
@app.route("/delete-cafe/<int:cafe_id>", methods=["POST"])
def delete_cafe(cafe_id):

    cafe = Cafe.query.get(cafe_id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        flash('Cafe successfully deleted!', 'success')
    else:
        flash('Cafe not found.', 'error')
    return redirect(url_for('display_cafes'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)