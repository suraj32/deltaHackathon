from flask import Flask, render_template, redirect, request
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = '__delta__'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    webmail = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    books = db.relationship('Book', backref = "owner")

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btitle = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    pages = db.relationship('Page',backref = 'bsource')

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ptext = db.Column(db.String)
    pimg = db.Column(db.String)
    bsource_id = db.Column(db.Integer,db.ForeignKey('book.id'))

@app.route('/')
def hello_world():
    return render_template('layout.html')

@app.route('/login',methods = ["GET","POST"])
def login():
    if request.method=='POST':
        webmail = request.form['name']
        print(webmail)
        psword = request.form['password']
        user = User.query.filter_by(webmail = webmail).first()
        if webmail and psword:
            if user :
                if user.password == psword:
                    return render_template('base.html',user = user)
                else:
                    flash("Incorrect Password")
                    return redirect("/login")
            else:
                flash('Incorrect webmail format or Not registered')
                return redirect("/login")
        else:
            flash('All credentials are required')
            return redirect('/login')
    return render_template('login.html')

def allowed_format(webmail):
    return (len(webmail)==18) and '@' in webmail and '.' in webmail and (webmail.rsplit('@', 1)[1] == 'nitt.edu')

@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method=='POST':
        webmail = request.form['name']
        password = request.form['psword']
        confirm = request.form['repeatPassword']
        #print(webmail)
        if webmail and password and confirm:
            user = User.query.filter_by(webmail = webmail).first()
            if allowed_format(webmail):
                if user:
                    flash('Already Registered--')
                    return redirect('/register')
                elif password == confirm :
                    person = User(webmail = webmail,password= confirm)
                    print(person)
                    db.session.add_all([ person,
                        Book(btitle = 'b1',owner = person),
                        Book(btitle = 'b2',owner = person),
                        Book(btitle = 'b3',owner = person),
                        Book(btitle = 'b4',owner = person),
                        Book(btitle = 'b5',owner = person),
                        Book(btitle = 'b6',owner = person),
                        Book(btitle = 'b7',owner = person),
                        Book(btitle = 'b8',owner = person)])
                    #db.session.add(person,b1,b2,b3,b4,b5,b6,b7,b8)
                    db.session.commit()
                    return redirect('/login')
                else:
                    flash('Confirm passowrd properly')
                    return redirect('/register')
            else:
                flash('Webmail format is not satisfied')
                return redirect('/register')
        else:
            flash('All credentials are required')
            return redirect('/register')
    return render_template('register.html')

@app.route('/logout')
def logout():
    return render_template('layout.html')

@app.route('/base/<int:id>')
def base(id):
    user = User.query.filter_by(id =id).first()
    return render_template('base.html',user = user)

@app.route('/index/<bid>/<pid>')
def index(bid,pid):
    book = Book.query.filter_by(id = bid).first()
    user = User.query.filter_by(id = book.owner_id).first()
    if pid == 1:
        page1 = Page(ptext = '',bsource = book)
    else: 
        page1 = Page.query.filter_by(id = pid).first()
    db.session.add(page1)
    db.session.commit()
    return render_template('index.html',book = book,user = user,page = page1)

if __name__ == "__main__":
    app.run(debug=True)
