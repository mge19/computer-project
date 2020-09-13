from flask import Flask,render_template,redirect,url_for,request
from sqlalchemy import create_engine,Column,Integer,String,Boolean,MetaData,Table,text
from gtts import gTTS
import os
import speech_recognition as sr
engine = create_engine('sqlite:///database.db', echo = True,connect_args={'check_same_thread':False})
meta=MetaData()
css="""<!DOCTYPE html>
<html>
<head>
<style>
  body{
    background-color:blue;
  }
  h1 {
    color: white;
	text-align:center;
	font-family: verdana;
	font-size:40px;
  }
    p {
    color: black;
	text-align:left;
	font-family: verdana;
	font-size:15px;
  }
  input[type=submit] {
    background-color: #2f806a;
	color: yellow;
  }
  input[type=text]:focus {
    border: 4px solid #235;
  }
  table{
  border-collapse:collapse;}
  tabke,th,td{
  border: 1px solid purple;}
  </style>"""
users=Table(
    'users',meta,
    Column('mail_id',Integer,primary_key=True),
    Column('name',String,nullable=False),
    Column('surname',String,nullable=False),
    Column('username',String,nullable=False),
    Column('password',String,nullable=False))
mails_inbox=Table(
    'mails_inbox',meta,
    Column('mail_id',Integer,primary_key=True),
    Column('from_person',String,nullable=False),
    Column('to_person',String,nullable=False),
    Column('subject',String),
    Column('content',String),
    Column('deleted',Boolean,default=False,nullable=False))
mails_outbox=Table(
    'mails_outbox',meta,
    Column('id',Integer,primary_key=True),
    Column('from_person',String,nullable=False),
    Column('to_person',String,nullable=False),
    Column('subject',String),
    Column('content',String),
    Column('deleted',Boolean,default=False,nullable=False))
users.create(engine,checkfirst=True)
mails_inbox.create(engine,checkfirst=True)
mails_outbox.create(engine,checkfirst=True)
conn=engine.connect()
app=Flask(__name__)
@app.route('/')
def mainpage():
    txt="""Welcome to the MailLAB!It is a useful e-mail application for visually impaired people.If you are a blind person,you should say just "I am a blind person."."""
    obj=gTTS(text=txt,lang='en',slow=True)
    obj.save("start.mp3")
    os.system("start.mp3")
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
    text=r.recognize_google(audio,language='en_US',show_all=True)
    if(text=="I am a blind person."):
        return redirect(url_for('page_for_visually_impaired_user_actions'))
    return render_template('mainpage.html')
@app.route('/login',methods=['GET'])
def login():
    str1=css+"""<title>
     MailLAB Log in
   </title>
  </head>
  <body>
    <h1>Log in</h1>
    <form type="get" id="login">Username: <input type="text" name="username"><br>
    Password:  <input type="text" name="password"><br>
    <input type="submit" value="Log In">
	</form>
    <a href="http://localhost:5000/forgotpassword">Forgot password?</a>"""
    a=request.args.get('username')
    b=request.args.get('password')
    txt=text("SELECT COUNT (*) FROM users WHERE username=:A")
    x=conn.execute(txt,A=a).scalar()
    t=text("SELECT password FROM users WHERE username=:A")
    y=conn.execute(t,A=a).scalar()
    if a!=None and a!="" and b!="" and b!=None and x!=0 and y==b:
        return redirect(url_for('mainmenu',username=a))
    elif a=="" or b=="":
        str1+="<p>Error! All of these blanks must be filled.</p>"
    elif x==0 and a!=None and b!=None:
        str1+="<p> Error! User not found. </p>"
    elif y!=b and a!=None and b!=None:
        str1+="<p> Error! Invalid password. </p>"
    return str1+"</body></html>"
@app.route('/signup',methods=['GET'])
def signup():
    a=request.args.get('name')
    b=request.args.get('surname')
    c=request.args.get('username')
    d=request.args.get('password')
    txt=text("SELECT COUNT (*) FROM users WHERE username=:A")
    x=conn.execute(txt,A=c).scalar()
    if a!=None and a!="" and b!="" and b!=None and c!="" and c!=None and d!="" and d!=None and x==0:
        t=text("INSERT INTO users (name,surname,username,password) VALUES (:A,:B,:C,:D)")
        conn.execute(t,A=a,B=b,C=c,D=d)
        return redirect(url_for('mainmenu',username=c))
    return render_template('signup.html')
