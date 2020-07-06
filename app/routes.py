from app import app,mongo
from flask import render_template,redirect,url_for,flash,session,request
import json
from app.forms import LoginForm,AddPatient,ViewPatient
from datetime import datetime,timedelta


user = mongo.db['user']
patient = mongo.db['patient']
medicine = mongo.db['medicines']
issued = mongo.db['issuedMedicines']
diagno = mongo.db['diagnostic']
conducted = mongo.db['conductedDiagnostics']


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

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
            session['type'] = userData['type']
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
            issued.delete_many({"patient_id":pid})
            diagno.delete_many({"patient_id":pid})
            flash(f"{patientData['name']} successfully discharge!","danger")
            return redirect(url_for('/viewAllPatient',delete=True))
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

    
# @app.route('/patientDetail/<pid>/<issue>',methods=['GET','POST'])
@app.route('/patientDetail/<pid>/<string:view>',methods=['GET','POST'])
def patientDetail(pid=None,issue=None,diagno=None,medicineData=None,diagnostics=None,view=None):
    if not session.get("username"):
        return redirect("/login")
    patientData = patient.find_one({"patient_id":pid})
    print(view)
    if view=="issue":
        medicineData = issued.find({"patient_id":pid})
    elif view=="diagno":
        diagnostics = conducted.find({"patient_id":pid})
    return render_template("patientDetail.html",patientData=patientData,medicineData=medicineData,view=view,diagnostics=diagnostics)  

@app.route('/viewPatient',methods=['GET','POST'])
# @app.route('/viewPatient/<view>',methods=['GET','POST'])
# @app.route('/viewPatient/<diagno>',methods=['GET','POST'])
# @app.route('/viewPatient/<bill>',methods=['GET','POST'])
def viewPatient(issue=None,diagno=None,bill=None,view=None):
    if not session.get("username"):
        return redirect("/login")
    form = ViewPatient()
    view = request.args.get('view')
    if form.validate_on_submit():
        patientData = patient.find_one({"patient_id":form.patientID.data})
        if patientData:
            if view=="issue":
                return redirect(url_for('patientDetail',pid=form.patientID.data,view='issue'))
            elif view=="diagno":
                return redirect(url_for('patientDetail',pid=form.patientID.data,view='diagno'))
            elif view=="bill":
                return redirect(url_for('billing',pid=form.patientID.data))
            return redirect(url_for('editPatient',pid=form.patientID.data))
        else:
            flash(f"patient not fount!","danger")
    return render_template("viewPatient.html",viewPatient=True,form=form,view=view)  

@app.route('/issueMedicine',methods=['GET','POST'])
def issueMedicine():
    if not session.get("username"):
        return redirect("/login")
    if request.args.get('pid'):
        session['pid'] = request.args.get('pid')
    # if request.args.get('medi')
    # session.pop('medicines')
    if request.args.get('clear'):
        session.pop('medicines')
    if request.args.get('add'):
        if 'medicines' in session:
            for i in session.get('medicines'):
                data = list(issued.find({"patient_id":session.get('pid'),"name":i['name']}))
                if not data:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    issued.insert_one({"patient_id":session.get('pid'),"name":i['name'],"quantity":i['quan'],"price":i['price'],"total":i['quan']*i['price'],"date":dt_string})
                else:
                    issued.update({"patient_id":session.get('pid')},{"$inc":{"quantity":i['quan'],"total":i['quan']*i['price']}})
            flash('succesfully issued',"success")
            session.pop("medicines")
            return redirect(url_for('patientDetail',pid=session.get('pid'),view="issue"))    
        else:
            flash('cart is empty','danger')
    if 'medicines' in session:
        if request.args.get('medicine'):
            name = request.args.get('medicine').split("+")
            quan = int(request.args.get('quantity'))
            f=0
            for i in session.get('medicines'):
                if i['name'] == name[0]:
                    i['quan'] = i['quan'] + quan
                    i['total'] = i['quan']*i['price']
                    f=1
                    break
            if not f:
                session['medicines'].append({"name":name[0],"price":float(name[1]),"quan":quan,"total":float(name
                [1])*quan})
    else:
        session['medicines'] = []
    medicines = medicine.find()
    return render_template("issueMedicine.html",issueMedicine=True,medicines=medicines)  

@app.route('/diagnostic',methods=['GET','POST'])
def diagnostic():
    if not session.get("username"):
        return redirect("/login")
    if request.args.get('pid'):
        session['pid'] = request.args.get('pid')
    if request.args.get('clear'):
        session.pop('diagnostics')
    if request.args.get('add'):
        if 'diagnostics' in session:
            for i in session.get('diagnostics'):
                data = list(conducted.find({"patient_id":session.get('pid'),"name":i['name']}))
                if not data:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    conducted.insert_one({"patient_id":session.get('pid'),"name":i['name'],"amount":int(i['amount']),"conducted":1,"total":int(i['amount']),"date":dt_string})
                else:
                    conducted.update({"patient_id":session.get('pid')},{"$inc":{"conducted":1,"total":i['amount']}})
            flash('succesfully conducted',"success")
            session.pop("diagnostics")
            return redirect(url_for('patientDetail',pid=session.get('pid'),view="diagno"))    
        else:
            flash('cart is empty','danger')
    if 'diagnostics' in session:
        if request.args.get('diagno'):
            name = request.args.get('diagno')
            amount = int(request.args.get('amount'))
            f=0
            for i in session.get('diagnostics'):
                if i['name'] == name:
                    f=1
                    break
            if not f:
                session['diagnostics'].append({"name":name,"amount":amount})
    else:
        session['diagnostics'] = []
    diagnostic = [i for i in diagno.find()]
    return render_template("diagnostic.html",diagnostic=True, diagnostics=diagnostic)  

@app.route("/logout",methods=['GET','POST'])
def logout():
    if not session.get('username'):
        return redirect('/login')
    session.pop('username')
    return redirect('/login')


@app.route('/billing/<pid>',methods=['GET','POST'])
def billing(pid=None,medicines=None,diagnostics=None,patientData=None):
    if not session.get("username"):
        return redirect("/login")
    if pid:
        patientData = patient.find_one({"patient_id":pid})
        if patientData:
            medicines = issued.find({"patient_id":pid})
            diagnostics = conducted.find({"patient_id":pid})
        else:
            flash(f"patient not fount!","danger")
    return render_template("billing.html",billing=True,medicines=medicines,diagnostics=diagnostics,patientData=patientData)