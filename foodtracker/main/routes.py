from flask import Blueprint,Flask, render_template, request, redirect, url_for,flash,current_app
from foodtracker.models import Food, Log, User
from werkzeug.security import generate_password_hash, check_password_hash
from foodtracker.extensions import db,mail
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Mail,Message

main = Blueprint('main', __name__)
s = URLSafeTimedSerializer('SHSHSHSHHSHS')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No account found with this email.', category='error')
        elif not check_password_hash(user.password, password):
            flash('Incorrect password.', category='error')
        elif not user.confirmed:  
            print(f"User {email} is not confirmed!")  # ✅ Debug log
            flash('Please confirm your email before logging in.', category='warning')
        else:
            print(f"User {email} logged in successfully!")  # ✅ Debug log
            login_user(user, remember=True)
            flash('Logged in successfully!', category='success')
            return redirect(url_for('main.index'))

    return render_template('login.html', user=current_user)






@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists!', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(firstname) < 2:
            flash('Firstname must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # ✅ Generate token and send confirmation email
            token = s.dumps(email, salt='email-confirm')
            msg = Message('Confirm Your Email', sender='derrickndirangu868@gmail.com', recipients=[email])
            link = url_for('main.confirm_email', token=token, _external=True)
            msg.body = f'Click this link to confirm your email: {link}'
            mail.send(msg)

            # ✅ Create user with confirmed=False
            new_user = User(email=email, first_name=firstname,
                            password=generate_password_hash(password1, method="pbkdf2:sha256"),
                            confirmed=False)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created! Check your email to confirm.', category='success')
            return redirect(url_for('main.login'))

    return render_template('signup.html', user=current_user)

@main.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)  # Token valid for 1 hour
        user = User.query.filter_by(email=email).first()

        if user:
            user.confirmed = True  # ✅ Mark email as confirmed
            db.session.commit()  # ✅ Save changes to database
            flash('Your email has been confirmed! You can now log in.', 'success')
            return redirect(url_for('main.login'))

    except SignatureExpired:
        flash('Confirmation link expired. Please request a new one.', 'danger')
        return redirect(url_for('main.signup'))

    flash('Invalid confirmation link.', 'danger')
    return redirect(url_for('main.signup'))


    
    

@main.route('/')
@login_required  # ✅ Requires user to be logged in
def index():
    print(f"Current user ID: {current_user.id}")  # Debugging

    logs = Log.query.filter_by(user_id=current_user.id).order_by(Log.date.desc()).all()
    
    print(f"Logs for user {current_user.id}: {logs}")  # Debugging

    log_dates = []  # ✅ Ensure log_dates is properly initialized

    for log in logs:  # ✅ Fix indentation
        proteins = sum(food.proteins for food in log.foods)
        carbs = sum(food.carbs for food in log.foods)
        fats = sum(food.fats for food in log.foods)
        calories = sum(food.calories for food in log.foods)

        log_dates.append({
            'log_date': log,
            'proteins': proteins,
            'carbs': carbs,
            'fats': fats,
            'calories': calories
        })

    return render_template('index.html', log_dates=log_dates, user=current_user)




@main.route('/create_log', methods=['POST'])
def create_log():
    date_str = request.form.get('date')
    
    if not date_str:
        return "Date is required", 400  # Return an error if missing
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD.", 400

    log = Log(date=date, user_id=current_user.id)
    db.session.add(log)
    db.session.commit()

    return redirect(url_for('main.view', log_id=log.id))


