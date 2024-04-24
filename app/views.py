from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('classificacao.html')

@main.route('/classificacao')
def classificacao():
    return render_template('classificacao.html')

@main.route('/base-de-dados')
def base_de_dados():
    return render_template('base_de_dados.html')