@app.route('/forgotpassword',methods=['GET'])
def forgotpassword():
    str1=css+"""<title>
     Forgot password
   </title>
  </head>
  <body>
    <p>If you forgot your password, please define a new password.</p>
    <form type="get" id="login">Username: <input type="text" name="username"><br>
    Password:  <input type="text" name="password"><br>
    <input type="submit" value="Change password">
	</form>
    <a href="http://localhost:5000/forgotpassword">Forgot password?</a>"""
    a=request.args.get('username')
    b=request.args.get('password')
    txt=text("SELECT COUNT (*) FROM users WHERE username=:A")
    x=conn.execute(txt,A=a).scalar()
    t=text("SELECT password FROM users WHERE username=:A")
    y=conn.execute(t,A=a).scalar()
    if a!=None and a!="" and b!="" and b!=None and x!=0 and y!=b:
        return redirect(url_for('mainmenu',username=a))
    elif a=="" or b=="":
        str1+="<p>Error! All of these blanks must be filled.</p>"
    elif x==0 and a!=None and b!=None:
        str1+="<p> Error! User not found. </p>"
    elif y==b and a!=None and b!=None:
        str1+="<p>Password should be different. </p>"
    return str1+"</body></html>"
@app.route('/mainmenu/<username>')
def mainmenu(username):
    t=text("SELECT name,surname FROM users where username=:A")
    name=conn.execute(t,A=username).fetchone()
    return css+"""<head>
   <title>
     MailLAB Main Menu
   </title>
  </head>
  <body>
<h1>Hello,{0} {1}! Please select one of the following actions:</h1>
<a href="http://localhost:5000/inbox/{2}">Show my inbox</a><br>
<a href="http://localhost:5000/outbox/{3}">Show my sended e-mails</a><br>
<a href="http://localhost:5000/deleted/{4}">Show my deleted e-mails</a><br>
<a href="http://localhost:5000/write_email/{5}">Write a new e-mail</a><br>
<a href="http://localhost:5000"> Log out</a>
  </body>
</html>""".format(name[0],name[1],username,username,username,username)
@app.route('/write_email/<username>',methods=['GET'])
def write_email(username):
    str1=css+"""  <title>
     Write e-mail
   </title>
  </head>
  <body>
	<h1> Write a new e-mail</h1>
    <form type="get" id="login">To who: <input type="text" name="receiver"><br>
    Subject:  <input type="text" name="subject"><br>
	Mail:  <input type="text" name="mail"><br>
    <input type="submit" value="Send">
	</form>"""
    a=request.args.get('receiver')
    b=request.args.get('subject')
    c=request.args.get('mail')
    txt=text("SELECT COUNT (*) FROM users WHERE username=:A")    
    x=conn.execute(txt,A=a).scalar()
    if(x!=0 and a!=None and a!=""):
        ins1=text("INSERT INTO mails_inbox (from_person,to_person,subject,content,deleted) VALUES (:A,:B,:C,:D,:E)")
        conn.execute(ins1,A=username,B=a,C=b,D=c,E=False)
        ins2=text("INSERT INTO mails_outbox (from_person,to_person,subject,content,deleted) VALUES (:A,:B,:C,:D,:E)")
        conn.execute(ins2,A=username,B=a,C=b,D=c,E=False)
        return redirect(url_for('mainmenu',username=username))
    elif a=="":
        str1+="<p>Error! Enter person who will receive e-mail</p>"
    elif x==0 and a!=None and b!=None:
        str1+="<p> Error! User not found. </p>"
    return str1+"</body></html>"
