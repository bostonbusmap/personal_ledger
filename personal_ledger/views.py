from loader import app
from models import *
from forms import *
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import csv
import re

from categorize import categorize_expenses, categorize_columns, CATEGORIZE_COLUMN_OPTIONS

@app.route('/')
def index():
    return redirect(url_for('accounts'))

@app.route('/transactions')
def transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions, title="Transactions")

@app.route('/accounts')
def accounts():
    accounts = Account.query.order_by(Account.full_title)
    return render_template('accounts.html', accounts=accounts, title="Accounts")

@app.route('/accounts/new', methods=['GET'])
def add_account():
    return render_template('add_account.html', title="Accounts")

def _make_options():
    class Option:
        def __init__(self, value):
            self.value = value
            self.description = value
    return [Option("Date"),
            Option("Withdrawal"),
            Option("Deposit"),
            Option("Description"),
            Option("Number")]


@app.route('/import_transactions', methods=['GET'])
def import_transactions():
    lines = None
    selections = None

    options = _make_options()

    return render_template('import_transactions.html', lines=lines, selections=selections, options=options, title="Transactions")

@app.route('/rules/create', methods=['POST'])
def rules_create():
    form = CreateRuleForm(request.form)
    if form.validate():
        regex = form.regex.data
        account_id = form.account_id.data
        weight = form.weight.data
        rule = Rule(regex, Account.query.get(account_id), weight)
        db.session.add(rule)
        db.session.commit()
    else:
        flash("Form error")
    return redirect(url_for('rules'))



@app.route('/rules', methods=['GET'])
def rules():
    rules = Rule.query.all()
    form = CreateRuleForm(request.form)
    return render_template('rules.html', title="Rules", rules=rules, form=form)

@app.route('/rules/new_partial', methods=['GET', 'POST'])
def rules_new_partial():
    form = CreateRuleForm(request.form)
    return render_template('add_rule_partial.html', title="Rules", form=form)

@app.route('/categorize_transactions', methods=['GET', 'POST'])
def categorize_transactions():
    if request.method == 'GET':
        return redirect(url_for('import_transactions'))
    file = request.files['file']
    if file:
        lines = [line for line in csv.reader(file)]
        max_length = 0
        for line in lines:
            max_length = max(max_length, len(line))
            
        select_columns = categorize_columns(lines)
        select_expenses = categorize_expenses(lines, select_columns)
    else:
        flash("File was not uploaded")

    options = CATEGORIZE_COLUMN_OPTIONS
    accounts = Account.query.order_by(Account.full_title).all()

    pairs = [(lines[i], select_expenses[i]) for i in xrange(len(lines))]

    return render_template('categorize_transactions.html', lines=lines, select_columns=select_columns,
                           pairs=pairs, options=options, accounts=accounts)


@app.route('/save_transactions', methods=['POST'])
def save_transactions():
    pass
    
@app.route('/transactions_partial', methods=['GET'])
def transactions_partial():
    transactions = Transaction.query.all()
    regex = request.args.get('regex')
    if regex:
        transactions = [transaction for transaction in transactions
                        if re.match(regex, transaction.description)]

    return render_template('transactions_partial.html', transactions=transactions)
        

