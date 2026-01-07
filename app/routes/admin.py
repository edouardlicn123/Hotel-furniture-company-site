from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Product, Category, User, Settings
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import os

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin.index'))
        flash('用户名或密码错误', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        settings.company_name = request.form.get('company_name', '').strip()
        settings.theme = request.form.get('theme', 'light')
        
        # 保存所有 SEO 字段
        settings.seo_home_title = request.form.get('seo_home_title', '')
        settings.seo_home_description = request.form.get('seo_home_description', '')
        settings.seo_home_keywords = request.form.get('seo_home_keywords', '')
        
        settings.seo_products_title = request.form.get('seo_products_title', '')
        settings.seo_products_description = request.form.get('seo_products_description', '')
        settings.seo_products_keywords = request.form.get('seo_products_keywords', '')
        
        settings.seo_about_title = request.form.get('seo_about_title', '')
        settings.seo_about_description = request.form.get('seo_about_description', '')
        
        settings.seo_contact_title = request.form.get('seo_contact_title', '')
        settings.seo_contact_description = request.form.get('seo_contact_description', '')
        
        db.session.commit()
        flash('所有设置保存成功！', 'success')
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/products')
@login_required
def product_list():
    products = Product.query.all()
    return render_template('admin/product_list.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def product_add():
    categories = Category.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        
        length = request.form.get('length')
        width = request.form.get('width')
        height = request.form.get('height')
        seat_height = request.form.get('seat_height')
        base_material = request.form.get('base_material')
        surface_material = request.form.get('surface_material')
        applicable_space = request.form.get('applicable_space')
        featured_series = request.form.get('featured_series')
        
        # 多图上传处理（最多10张）
        upload_folder = os.path.join('app', 'static', 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True)
        
        photos_list = []
        image_files = request.files.getlist('photos')  # name="photos"
        
        for file in image_files[:10]:
            if file and file.filename != '':
                filename = file.filename
                file.save(os.path.join(upload_folder, filename))
                photos_list.append(filename)
        
        photos_str = ','.join(photos_list) if photos_list else None
        main_image = photos_list[0] if photos_list else None
        
        new_product = Product(
            name=name,
            description=description,
            image=main_image,
            photos=photos_str,
            length=int(length) if length else None,
            width=int(width) if width else None,
            height=int(height) if height else None,
            seat_height=int(seat_height) if seat_height else None,
            base_material=base_material,
            surface_material=surface_material,
            applicable_space=applicable_space,
            featured_series=featured_series,
            category_id=category_id or None
        )
        db.session.add(new_product)
        db.session.commit()
        flash(f'产品添加成功！已上传 {len(photos_list)} 张图片', 'success')
        return redirect(url_for('admin.product_list'))
    
    return render_template('admin/product_add.html', categories=categories)

@admin_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password, old_password):
            flash('旧密码不正确', 'danger')
            return redirect(url_for('admin.change_password'))

        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'danger')
            return redirect(url_for('admin.change_password'))

        if len(new_password) < 6:
            flash('新密码至少需要6位字符', 'danger')
            return redirect(url_for('admin.change_password'))

        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('密码修改成功！请重新登录', 'success')
        logout_user()
        return redirect(url_for('admin.login'))

    return render_template('admin/change_password.html')