@app.route('/inbox/<username>',methods=['GET'])
def inbox(username):
    t=text("SELECT name,surname FROM users where username=:A")
    name=conn.execute(t,A=username).fetchone()
    str2=list()
    str1= """<title>
                    My inbox
                </title>
             </head>
              <body>
                <h1> Dear {0} {1},You can show your incoming e-mails</h1>
                <table align="center">
                <tr>
                <th>ID</th>
                <th>From</th>
                <th>Subject</th>
                <th>Content</th></tr>""".format(name[0],name[1])
    txt=text("SELECT mail_id,from_person,subject,content FROM mails_inbox WHERE to_person=:A AND deleted=:B")
    mails=conn.execute(txt,A=username,B=False)
    for mail in mails:
        str2.append("""<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td></tr>""".format(mail[0],mail[1],mail[2],mail[3]))
    str3="""</table>Enter ID of the mail which you want to delete (you can see your deleted e-mails in your deleted e-mails folder):<form><input type="text" name="delete">
        <input type="submit" value="Delete"></form>"""
    str5="<p>Error! Invalid mail ID</p>"
    str7="<p>Error! You must enter a valid mail ID</p>"
    str6=css+str1
    for i in range(0,len(str2)):
        str6+=str2[i]
    str6+=str3
    c=request.args.get('delete')
    if c!=None and c!="":
        t0=text("SELECT to_person FROM mails_inbox WHERE mail_id=:A")
        a=conn.execute(t0,A=int(c)).scalar()
        if a==username:
            t=text("UPDATE mails_inbox SET deleted=:A WHERE mail_id=:B")
            conn.execute(t,A=True,B=int(c))
        else:
            str6+=str5
    elif c=="":
        str6+=str7
    str4="""<form><input type="submit" name="delete_all" value="Delete All"></form><br><a href="http://localhost:5000/mainmenu/%s">Go back to main menu</a></body></html>"""%(username)
    deleteall=request.args.get('delete_all')
    if deleteall:
        t0=text("UPDATE mails_inbox SET deleted=:A WHERE to_person=:B")
        a=conn.execute(t0,A=True,B=username)
    str6+=str4
    return str6
@app.route('/outbox/<username>',methods=['GET'])
def outbox(username):
    t=text("SELECT name,surname FROM users where username=:A")
    name=conn.execute(t,A=username).fetchone()
    str2=list()
    str1= """<title>
                    My outbox
                </title>
             </head>
              <body>
                <h1> Dear {0} {1},You can show your sended e-mails</h1>
                <table align="center">
                <tr>
                <th>ID</th>
                <th>From</th>
                <th>Subject</th>
                <th>Content</th></tr>""".format(name[0],name[1])
    txt=text("SELECT mail_id,to_person,subject,content FROM mails_outbox WHERE from_person=:A AND deleted=:B")
    mails=conn.execute(txt,A=username,B=False)
    for mail in mails:
        str2.append("""<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td></tr>""".format(mail[0],mail[1],mail[2],mail[3]))
    str3="""</table>Enter ID of the mail which you want to delete (you can see your deleted e-mails in your deleted e-mails folder):<form><input type="text" name="delete">
        <input type="submit" value="Delete"></form>"""
    str5="<p>Error! Invalid mail ID</p>"
    str7="<p>Error! You must enter a valid mail ID</p>"
    str6=css+str1
    for i in range(0,len(str2)):
        str6+=str2[i]
    str6+=str3
    c=request.args.get('delete')
    if c!=None and c!="":
        t0=text("SELECT from_person FROM mails_outbox WHERE mail_id=:A")
        a=conn.execute(t0,A=int(c)).scalar()
        if a==username:
            t=text("UPDATE mails_outbox SET deleted=:A WHERE mail_id=:B")
            conn.execute(t,A=True,B=int(c))
        else:
            str6+=str5
    elif c=="":
        str6+=str7
    str4="""<form><input type="submit" name="delete_all" value="Delete All"></form><br><a href="http://localhost:5000/mainmenu/%s">Go back to main menu</a></body></html>"""%(username)
    deleteall=request.args.get('delete_all')
    if deleteall:
        t0=text("UPDATE mails_outbox SET deleted=:A WHERE from_person=:B")
        a=conn.execute(t0,A=True,B=username)
    str6+=str4
    return str6
