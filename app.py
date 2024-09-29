from flask import Flask
from flask_pymongo import PyMongo
from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
  

from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.income import Income
from models.expense import Expense
from models.budget import Budget
from bson import ObjectId
import logging
# Income route
from models.activity_log import ActivityLog


logging.basicConfig(level=logging.INFO)
import logging

app = Flask(__name__)
app.config.from_object('config.Config')

mongo = PyMongo(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login if not logged in

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)  # This remains unchanged since get() already retrieves the user


@app.route('/')
def home():
    return render_template('home.html')

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']  # Get email from the form
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        # Check if username or email already exists
        if mongo.db.users.find_one({"username": username}):
            flash('Username already exists. Please choose a different one.')
            return render_template('pages-register.html')

        if mongo.db.users.find_one({"email": email}):
            flash('Email already exists. Please choose a different one.')
            return render_template('pages-register.html')

        # Check if passwords match
        if password != password_confirm:
            flash('Passwords do not match. Please try again.')
            return render_template('pages-register.html')

        # Create the user account
        User.create(username, email, password)  # Pass email to create method
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('pages-register.html')




# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['username']  # The input field still uses 'username'
        password = request.form['password']
        user = User.get_by_username_or_email(identifier)  # Check by username or email

        # Use User.verify_password to check the password
        if user and User.verify_password(user['password'], password):
            user_instance = User(user['_id'], user['username'], user['email'])  # Include email
            login_user(user_instance)
            return redirect(url_for('dashboard'))

        flash('Invalid username or password')
    return render_template('pages-login.html')




# Dashboard route



@app.route('/dashboard')
@login_required
def dashboard():
    incomes = Income.get_all_incomes(user_id=current_user.id)
    categories = Budget.get_all_categories(user_id=current_user.id)
    budgets = Budget.get_all_budgets(user_id=current_user.id)
    expenses = Expense.get_all_expenses(user_id=current_user.id)

    recent_activities = mongo.db.activity_logs.find(
        {"user_id": current_user.id}
    ).sort("timestamp", -1).limit(10)

   
    # Calculate total income
    total_income = sum(income['amount'] for income in incomes)

    # Calculate allocated income (sum of all budgets)
    allocated_income = sum(budget['amount'] for budget in budgets)

    # Calculate remaining income (total income - allocated income)
    remaining_income = total_income - allocated_income

    return render_template('index.html', incomes=incomes, categories=categories, budgets=budgets, expenses=expenses,
                           total_income=total_income, allocated_income=allocated_income, remaining_income=remaining_income,recent_activities=recent_activities)








@app.route('/profile')
@login_required
def profile():
    user = User.get(current_user.id)  # Get the current logged-in user
    return render_template('users-profile.html', user=user)  # Pass user to the template


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))















@app.route('/add_income', methods=['POST'])
@login_required
def add_income():
    income_name = request.form.get('income_name')
    income_amount = float(request.form.get('income_amount'))
    Income.add_income(user_id=current_user.id, amount=income_amount, source=income_name)
    
    # Log this activity
    ActivityLog.log_activity(current_user.id, "added", "income", income_name)

    flash('Income added successfully!')
    return redirect(url_for('dashboard'))



# Budget route
@app.route('/add_budget', methods=['POST'])
@login_required
def add_budget():
    budget_name = request.form.get('budget_name')
    budget_amount = float(request.form.get('budget_amount'))

    # Calculate total income and allocated income
    incomes = Income.get_all_incomes(user_id=current_user.id)
    total_income = sum(income['amount'] for income in incomes)
    budgets = Budget.get_all_budgets(user_id=current_user.id)
    allocated_income = sum(budget['amount'] for budget in budgets)
    remaining_income = total_income - allocated_income

    # Check if the budget amount exceeds the remaining income
    if budget_amount > remaining_income:
        flash(f'Your balance is insufficient to create this budget. '
              f'Your current income balance is {remaining_income:.2f}, '
              f'please try to grow your income and come back later.')
        return redirect(url_for('dashboard'))

    Budget.add_budget(user_id=current_user.id, amount=budget_amount, name=budget_name)

    # Log this activity
    ActivityLog.log_activity(current_user.id, "added", "budget", budget_name)
    flash('Budget created successfully!')
    return redirect(url_for('dashboard'))


# Expense route


