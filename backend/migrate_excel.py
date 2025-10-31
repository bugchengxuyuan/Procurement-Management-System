"""
Excel Data Migration Script

This script migrates data from the Excel file to the database.
"""
import pandas as pd
from datetime import datetime
from database import SessionLocal, init_db
from models.order import PurchaseOrder
from models.product import Product
from utils.excel import read_excel_file, parse_order_data


def migrate_excel_to_database(excel_path: str):
    """
    Migrate Excel data to database

    Args:
        excel_path: Path to Excel file
    """
    print(f"Starting migration from {excel_path}...")

    # Initialize database
    init_db()
    db = SessionLocal()

    try:
        # Read Excel file
        print("Reading Excel file...")
        with open(excel_path, 'rb') as f:
            content = f.read()

        # Read Excel with correct sheet name and skip rows
        import pandas as pd
        df = pd.read_excel(excel_path, sheet_name="CAISHENDAO", header=None)

        # Extract the data columns (columns 10-16) starting from row 7
        df_data = df.iloc[7:, 10:17].copy()
        df_data.columns = ['日期', '初始状态', '订单编号', '产品名称', '采购金额', '时间', '先采后付']

        print(f"Found {len(df_data)} rows in Excel")

        # Parse order data
        print("Parsing order data...")
        orders, errors = parse_order_data(df_data)
        print(f"Successfully parsed {len(orders)} orders")

        if errors:
            print(f"Found {len(errors)} parsing errors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - Row {error.get('row', 'Unknown')}: {error.get('error', 'Unknown error')}")

        # Import orders
        print("\nImporting orders to database...")
        success_count = 0
        error_count = 0
        seen_order_nos = set()

        for idx, order_data in enumerate(orders, 1):
            try:
                # Check if order already exists in this batch
                if order_data["order_no"] in seen_order_nos:
                    error_count += 1
                    continue

                # Check if order already exists in database
                existing_order = db.query(PurchaseOrder).filter(
                    PurchaseOrder.order_no == order_data["order_no"]
                ).first()

                if existing_order:
                    error_count += 1
                    continue

                seen_order_nos.add(order_data["order_no"])

                # Create order
                order = PurchaseOrder(
                    order_no=order_data["order_no"],
                    product_name=order_data["product_name"],
                    purchase_amount=order_data["purchase_amount"],
                    order_date=order_data["order_date"],
                    order_status=order_data["order_status"],
                    payment_method=order_data["payment_method"],
                    record_time=order_data["record_time"],
                )

                db.add(order)
                success_count += 1

                # Commit every 100 orders
                if idx % 100 == 0:
                    db.commit()
                    print(f"  Imported {idx} orders...")

            except Exception as e:
                print(f"  Error importing order {order_data.get('order_no', 'Unknown')}: {str(e)}")
                error_count += 1
                db.rollback()

        # Final commit
        db.commit()

        print(f"\nImport completed!")
        print(f"  Success: {success_count}")
        print(f"  Errors: {error_count}")

        # Update product stats
        print("\nUpdating product statistics...")
        update_all_product_stats(db)

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"\nMigration failed: {str(e)}")
        db.rollback()
        raise

    finally:
        db.close()


def update_all_product_stats(db):
    """
    Update statistics for all products
    """
    # Get all unique product names
    products = db.query(PurchaseOrder.product_name).distinct().all()

    for (product_name,) in products:
        # Calculate stats
        stats = db.query(
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.count(PurchaseOrder.id).label("total_count"),
            func.avg(PurchaseOrder.purchase_amount).label("avg_price"),
            func.max(PurchaseOrder.order_date).label("last_date"),
        ).filter(PurchaseOrder.product_name == product_name).first()

        # Get or create product
        product = db.query(Product).filter(Product.product_name == product_name).first()

        if not product:
            product = Product(product_name=product_name)
            db.add(product)

        # Update stats
        product.total_purchase_amount = float(stats.total_amount) if stats.total_amount else 0
        product.total_order_count = stats.total_count if stats.total_count else 0
        product.avg_unit_price = float(stats.avg_price) if stats.avg_price else 0
        product.last_purchase_date = stats.last_date

    db.commit()
    print(f"Updated statistics for {len(products)} products")


if __name__ == "__main__":
    from sqlalchemy import func

    # Path to Excel file
    EXCEL_PATH = "../采购表-2（最新版.xlsx"

    migrate_excel_to_database(EXCEL_PATH)
