import sqlite3

class InventoryManager:
    def __init__(self):
        # 创建或连接到库存数据库
        self.conn = sqlite3.connect('inventory.db')
        self.c = self.conn.cursor()

        # 创建商品表
        self.c.execute('''CREATE TABLE IF NOT EXISTS products
                     (product_id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER,  ID INTEGER, safe_inventory INTEGER)''')
        # self.c.execute('''DROP TABLE IF EXISTS products''')
    def add_product(self, name, quantity, ID, safe_inventory):
        """添加商品"""
        self.c.execute("INSERT INTO products (name, quantity, ID, safe_inventory) VALUES (?, ?, ?, ?)", (name, quantity, ID, safe_inventory))
        self.conn.commit()

    def update_product(self, product_id, quantity):
        """更新商品数量"""
        self.c.execute("UPDATE products SET quantity = ? WHERE product_id = ?", (quantity, product_id))
        self.conn.commit()

    def delete_product(self, product_id):
        """删除商品"""
        self.c.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        self.conn.commit()

    def list_products(self):
        """列出所有商品"""
        self.c.execute("SELECT * FROM products")
        return self.c.fetchall()

    def close(self):
        """关闭数据库连接"""
        self.conn.close()

# 示例用法
if __name__ == "__main__":
    manager = InventoryManager()

    # 添加商品
    manager.add_product("大众自动钳", 101, 1, 41)
    manager.add_product("壳体2", 102, 2, 42)
    manager.add_product("支架1", 103, 3, 43)
    manager.add_product("配件", 104, 4, 44)
    manager.add_product("左壳体1", 105,  5, 45)
    manager.add_product("右壳体1", 106,  6, 46)
    manager.add_product("密封圈2", 107, 7, 47)
    manager.add_product("活塞1", 108, 8, 48)
    manager.add_product("塑料套1", 109,  9, 49)
    manager.add_product("橡胶套1", 110,  10, 50)
    manager.add_product("放气螺栓1", 111, 11, 51)
    manager.add_product("防尘帽1", 112, 12, 52)
    manager.add_product("内六角螺栓1", 113, 13, 53)
    manager.add_product("摩擦片2", 114,  14, 54)
    manager.add_product("隔垫1", 115,  15, 55)
    manager.add_product("开口导向套管2", 116, 16, 56)

    # 列出所有商品
    print(manager.list_products())

    # # 更新商品
    # manager.update_product(1, 110)

    # # 列出所有商品
    # print(manager.list_products())

    # # 删除商品
    # manager.delete_product(2)

    # # 列出所有商品
    # print(manager.list_products())

    manager.close()