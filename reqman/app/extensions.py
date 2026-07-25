from flask_appbuilder import AppBuilder
from flask_appbuilder.utils.legacy import get_sqla_class

from .views import DashboardIndexView

# Initialize the SQLAlchemy database helper
db = get_sqla_class()()

# Initialize AppBuilder with custom IndexView
appbuilder = AppBuilder(indexview=DashboardIndexView())
