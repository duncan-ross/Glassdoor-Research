from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from glassdoor import app, db
from models import Companies, Reviews, CompanyReviews, CompanyFinancials
import os
import code

# app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