@app.route('/deleted/<username>',methods=['GET'])
def deleted(username):
    t=text("SELECT name,surname FROM users where username=:A")
    name=conn.execute(t,A=username).fetchone()
    str2=list()
    str1= """<title>
                    My deleted mails
                </title>
             </head>
              <body>
                <h1> Dear {0} {1},You can show your deleted e-mails</h1>
                <table align="center">
                <tr>
                <th>ID</th>
                <th>Description</th>
                <th>Subject</th>
                <th>Content</th></tr>""".format(name[0],name[1])
    sel_inbox=text("SELECT mail_id,from_person,subject,content FROM mails_inbox WHERE to_person=:A AND deleted=:B")
    mails_inbox=conn.execute(sel_inbox,A=username,B=True)
    for mail in mails_inbox:
        str2.append("""<tr><td>{0}</td><td>Sended by {1}</td><td>{2}</td><td>{3}</td></tr>""".format(mail[0],mail[1],mail[2],mail[3]))
    sel_outbox=text("SELECT mail_id,to_person,subject,content FROM mails_outbox WHERE from_person=:A AND deleted=:B and to_person!=:C")
    mails_outbox=conn.execute(sel_outbox,A=username,B=True,C=username)    
    for mail in mails_outbox:
        str2.append("""<tr><td>{0}</td><td>You sended to {1}</td><td>{2}</td><td>{3}</td></tr>""".format(mail[0],mail[1],mail[2],mail[3]))
    str3="""</table>Enter ID of the mail which you want to completely delete:<form><input type="text" name="delete">
    <input type="submit" value="Delete"></form>"""
    str5="<p>Error! Invalid mail ID</p>"
    str7="<p>Error! You must enter a valid mail ID</p>"
    str6=css+str1
    for i in range(0,len(str2)):
        str6+=str2[i]
    str6+=str3
    c=request.args.get('delete')
    if c!=None and c!="":
        t0=text("SELECT to_person FROM mails_inbox WHERE mail_id=:A")
        a=conn.execute(t0,A=int(request.args.get('delete'))).scalar()
        t1=text("SELECT from_person FROM mails_outbox WHERE mail_id=:A")
        b=conn.execute(t1,A=int(c)).scalar()
        if a==username or b==username:
            if a==username:
                t=text("DELETE FROM mails_inbox WHERE mail_id=:A AND deleted=:B")
                conn.execute(t,A=int(c),B=True)
            if b==username:
                n=text("DELETE FROM mails_outbox WHERE mail_id=:A AND deleted=:B")
                conn.execute(n,A=int(c),B=True)
        else:
            str6+=str5
    elif c=="":
        str6+=str7
    str4="""<form><input type="submit" name="delete_all" value="Delete All"></form><br><a href="http://localhost:5000/mainmenu/%s">Go back to main menu</a></body></html>"""%(username)
    deleteall=request.args.get('delete_all')
    if deleteall:
        t0=text("DELETE FROM mails_inbox WHERE to_person=:A")
        a=conn.execute(t0,A=username)
        t0=text("DELETE FROM mails_outbox WHERE from_person=:A")
        a=conn.execute(t0,A=username)
    str6+=str4
    return str6
