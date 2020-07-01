from app import app,mongo
from flask import render_template,redirect,url_for,flash,session,request
import json
from app.forms import LoginForm,AddPatient,ViewPatient
from datetime import datetime


user = mongo.db['user']
patient = mongo.db['patient']

@app.route('/')
@app.route('/index')
def index():
    if not session.get("username"):
        return redirect('/login')
    return render_template("index.html",index=True)

@app.route('/login',methods=['GET','POST'])
def login():
    if session.get("username"):
        return redirect("/index")
    form = LoginForm()
    if form.validate_on_submit():
        userData = user.find_one({"username":form.username.data})
        if userData and userData['password'] == form.password.data:
            flash(f"{userData['username']},you are successfully logged in!","success")
            session['username'] = userData['username']
            return redirect("/index")
        else:
            flash("sorry try again!","danger")
    return render_template("login.html",login=True,title="Login",form=form)  

@app.route('/addPatient',methods=['GET','POST'])
def addPatient(pid=None):
    if not session.get("username"):
        return redirect("/login")
    form = AddPatient()
    if form.validate_on_submit():
        onePatientData = patient.find_one({"patient_id":form.patientID.data})
        if not onePatientData:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            patient.insert_one({"patient_id":form.patientID.data,"name":form.name.data,"age":form.age.data,"addressline1":form.addressline1.data,
            "addressline2":form.addressline2.data,"city":form.city.data,"state":form.state.data,"date":dt_string,"typeOfBed":form.typeOfBed.data})
            flash(f"{form.name.data} successfully admitted!","success")
        else:
            flash(f"patient already fount!","danger")
    return render_template("addPatient.html",addPatient=True,form=form,pid=pid)  

@app.route('/editPatient/<pid>',methods=['GET','POST'])
def editPatient(pid=None):
    if not session.get("username"):
        return redirect("/login")
    patientData = patient.find_one({"patient_id":pid}) 
    form = AddPatient(**patientData,patientID=patientData['patient_id'])
    if form.validate_on_submit():
        patient.update_one({"patient_id":form.patientID.data},{"$set":{"name":form.name.data,"age":form.age.data,"addressline1":form.addressline1.data,
        "addressline2":form.addressline2.data,"city":form.city.data,"state":form.state.data,"typeOfBed":form.typeOfBed.data}})
        flash(f"{form.name.data} successfully updated!","success")
        return redirect('/viewPatient')
    return render_template("addPatient.html",addPatient=True,form=form,pid=pid)  

@app.route('/dischargePatient',methods=['GET','POST'])
def dischargePatient():
    if not session.get("username"):
        return redirect("/login")
    pid = request.form.get('pid')
    if pid:
        patientData = patient.find_one({"patient_id":pid})
        if patientData:
            patient.delete_one({"patient_id":pid})
            flash(f"{patientData['name']} successfully discharge!","danger")
            return redirect('/viewAllPatient')
    return render_template("dischargePatient.html",dischargePatient=True)  


@app.route('/viewAllPatient',methods=['GET','POST'])
@app.route('/viewAllPatient/<delete>',methods=['GET','POST'])
def viewAllPatient(delete=None):
    if not session.get("username"):
        return redirect("/login")
    pid = request.args.get('search')
    if pid:
        patientData = patient.find({"patient_id":pid})
        if patientData.count() == 0:
            flash("Patient does not exist!","danger")
            return redirect('viewAllPatient')
    else:
        patientData = patient.find()

    return render_template("viewAllPatient.html",viewAllPatient=True,patientData=patientData,delete=delete)  



# @app.route('/searchPatient',methods=['GET','POST'])
# def searchPatient():
#     if not session.get("username"):
#         return redirect("/login")
#     pid = request.form.get('search')
#     patientData = patient.find_one({"patient_id":form.patientID.data})
#     if patientData:
#         return redirect(url_for('editPatient',pid=form.patientID.data))
#     else:
#         flash(f"patient not fount!","danger")
#     return render_template("searchPatient.html",searchPatient=True,form=form)  
    

@app.route('/viewPatient',methods=['GET','POST'])
def viewPatient():
    if not session.get("username"):
        return redirect("/login")
    form = ViewPatient()
    if form.validate_on_submit():
        patientData = patient.find_one({"patient_id":form.patientID.data})
        if patientData:
           return redirect(url_for('editPatient',pid=form.patientID.data))
        else:
            flash(f"patient not fount!","danger")
    return render_template("viewPatient.html",viewPatient=True,form=form)  
    