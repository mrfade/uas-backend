from app import db


class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(1000, collation='utf8_general_ci'), nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_accepted = Column(Boolean, unique=False, default=False)

    def __repr__(self):
        return 'Id: {}'.format(self.id)