@app.route('/page_for_visually_impaired_user_actions')
def page_for_visually_impaired_user_actions():
    txt="Please say login,sign up,forgot password or exit:"
    obj=gTTS(text=txt,lang='en',slow=True)
    obj.save("next.mp3")
    os.system("next.mp3")
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
    action=r.recognize_google(audio,language='en_US',show_all=True)
    if action=="Log in":
        txt="Please say your username"
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
        usr=r.recognize_google(audio,language='en_US',show_all=True)
        t=text("SELECT COUNT (*) FROM users WHERE username=:A")
        n=conn.execute(t,A=usr).scalar()
        if n==0:
            txt="User not found. Try again"
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            return redirect(url_for('page_for_visually_impaired_user_actions'))
        else:        
            txt="Please say your password"
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            r=sr.Recognizer()
            with sr.Microphone() as source:
                audio=r.listen(source)
            text=r.recognize_google(audio,language='en_US',show_all=True)
            t=text("SELECT password FROM users WHERE username=:A")
            n=conn.execute(t,A=usr).scalar()
            if n!=text:
                txt="Invalid password. Try again"
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                return redirect(url_for('page_for_visually_impaired_user_actions'))                 
            else:
                txt="Congrulations.You have successfully logged in."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                return redirect(url_for('page_for_visually_impaired_mail_actions',user=usr))
    elif action=="Sign up":
        txt="Please say your name"
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
        name=r.recognize_google(audio,language='en_US',show_all=True)
        txt="Please say your surname:"
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
        surname=r.recognize_google(audio,language='en_US',show_all=True)                 
        txt="Please say your username:"
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)   
        usr=r.recognize_google(audio,language='en_US',show_all=True)                 
        txt="Please say your username"
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
        usr=r.recognize_google(audio,language='en_US',show_all=True)
        t=text("SELECT COUNT (*) FROM users WHERE username=:A")
        n=conn.execute(t,A=usr).scalar()
        if n!=0:
            txt="This username has been already taken.Try again."
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            return redirect(url_for('page_for_visually_impaired_user_actions'))
        else:
            txt="Please say your password"
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            r=sr.Recognizer()
            with sr.Microphone() as source:
                audio=r.listen(source)
            text=r.recognize_google(audio,language='en_US',show_all=True)
            t=text("INSERT INTO users (name,surname,username,password) VALUES (:A,:B,:C,:D)")
            conn.execute(t,A=name,B=surname,C=usr,D=text)
            txt="Congrulations.You have successfully signed up."
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            return redirect(url_for('page_for_visually_impaired_mail_actions',user=usr))
    elif action=="Forgot password":
        txt="Please say your username"
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
        usr=r.recognize_google(audio,language='en_US',show_all=True)
        t=text("SELECT COUNT (*) FROM users WHERE username=:A")
        n=conn.execute(t,A=usr).scalar()
        if n==0:
            txt="User not found. Try again"
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            return redirect(url_for('page_for_visually_impaired_user_actions'))
        else:        
            txt="Please say your password"
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            r=sr.Recognizer()
            with sr.Microphone() as source:
                audio=r.listen(source)
            text=r.recognize_google(audio,language='en_US',show_all=True)
            t=text("SELECT password FROM users WHERE username=:A")
            n=conn.execute(t,A=usr).scalar()
            if n==text:
                txt="Password is already same.Try again."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                return redirect(url_for('page_for_visually_impaired_user_actions'))                 
            else:
                txt="Congrulations.You have successfully changed your password."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")                
                return redirect(url_for('page_for_visually_impaired_mail_actions',user=usr))
    elif action=="Exit":
        sys.exit()
    else:
        txt="You made an invalid choice or your voice is not heard clearly.Please try again."
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")                
        return redirect(url_for('page_for_visually_impaired_user_actions'))  
    return render_template('page_for_visually_impaired_user_actions.html')
