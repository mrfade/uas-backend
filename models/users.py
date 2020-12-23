from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20, collation='utf8_general_ci'), nullable=False)
    last_name = db.Column(db.String(20, collation='utf8_general_ci'), nullable=False)
    password = db.Column(db.String(100, collation='utf8_general_ci'), nullable=False)
    email = db.Column(db.String(100, collation='utf8_general_ci'), unique=True, nullable=False)
    tc_number = db.Column(db.String(11, collation='utf8_general_ci'), nullable=False)
    phone = db.Column(db.String(20, collation='utf8_general_ci'), nullable=False)
    type = db.Column(db.String(10, collation='utf8_general_ci'), default='guest', nullable=False)

    user_student = db.relationship('UserStudent', backref='user', lazy=True, uselist=False)
    user_staff = db.relationship('UserStaff', backref='user', lazy=True, uselist=False)
    user_appointment = db.relationship('Appointment', backref='user', lazy=True, uselist=False)

    def __repr__(self):
        return 'Id: {}, name: {}'.format(self.id, self.first_name)

class UserStudent(db.Model):
    __tablename__ = 'user_student'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    student_id = db.Column(db.String(12, collation='utf8_general_ci'), unique=True, nullable=False)

    def __repr__(self):
        return 'Id: {}'.format(self.id)

class UserStaff(db.Model):
    __tablename__ = 'user_staff'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    staff_id = db.Column(db.String(12, collation='utf8_general_ci'), unique=True, nullable=False)

    def __repr__(self):
        return 'Id: {}'.format(self.id)
