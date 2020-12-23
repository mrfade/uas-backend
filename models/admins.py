from app import db


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20, collation='utf8_general_ci'), nullable=False)
    last_name = db.Column(db.String(20, collation='utf8_general_ci'), nullable=False)
    password = db.Column(db.String(100, collation='utf8_general_ci'), nullable=False)
    email = db.Column(db.String(100, collation='utf8_general_ci'), unique=True, nullable=False)
    tc_number = db.Column(db.String(11, collation='utf8_general_ci'), nullable=False)

    environments = db.relationship('EnvironmentAdmin', backref='admin', lazy=True)

    def __repr__(self):
        return 'Id: {}, name: {}'.format(self.id, self.first_name)
