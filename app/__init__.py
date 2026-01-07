from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'  # 未登录跳转到登录页
login_manager.login_message = '请先登录后台管理系统'
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-very-secret-key-change-me'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 注册蓝图
    from app.routes.main import main_bp
    from app.routes.products import products_bp
    from app.routes.featured import featured_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(featured_bp, url_prefix='/featured')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app