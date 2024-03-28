from flask import Flask,render_template,url_for,request,redirect,flash,session
import mysql.connector
from cmail import sendmail
from otp import genotp

app=Flask(__name__)
#secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
mydb=mysql.connector.connect(host="localhost",user="root",password="system",db="blog")
with mysql.connector.connect(host="localhost",user="root",password="system",db="blog"):
    cursor=mydb.cursor(buffered=True)
    cursor.execute("create table if not exists register(username varchar(50) primary key,mobile varchar(30) unique,email varchar(250) unique,address varchar(30),password varchar(50))")
    cursor.execute("create table if not exists login(username varchar(30) primary key,password varchar(50))")
    

mycursor=mydb.cursor()

@app.route('/re',methods=['GET','POST'])
def regi():
    if request.method=='POST':
        username=request.form.get('username')
        mobile=request.form.get('mobile')
        email=request.form.get('email')
        address=request.form.get('address')
        password=request.form.get('password')
        otp=genotp()
        sendmail(to=email,subject="thanks for registration",body=f'otp is : {otp}')
        return render_template("verification.html",username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)
        

    return render_template('register.html')
@app.route('/otp/<username>/<mobile>/<email>/<address>/<password>/<otp>',methods=["GET","POST"])
def otp(username,mobile,email,address,password,otp):
    if request.method=='POST':
        uotp=request.form["uotp"]
        cursor=mydb.cursor(buffered=True)
        if otp==uotp:
            cursor.execute('insert into register values(%s,%s,%s,%s,%s)',[username,mobile,email,address,password])
            mydb.commit()
            cursor.close()
            return redirect(url_for('log'))
    return render_template("verification.html",username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)
    

 
@app.route('/lo',methods=["GET","POST"])
def log():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from register where username=%s && password=%s',[username,password])
        data=cursor.fetchone()[0]
        if data==1:
            session['username']=username
            if not session.get(session['username']):
                session[session['username']]={}
            return redirect(url_for('homepage'))
        else:
            return 'Invalid username and password'

            
    return render_template('login.html')
@app.route('/logout')
def logout():
    if session.get('username'):
        session.pop('username')
    return redirect(url_for('log'))
@app.route('/hom')
def homepage():
    return render_template('homepage.html')
@app.route('/post',methods=['GET','POST'])
def add_post():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into posts (title,content,slug) values(%s,%s,%s)',[title,content,slug])
        mydb.commit()
        cursor.close()
    return render_template('add_post.html')
@app.route('/view')
def view_posts():
    cursor=mydb.cursor(buffered=True)
    cursor.execute("select * from posts")
    posts=cursor.fetchall()
    print(posts)
    cursor.close()
    return render_template('view_posts.html',posts=posts)


#create admin page

@app.route('/admin')
def admin():
    return render_template('admin.html')

#delete button
@app.route('/delete_post/<int:id>',methods=['POST'])
def delete_post(id):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select * from posts where id=%s',(id,))
    post=cursor.fetchone()
    cursor.execute('DELETE FROM posts WHERE id=%s',(id,))
    
    mydb.commit()
    cursor.close()
    return redirect(url_for('view_posts'))
#update row
@app.route('/update_post/<int:id>',methods=['GET','POST'])
def update_post(id):
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('UPDATE posts SET title=%s,content=%s,slug=%s where id=%s',(title,content,slug,id))
        mydb.commit()
        cursor.close()
        return redirect(url_for('view_posts'))
    else:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from posts where id=%s',(id,))
        post=cursor.fetchone()
        cursor.close()
        return render_template('update.html',post=post)





app.run(debug=True,use_reloader=True)