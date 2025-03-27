from flask import Blueprint, render_template, request, redirect, url_for
from foodtracker.models import Food, Log
from foodtracker.extensions import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
	
	logs = Log.query.order_by(Log.date.desc()).all()
	log_dates = []

	for log in logs:
		proteins=0
		carbs=0
		fats=0
		calories=0

		for food in  log.foods:
			proteins+= food.proteins
			carbs+= food.carbs
			fats+= food.fats
			calories+=food.calories



		log_dates.append({
			'log_date' :log,
			'proteins' :proteins,
			'carbs' :carbs,
			'fats' :fats,
			'calories' :calories
			})

	return render_template('index.html',log_dates=log_dates)


@main.route('/create_log', methods=['POST'])
def create_log():
    date_str = request.form.get('date')
    
    if not date_str:
        return "Date is required", 400  # Return an error if missing
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD.", 400

    log = Log(date=date)
    db.session.add(log)
    db.session.commit()

    return redirect(url_for('main.view', log_id=log.id))


@main.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        food_name = request.form.get('food-name')
        proteins = request.form.get('protein', type=float)
        carbs = request.form.get('carbohydrates', type=float)
        fats = request.form.get('fat', type=float)
        food_id = request.form.get('food-id')

        if food_id:  # Updating existing food
            food = Food.query.get(food_id)
            if food:
                food.name = food_name
                food.proteins = proteins
                food.carbs = carbs
                food.fats = fats
        else:  # Adding new food
            new_food = Food(name=food_name, proteins=proteins, carbs=carbs, fats=fats)
            db.session.add(new_food)

        db.session.commit()

        return redirect(url_for('main.add'))

    foods = Food.query.all()
    return render_template('add.html', foods=foods, food=None)


@main.route('/delete_food/<int:food_id>', methods=['POST'])
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()

    return redirect(url_for('main.add'))


@main.route('/edit_food/<int:food_id>')
def edit_food(food_id):
    food = Food.query.get_or_404(food_id)
    foods = Food.query.all()

    return render_template('add.html', food=food, foods=foods)


@main.route('/view/', defaults={'log_id': None})
@main.route('/view/<int:log_id>')
def view(log_id):
    if log_id is None:
        log = Log.query.order_by(Log.date.desc()).first()  # Get the most recent log
        if not log:
            return "No logs found. Create a log first.", 404  # Handle empty database case
        return redirect(url_for('main.view', log_id=log.id))

    log = Log.query.get_or_404(log_id)
    foods = Food.query.all()

    totals = {
        'protein' : 0,
        'carbs' : 0,
        'fat' : 0,
        'calories' : 0
    }

    for food in log.foods:
        totals['protein'] += food.proteins
        totals['carbs'] += food.carbs
        totals['fat'] += food.fats 
        totals['calories'] += food.calories

    return render_template('view.html', foods=foods, log=log, totals=totals)



@main.route('/add_food_to_log/<int:log_id>', methods=['POST'])
def add_food_to_log(log_id):
    log = Log.query.get_or_404(log_id)
    selected_food_id = request.form.get('food-select')

    if not selected_food_id:
        return "No food selected", 400

    food = Food.query.get(int(selected_food_id))

    if not food:
        return "Invalid food item", 400

    log.foods.append(food)  # Ensure Log has a Many-to-Many relationship with Food
    db.session.commit()

    return redirect(url_for('main.view', log_id=log_id))

@main.route('/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get(log_id)
    food = Food.query.get(food_id)

    log.foods.remove(food)
    db.session.commit()

    return redirect(url_for('main.view', log_id=log_id))