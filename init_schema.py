import os
from app import create_app, db
from app.models import User, Settings, Category, Product
from werkzeug.security import generate_password_hash

app = create_app()

instance_path = os.path.join(app.root_path, 'instance')
os.makedirs(instance_path, exist_ok=True)

with app.app_context():
    db.create_all()

    # 默认管理员账号
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123')
        )
        db.session.add(admin_user)

    # 默认网站设置 + SEO 配置
    if Settings.query.count() == 0:
        default_settings = Settings(
            company_name='XX Hotel Furniture Manufacturer',
            theme='light',

            # Homepage SEO
            seo_home_title='Home - Premium Hotel Furniture | {company_name}',
            seo_home_description='Professional hotel furniture manufacturer specializing in luxury beds, sofas, wardrobes and custom solutions for 5-star hotels worldwide.',
            seo_home_keywords='hotel furniture, luxury hotel beds, hotel sofas, custom hospitality furniture, hotel room furniture',

            # Products Page SEO
            seo_products_title='Hotel Furniture Products | Beds, Sofas, Wardrobes - {company_name}',
            seo_products_description='Explore our complete collection of premium hotel furniture including beds, nightstands, sofas, wardrobes and custom case goods for luxury hospitality projects.',
            seo_products_keywords='hotel furniture products, hotel beds, hotel sofas, hotel wardrobes, luxury hotel furniture collection',

            # About Page SEO
            seo_about_title='About Us - {company_name} | Leading Hotel Furniture Manufacturer',
            seo_about_description='Learn about {company_name}, a professional hotel furniture manufacturer with years of experience in custom hospitality furniture design and production.',

            # Contact Page SEO
            seo_contact_title='Contact Us - {company_name} | Hotel Furniture Inquiry',
            seo_contact_description='Contact {company_name} for custom hotel furniture solutions, quotes, and partnership opportunities.'
        )
        db.session.add(default_settings)

    # 酒店家具英文分类（Loose + Fixed）
    if Category.query.count() == 0:
        loose_cats = [
            "Beds",
            "Nightstands/Bedside Tables",
            "Sofas and Armchairs",
            "Coffee Tables/Tea Tables",
            "Lounge Chairs/Ottomans",
            "Desk Chairs/Writing Chairs",
            "Dining Chairs",
            "Luggage Racks/Benches",
            "Side Tables/End Tables",
            "Accent Chairs"
        ]

        fixed_cats = [
            "Headboards",
            "Wardrobes/Closets/Armoires",
            "Built-in Desks/Writing Tables",
            "TV Cabinets/Entertainment Units",
            "Dressers/Chests of Drawers",
            "Vanities/Bathroom Cabinets",
            "Built-in Minibars",
            "Wall Panels/Decorative Paneling",
            "Fixed Shelving/Storage Units",
            "Console Tables (wall-fixed)"
        ]

        all_cats = loose_cats + fixed_cats
        for cat_name in all_cats:
            db.session.add(Category(name=cat_name))

        # 示例产品（包含座高、基材、覆面、适用空间、精选系列）
        prod1 = Product(
            name="King Size Hotel Bed",
            description="Luxury 5-star hotel standard bed with premium support",
            image="bed_king.jpg",
            length=2000, width=1800, height=800,
            seat_height=None,
            base_material="Solid Wood",
            surface_material="Fabric",
            featured_series="Modern Hotel Series,Luxury Classic Series",
            applicable_space="Guest Room, Suite",
            category=Category.query.filter_by(name="Beds").first()
        )
        prod2 = Product(
            name="Built-in Wardrobe with Sliding Doors",
            description="Large capacity storage with full-length mirror",
            image="wardrobe_builtin.jpg",
            length=2400, width=600, height=2400,
            seat_height=None,
            base_material="Engineered Wood",
            surface_material="Lacquer Finish",
            featured_series="Modern Hotel Series",
            applicable_space="Guest Room",
            category=Category.query.filter_by(name="Wardrobes/Closets/Armoires").first()
        )
        prod3 = Product(
            name="Hotel Writing Desk",
            description="Multi-functional desk with drawers",
            image="desk_hotel.jpg",
            length=1200, width=600, height=750,
            seat_height=None,
            base_material="Solid Wood",
            surface_material="Lacquer Finish",
            featured_series="Modern Hotel Series",
            applicable_space="Guest Room",
            category=Category.query.filter_by(name="Built-in Desks/Writing Tables").first()
        )
        prod4 = Product(
            name="Three-Seater Fabric Sofa",
            description="Comfortable and durable for hotel lobby",
            image="sofa_fabric.jpg",
            length=2200, width=900, height=850,
            seat_height=450,
            base_material="Metal + Solid Wood",
            surface_material="Fabric",
            featured_series="Luxury Classic Series",
            applicable_space="Lobby, Lounge",
            category=Category.query.filter_by(name="Sofas and Armchairs").first()
        )
        prod5 = Product(
            name="TV Cabinet with Minibar",
            description="Integrated minibar and storage",
            image="tv_cabinet.jpg",
            length=1800, width=450, height=600,
            seat_height=None,
            base_material="Engineered Wood",
            surface_material="Lacquer Finish",
            featured_series="Modern Hotel Series",
            applicable_space="Guest Room",
            category=Category.query.filter_by(name="TV Cabinets/Entertainment Units").first()
        )

        db.session.add_all([prod1, prod2, prod3, prod4, prod5])

    db.session.commit()
    print("Database initialization complete! English hotel furniture theme with SEO settings applied.")
    print("Admin account: admin / admin123")