@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    expense_name = request.form['expense_name']
    expense_amount = float(request.form['expense_amount'])
    budget_category = request.form['budget_category']

    # Check remaining budget before adding expense
    remaining_amount = Budget.get_remaining_amount(current_user.id, budget_category)
    
    if expense_amount > remaining_amount:
        flash(f'Insufficient funds in "{budget_category}" budget. Remaining amount is {remaining_amount:.2f}.')
        return redirect(url_for('dashboard'))

    Expense.add_expense(user_id=current_user.id, name=expense_name, amount=expense_amount, category=budget_category)
    # Log this activity
    ActivityLog.log_activity(current_user.id, "added", "expense", expense_name)
    flash('Expense added successfully!')
    return redirect(url_for('dashboard'))












@app.route('/edit_income', methods=['POST'])
@login_required
def edit_income():
    income_id = request.form['income_id']
    new_name = request.form['income_name']
    new_amount = float(request.form['income_amount'])
    Income.update_income(income_id, new_name, new_amount)  # Create this method in Income model
    ActivityLog.log_activity(current_user.id, "edited", "income", new_name)
    flash('Income updated successfully!')
    return redirect(url_for('dashboard'))

    

@app.route('/delete_income/<income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    # Fetch income details before deletion
    income = Income.get_income_by_id(income_id)
    income_name = income['source'] if income else "Unknown Income"  # Fallback if income not found

    # Delete income
    Income.delete_income(income_id)

    # Log this delete action
    ActivityLog.log_activity(current_user.id, "deleted", "income", income_name)

    flash('Income deleted successfully!')
    return redirect(url_for('dashboard'))





@app.route('/edit_budget', methods=['POST'])
@login_required
def edit_budget():
    budget_id = request.form['budget_id']
    new_name = request.form['budget_name']
    new_amount = float(request.form['budget_amount'])

    # Calculate total income and allocated income
    incomes = Income.get_all_incomes(user_id=current_user.id)
    total_income = sum(income['amount'] for income in incomes)
    budgets = Budget.get_all_budgets(user_id=current_user.id)
    allocated_income = sum(budget['amount'] for budget in budgets)
    remaining_income = total_income - allocated_income

    # Check if the new budget amount exceeds the remaining income
    if new_amount > remaining_income:
        flash(f'Your balance is insufficient to update this budget. '
              f'Your current income balance is {remaining_income:.2f}, '
              f'please try to grow your income and come back later.')
        return redirect(url_for('dashboard'))

    Budget.update_budget(budget_id, new_name, new_amount)
    ActivityLog.log_activity(current_user.id, "edited", "budget", new_name)
    flash('Budget updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/delete_budget/<budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
      # Create this method in Budget model

    budget = Budget.get_budget_by_id(budget_id)
    budget_name = budget['name'] if budget else "Unknown Budget"  # Fallback if income not found

    # Delete budget
    Budget.delete_budget(budget_id)

    # Log this delete action
    ActivityLog.log_activity(current_user.id, "deleted", "budget", budget_name)
    flash('Budget deleted successfully!')
    return redirect(url_for('dashboard'))









@app.route('/edit_expense', methods=['POST'])
@login_required
def edit_expense():
    expense_id = request.form['expense_id']
    new_name = request.form['expense_name']
    new_amount = float(request.form['expense_amount'])
    new_category = request.form['expense_category']

    # Check remaining budget before updating expense
    remaining_amount = Budget.get_remaining_amount(current_user.id, new_category)
    
    if new_amount > remaining_amount:
        flash(f'Insufficient funds in "{new_category}" budget. Remaining amount is {remaining_amount:.2f}.')
        return redirect(url_for('dashboard'))

    Expense.update_expense(expense_id, new_name, new_amount, new_category)
    ActivityLog.log_activity(current_user.id, "edited", "expense", new_name)
    flash('Expense updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/delete_expense/<expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    

    expense = Expense.get_expense_by_id(expense_id)
    expense_name = expense['name'] if expense else "Unknown Expense"  # Fallback if income not found

    # Delete budget
    Expense.delete_expense(expense_id)

    # Log this delete action
    ActivityLog.log_activity(current_user.id, "deleted", "expense", expense_name)
    flash('Expense deleted successfully!')
    return redirect(url_for('dashboard'))





@app.route('/change-password', methods=['POST'])
@login_required  # Ensure the user is logged in
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    renew_password = request.form['renew_password']

    # Verify the current password
    user = User.get(current_user.id)  # Get the current logged-in user
    if not user or not User.verify_password(user.password, current_password):  # Updated to use verify_password
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))

    # Check if new passwords match
    if new_password != renew_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('profile'))

    # Hash the new password and update it in the database
    hashed_new_password = generate_password_hash(new_password)
    mongo.db.users.update_one({"_id": ObjectId(user.id)}, {"$set": {"password": hashed_new_password}})

    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))



if __name__ == '__main__':
    app.run(debug=True, port=3000)