@main.route('/add', methods=['GET', 'POST'])
@login_required  # Ensure only logged-in users can access
def add():
    if request.method == 'POST':
        food_name = request.form.get('food-name').strip()  # Trim whitespace
        proteins = request.form.get('protein', type=float)
        carbs = request.form.get('carbohydrates', type=float)
        fats = request.form.get('fat', type=float)
        food_id = request.form.get('food-id')

        # Check if food name already exists for this user
        existing_food = Food.query.filter_by(name=food_name, user_id=current_user.id).first()

        if existing_food and not food_id:  # If adding a new food and it already exists
            flash(f"Food '{food_name}' already exists!", category="error")
            return redirect(url_for('main.add'))

        if food_id:  # Updating existing food
            food = Food.query.get(food_id)
            if food and food.user_id == current_user.id:  # Ensure the food belongs to the user
                food.name = food_name
                food.proteins = proteins
                food.carbs = carbs
                food.fats = fats
                db.session.commit()  # ✅ Commit changes for updating food
                flash(f"{food_name} successfully updated!", category="success")
            else:
                flash("Food item not found or unauthorized.", category="error")
        else:  # Adding new food
            new_food = Food(
                name=food_name,
                proteins=proteins,
                carbs=carbs,
                fats=fats,
                user_id=current_user.id
            )
            db.session.add(new_food)
            db.session.commit()  # ✅ Commit after adding new food
            flash(f"{food_name} successfully added!", category="success")

        return redirect(url_for('main.add'))

    # ✅ Only fetch foods for the current user
    foods = Food.query.filter_by(user_id=current_user.id).all()
    return render_template('add.html', foods=foods, food=None, user=current_user)




@main.route('/delete_food/<int:food_id>', methods=['GET', 'POST'])
@login_required
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    food_name = food.name  # Store food name before deleting
    
    # Ensure only the owner can delete
    if food.user_id != current_user.id:
        flash("You are not authorized to delete this food item!", category="error")
        return redirect(url_for('main.add'))
    
    db.session.delete(food)
    db.session.commit()

    flash(f"🗑️ {food_name} has been deleted successfully!", category="success")
    return redirect(url_for('main.add'))




@main.route('/edit_food/<int:food_id>')
@login_required  # Ensure only logged-in users can access
def edit_food(food_id):
    food = Food.query.get_or_404(food_id)
    
    # ✅ Ensure only the owner of the food can edit it
    if food.user_id != current_user.id:
        flash("You are not authorized to edit this food item!", category="error")
        return redirect(url_for('main.add'))
    
    foods = Food.query.filter_by(user_id=current_user.id).all()  # ✅ Show only user's foods

    return render_template('add.html', food=food, foods=foods, user=current_user)  # ✅ Pass user



@main.route('/view/', defaults={'log_id': None})
@main.route('/view/<int:log_id>')
def view(log_id):
    log = Log.query.filter_by(id=log_id, user_id=current_user.id).first()
    if log_id is None:

        log = Log.query.order_by(Log.date.desc()).first()
          # Get the most recent log
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

    return render_template('view.html', foods=foods, log=log, totals=totals, user=current_user)


@main.route('/add_food_to_log/<int:log_id>', methods=['POST'])
def add_food_to_log(log_id):
    log = Log.query.get_or_404(log_id)
    selected_food_id = request.form.get('food-select')

    if not selected_food_id:
        flash("No food selected!", category="error")
        return redirect(url_for('main.view', log_id=log_id))

    food = Food.query.get(int(selected_food_id))

    if not food:
        flash("Invalid food item!", category="error")
        return redirect(url_for('main.view', log_id=log_id))

    # Check if food is already in log (to prevent duplicates)
    if food in log.foods:
        flash(f"{food.name} is already in this log!", category="error")
    else:
        log.foods.append(food)
        db.session.commit()
        flash(f"{food.name} successfully added!", category="success")

    return redirect(url_for('main.view', log_id=log_id))

@main.route('/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get_or_404(log_id)
    food = Food.query.get_or_404(food_id)

    if food not in log.foods:
        flash(f"{food.name} is not in this log!", category="error")
    else:
        log.foods.remove(food)
        db.session.commit()
        flash(f"{food.name} successfully removed!", category="success")

    return redirect(url_for('main.view', log_id=log_id))




