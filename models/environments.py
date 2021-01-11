from app import db
import enum

class EnvironmentType(enum.Enum):
    classroom = 'classroom'
    laboratory = 'laboratory'
    congress_center = 'congress_center'
    meeting_room = 'meeting_room'


class Environment(db.Model):
    __tablename__ = 'environment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100, collation='utf8_general_ci'), nullable=False)
    location = db.Column(db.String(100, collation='utf8_general_ci'), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50, collation='utf8_general_ci'), nullable=False)

    fixtures = db.relationship('Fixture', backref='environment', lazy=True)
    admins = db.relationship('EnvironmentAdmin', backref='environment', lazy=True)
    appointments = db.relationship('Appointment', backref='environment', lazy=True)
    working_hours = db.relationship('EnvironmentWorkingHour', backref='environment', lazy=True)

    def __repr__(self):
        return 'Id: {}'.format(self.id)


class EnvironmentAdmin(db.Model):
    __tablename__ = 'environment_admin'

    id = db.Column(db.Integer, primary_key=True)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

    def __repr__(self):
        return 'Id: {}'.format(self.id)


class EnvironmentWorkingHour(db.Model):
    __tablename__ = 'environment_working_hour'

    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)

    def __repr__(self):
        return 'Id: {}'.format(self.id)
