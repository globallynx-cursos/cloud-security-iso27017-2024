from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, ExpenseForm
from app.models import User, Expense

bp = Blueprint('routes', __name__)

@bp.route("/")
@bp.route("/home")
@login_required
def home():
    return render_template('home.html')

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('routes.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('routes.home'))

@bp.route("/expenses", methods=['GET', 'POST'])
@login_required
def expenses():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(description=form.description.data, amount=form.amount.data, owner=current_user)
        db.session.add(expense)
        db.session.commit()
        flash('Your expense has been added!', 'success')
        return redirect(url_for('routes.expenses'))
    expenses = Expense.query.filter_by(owner=current_user)
    total = sum(expense.amount for expense in expenses)
    return render_template('expenses.html', title='Expenses', form=form, expenses=expenses, total=total)

@bp.route("/delete_expense/<int:expense_id>")
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.owner != current_user:
        abort(403)
    db.session.delete(expense)
    db.session.commit()
    flash('Your expense has been deleted!', 'success')
    return redirect(url_for('routes.expenses'))
