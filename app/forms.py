from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField,PasswordField,SubmitField,SelectField,IntegerField,DateField
from wtforms.validators import DataRequired,Required,NumberRange,Regexp,Length,ValidationError,Optional

class LoginForm(FlaskForm):
    username = StringField(label="Username",validators=[DataRequired()])
    password = PasswordField(label="Password",validators=[DataRequired()])
    submit = SubmitField(label="Login")

beds = [('None','None'),('General','general'),('Semi Sharing','semi sharing'),('Single','single')]
class AddPatient(FlaskForm):
    patientID = StringField(label="Patient ID(SSN ID)",validators=[DataRequired(),Regexp('^\\d{9}$',message="required 9 digit ID")])
    name = StringField(label="Name",validators=[DataRequired(),Length(min=3)])
    age = IntegerField(label="Age",validators=[DataRequired(),NumberRange(min=10,max=100)])
    typeOfBed = SelectField(label="Bed Type",choices=beds,validators=[Required()])
    addressline1 = StringField('Address Line 1*',validators=[DataRequired(), Length(min=1, max=100)])
    addressline2 = StringField('Address Line 2',validators=[Length(max=100)])
    city = StringField('City',validators=[DataRequired()])
    state = StringField('State',validators=[DataRequired()])
    submit = SubmitField(label="Create")
    def validate_typeOfBed(self,field):
        if self.typeOfBed.data == "None":
            raise ValidationError("Please select bed type!")

class ViewPatient(FlaskForm):
    patientID = StringField(label="Patient ID(SSN ID)",validators=[DataRequired(),Regexp('^\\d{9}$',message="required 9 digit ID")])
    submit = SubmitField(label="View")