@app.route('/page_for_visually_impaired_mail_actions/<user>')
def page_for_visually_impaired_mail_actions(user):
    txt="Say zero to write an e-mail,say one to read or delete in your e-mails,say two to go back to the main menu:"
    obj=gTTS(text=txt,lang='en',slow=True)
    obj.save("next.mp3")
    os.system("next.mp3")
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
    action=r.recognize_google(audio,language='en_US',show_all=True)
    if action=="zero":
        txt="Enter the username of the user that will receive the e-mail:"
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
        receiver=r.recognize_google(audio,language='en_US',show_all=True)
        t=text("SELECT COUNT (*) FROM users WHERE username=:A")
        n=conn.execute(t,A=receiver).scalar()
        if n==0:
            txt="User not found. Try again"
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            return redirect(url_for('page_for_visually_impaired_mail_actions',user=user))
        else:
            txt="Enter the subject of the e-mail:"
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            r=sr.Recognizer()
            with sr.Microphone() as source:
                audio=r.listen(source)
            subject=r.recognize_google(audio,language='en_US',show_all=True)
            txt="Enter the content of the e-mail:"
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            r=sr.Recognizer()
            with sr.Microphone() as source:
                audio=r.listen(source)
            content=r.recognize_google(audio,language='en_US',show_all=True)
            txt="Congrulations! You sent an e-mail successfully."
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")            
            ins1=text("INSERT INTO mails_inbox (from_person,to_person,subject,content,deleted) VALUES (:A,:B,:C,:D,:E)")
            conn.execute(ins1,A=user,B=receiver,C=subject,D=content,E=False)
            ins2=text("INSERT INTO mails_outbox (from_person,to_person,subject,content,deleted) VALUES (:A,:B,:C,:D,:E)")
            conn.execute(ins2,A=user,B=receiver,C=subject,D=content,E=False)
            return redirect(url_for('page_for_visually_impaired_mail_actions',user=user))
    elif action=="one":
        txt="Say zero to read or delete in your inbox,one to read  or delete in your sended e-mails,and three to read or delete in your deleted e-mails."
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
        text=r.recognize_google(audio,language='en_US',show_all=True)
        if text=="zero":
            txt="Say zero to read an e-mail,say one to delete an e-mail,say two to delete your all e-mails."
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            r=sr.Recognizer()
            with sr.Microphone() as source:
                audio=r.listen(source)
            text=r.recognize_google(audio,language='en_US',show_all=True)
            if text=="zero":
                txt="Say an e-mail ID:."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                r=sr.Recognizer()
                with sr.Microphone() as source:
                    audio=r.listen(source),
                text=r.recognize_google(audio,language='en_US',show_all=True)
                txt=text("SELECT COUNT (*) FROM mails_inbox WHERE to_person=:A AND deleted=:B AND mail.id=:C")
                n=conn.execute(txt,A=user,B=False,C=int(text))
                if n!=0:
                    txt=text("SELECT from_person,subject,content FROM mails_inbox WHERE to_person=:A AND deleted=:B AND mail.id=:C")
                    mail=conn.execute(txt,A=user,B=False,C=int(text)).fetchone()
                    txt="From:."+mail[0]+"Subject:"+mail[1]+"Content:"+mail[2]
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")
                else:
                    txt="Invalid Choice."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")                    
            elif text=="one":
                txt="Say an e-mail ID:."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                r=sr.Recognizer()
                with sr.Microphone() as source:
                    audio=r.listen(source),
                text=r.recognize_google(audio,language='en_US',show_all=True)
                txt=text("SELECT COUNT (*) FROM mails_inbox WHERE to_person=:A AND deleted=:B AND mail.id=:C")
                n=conn.execute(txt,A=user,B=False,C=int(text))
                if n!=0:
                    txt=text("UPDATE mails_inbox SET deleted=:A WHERE mail_id=:B")
                    conn.execute(txt,A=True,B=int(text))
                    txt="The e-mail is deleted."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3"),
                else:
                    txt="Invalid Choice."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")                 
            elif text=="two":
                txt=text("UPDATE mails_inbox SET deleted=:A WHERE to_person=:B")
                conn.execute(txt,A=True,B=user)
                txt="All e-mails are moved to the deleted folder."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
            else:
                txt="Invalid choice."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")                
        elif text=="one":
            txt="Say zero to read an e-mail,say one to delete an e-mail,say two to delete your all e-mails."
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            r=sr.Recognizer()
            with sr.Microphone() as source:
                audio=r.listen(source)
            text=r.recognize_google(audio,language='en_US',show_all=True)
            if text=="zero":
                txt="Say an e-mail ID:."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                r=sr.Recognizer()
                with sr.Microphone() as source:
                    audio=r.listen(source),
                text=r.recognize_google(audio,language='en_US',show_all=True)
                txt=text("SELECT COUNT (*) FROM mails_outbox WHERE from_person=:A AND deleted=:B AND mail.id=:C")
                n=conn.execute(txt,A=user,B=False,C=int(text))
                if n!=0:
                    txt=text("SELECT to_person,subject,content FROM mails_outbox WHERE from_person=:A AND deleted=:B AND mail.id=:C")
                    mail=conn.execute(txt,A=user,B=False,C=int(text)).fetchone()
                    txt="From:."+mail[0]+"Subject:"+mail[1]+"Content:"+mail[2]
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")
                else:
                    txt="Invalid Choice."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")                    
            elif text=="one":
                txt="Say an e-mail ID:."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                r=sr.Recognizer()
                with sr.Microphone() as source:
                    audio=r.listen(source),
                text=r.recognize_google(audio,language='en_US',show_all=True)
                txt=text("SELECT COUNT (*) FROM mails_outbox WHERE from_person=:A AND deleted=:B AND mail.id==:C")
                n=conn.execute(txt,A=user,B=False,C=int(text))
                if n!=0:
                    txt=text("UPDATE mails_outbox SET deleted=:A WHERE mail_id=:B")
                    conn.execute(txt,A=True,B=int(text))
                    txt="The e-mail is deleted."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3"),
                else:
                    txt="Invalid Choice."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")                 
            elif text=="two":
                txt=text("UPDATE mails_outbox SET deleted=:A WHERE from_person=:B")
                conn.execute(txt,A=True,B=user)
                txt="All e-mails are moved to the deleted folder."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
            else:
                txt="Invalid choice."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")    
        elif text=="two":
            txt="Say zero to read an e-mail,say one to delete an e-mail,say two to delete your all e-mails."
            obj=gTTS(text=txt,lang='en',slow=True)
            obj.save("next.mp3")
            os.system("next.mp3")
            r=sr.Recognizer()
            with sr.Microphone() as source:
                audio=r.listen(source)
            text=r.recognize_google(audio,language='en_US',show_all=True)
            if text=="zero":
                txt="Say an e-mail ID:."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                r=sr.Recognizer()
                with sr.Microphone() as source:
                    audio=r.listen(source)
                text=r.recognize_google(audio,language='en_US',show_all=True)
                txt=text("SELECT COUNT (*) FROM mails_inbox WHERE to_person=:A AND deleted=:B AND mail.id=:C")
                n=conn.execute(txt,A=user,B=True,C=int(text))
                txt=text("SELECT COUNT (*) FROM mails_outbox WHERE from_person=:A AND deleted=:B AND mail.id=:C")
                m=conn.execute(txt,A=user,B=True,C=int(text))
                if n!=0:
                    txt=text("SELECT from_person,subject,content FROM mails_inbox WHERE to_person=:A AND deleted=:B AND mail.id=:C")
                    mail=conn.execute(txt,A=user,B=True,C=int(text)).fetchone()
                    txt="From:."+mail[0]+"Subject:"+mail[1]+"Content:"+mail[2]
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")
                elif m!=0:
                    txt=text("SELECT to_person,subject,content FROM mails_outbox WHERE from_person=:A AND deleted=:B AND mail.id=:C")
                    mail=conn.execute(txt,A=user,B=True,C=int(text)).fetchone()
                    txt="From:."+mail[0]+"Subject:"+mail[1]+"Content:"+mail[2]
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")
                else:
                    txt="Invalid Choice."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")                    
            elif text=="one":
                txt="Say an e-mail ID:."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
                r=sr.Recognizer()
                with sr.Microphone() as source:
                    audio=r.listen(source)
                text=r.recognize_google(audio,language='en_US',show_all=True)
                txt=text("SELECT COUNT (*) FROM mails_inbox WHERE to_person=:A AND deleted=:B AND mail.id=:C")
                n=conn.execute(txt,A=user,B=True,C=int(text))
                txt=text("SELECT COUNT (*) FROM mails_outbox WHERE from_person=:A AND deleted=:B AND mail.id=:C")
                m=conn.execute(txt,A=user,B=True,C=int(text))
                if n!=0:
                    txt=text("DELETE FROM mails_inbox WHERE mail_id=:A AND deleted=:B")
                    conn.execute(txt,A=int(text),B=True)
                    txt="Mail is completely deleted."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")
                elif m!=0:
                    txt=text("DELETE FROM mails_outbox WHERE mail_id=:A AND deleted=:B")
                    conn.execute(txt,A=int(text),B=True)
                    txt="Mail is completely deleted."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")
                else:
                    txt="Invalid Choice."
                    obj=gTTS(text=txt,lang='en',slow=True)
                    obj.save("next.mp3")
                    os.system("next.mp3")                         
            elif text=="two":
                txt=text("DELETE FROM mails_inbox WHERE to_person=:A")
                conn.execute(txt,A=user)
                txt=text("DELETE FROM mails_outbox WHERE from_person=:A")
                conn.execute(txt,A=user)
                txt="All e-mails are moved to the deleted folder."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
            else:
                txt="Invalid choice."
                obj=gTTS(text=txt,lang='en',slow=True)
                obj.save("next.mp3")
                os.system("next.mp3")
        return redirect(url_for('page_for_visually_impaired_mail_actions',user=user))
    elif action=="two":
        return redirect(url_for('page_for_visually_impaired_user_actions'))
    else:
        txt="Invalid choice."
        obj=gTTS(text=txt,lang='en',slow=True)
        obj.save("next.mp3")
        os.system("next.mp3")
        return redirect(url_for('page_for_visually_impaired_mail_actions',user=user))
    return render_template('page_for_visually_impaired_mail_actions.html')
if __name__=='__main__':
    app.run(debug=True)
