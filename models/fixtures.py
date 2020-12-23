from app import db


class Fixture(db.Model):
    __tablename__ = 'fixture'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100, collation='utf8_general_ci'), nullable=False)
    type = db.Column(db.String(50, collation='utf8_general_ci'), nullable=False)
    description = db.Column(db.String(250, collation='utf8_general_ci'), nullable=False)
    size = db.Column(db.String(50, collation='utf8_general_ci'), nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)

    def __repr__(self):
        return 'Id: {}'.format(self.id)

