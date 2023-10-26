import sys
import os
sys.path.append(os.path.abspath("../../xt/code"))
from xt_sql import XTDataBase
sys.path.append(os.path.abspath("../../xs"))
from xs_sql import XSDataBase
sys.path.append(os.path.abspath("../../kc"))
from inventory import InventoryManager
sys.path.append(os.path.abspath("../../cg"))
from cg_database import cg_database_entity

import sqlite3 as sql

from datetime import date, datetime, timedelta

class JHDataBase:
    def __init__(self, file_path):
        self.connection = sql.connect(file_path)
        self.file_path = file_path

    def MPS_table(self, name):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS {}(
            product_id INTEGER PRIMARY KEY,
            planned_amount INTEGER NOT NULL,
            planned_deadline DATE
        );
        '''.format(name))
        self.connection.commit()

    def MRP_table(self, name):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS {}(
            product_id INTEGER PRIMARY KEY,
            planned_amount INTEGER NOT NULL,
            planned_deadline TIME
        );
        '''.format(name))
        self.connection.commit()

    def chejiancaigou_table(self, name):
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS {} (
            caigoupin_id INTEGER PRIMARY KEY,
            caigou_amount INTEGER NOT NULL,
            ddl_time INTEGER
        );
        """.format(name))
        self.connection.commit()

    def chejianzuoye_table(self, name):
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS {} (
            chejian_id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            product_amount INTEGER NOT NULL,
            ddl_time INTERGER
        );
        """.format(name))
        self.connection.commit()

    def paigong_table(self, name):
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS {} (
            work_id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            work_request varchar(30) NOT NULL,
            work_time INTEGER
        );
        """.format(name))
        self.connection.commit()

    def lingliao_table(self, name):
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS {} (
            work_id INTEGER PRIMARY KEY,
            goods_id INTEGER NOT NULL,
            goods_amount INTEGER NOT NULL,
            needed_time INTEGER NOT NULL
        );
        """.format(name))
        self.connection.commit()

    def insert_table(self, table_name, col_name: list, values: list):

        cursor = self.connection.cursor()
        cmd = f"INSERT INTO {table_name} (" + ",".join(col_name) + \
              f") VALUES ("
        for i in range(len(values)):
            cmd += f"'{values[i]}',"
        cmd = cmd[:-1]+");"
        # print(cmd)
        cursor.execute(cmd)
        self.connection.commit()

    def find_info(self, table_name, args):
        cursor = self.connection.cursor()
        cmd = None
        # print(args)
        if not len(args):
            cmd = "SELECT * FROM {};".format(table_name)
            # print(cmd)
            cursor.execute(cmd)
            # print(" | ".join(self.params))
        else:
            cmd = "SELECT " + ", ".join(args) + " FROM {};".format(table_name)
            # print(cmd)
            cursor.execute(cmd)
            # print(" | ".join(args))
        result = []
        for each in cursor:
            result.append(each)
            # each = [str(i) for i in each ]
            # print(" | ".join(each))
        return result

    def sql_cmd(self, cmd):
        cursor = self.connection.cursor()
        cursor.execute(cmd)
        self.connection.commit()
        result = []
        for each in cursor:
            result.append(each)
            # print(each)
        return result

    def where(self, table_name, col, **dicts):
        cursor = self.connection.cursor()
        cmd = None
        # print(args)
        if not len(col):
            cmd = "SELECT * FROM {} WHERE ".format(table_name)
            for k,v in dicts.items():
                cmd += "{} = '{}' ".format(k,v)
            # print(cmd)
            cursor.execute(cmd)
            # print(" | ".join(self.params))
        else:
            cmd = "SELECT " + ", ".join(col) + " FROM {} WHERE ".format(table_name)
            for k,v in dicts.items():
                cmd += "{} = '{}' ".format(k,v)
            # print(cmd)
            cursor.execute(cmd)
            # print(" | ".join(col))
        result = []
        for each in cursor:
            result.append(each)
            # each = [str(i) for i in each]
            # print(" | ".join(each))
        return result

    def delete(self, table_name, **kwargs):
        cursor = self.connection.cursor()
        cmd = "DELETE FROM {} WHERE ".format(table_name)
        for k,v in kwargs.items():
            cmd += "{} = '{}' ".format(k,v)
        # print(cmd)
        cursor.execute(cmd[:-1])
        self.connection.commit()

    def update(self, table_name, dicts, **condition):
        cursor = self.connection.cursor()
        cmd = None
        # print(args)
        if len(condition):
            cmd = "UPDATE {} SET ".format(table_name)
            for k, v in dicts.items():
                if type(v) == str:
                    cmd += "{} = '{}',".format(k, v)
                else:
                    cmd += "{} = {},".format(k, v)
            cmd = cmd[:-1] + " WHERE "
            for k, v in condition.items():
                cmd += "{} = '{}'".format(k, v)
            # print(cmd)
            cursor.execute(cmd)
            # print(" | ".join(self.params))
        else:
            cmd = "UPDATE {} SET ".format(table_name)
            for k, v in dicts.items():
                cmd += "{} = '{}',".format(k, v)
            # print(cmd)
            cursor.execute(cmd[:-1])
            # print(" | ".join(col))

    def close(self):
        self.connection.commit()
        self.connection.close()

    def MPS_insert(self):
        MPS = self.find_info("MPS_table", [])
        for i in range(len(MPS)):
            db.delete("MPS_table", product_id=i+1)
        db1 = XTDataBase("../../test.db")
        BOM1 = db1.where("xt_bom_大众自动钳BOM", ["ID"], LAYER=1)
        for i in range(len(BOM1)):
            self.insert_table("MPS_table", ["product_id", "planned_amount", "planned_deadline"],
                              [BOM1[i][0], 1000, date(2024, 12, 31)])

    def MRP_calculate(self):
        MPS = self.find_info("MPS_table", [])
        MRP = self.find_info("MRP_table", [])
        for i in range(len(MRP)):
            db.delete("MRP_table", product_id=i+1)

        for i in range(len(MPS)):
            MPS_amount = self.where("MPS_table", ["planned_amount"], product_id=i+1)
            if MPS_amount != []:
                MRP_amount = MPS_amount[0][0]/12
                self.insert_table("MRP_table", ["product_id", "planned_amount", "planned_deadline"],
                                  [i + 1, MRP_amount, date(2024, 1, 31)])

        # 计算物料需求量
        # 毛需求 = 独立需求 + 相关需求
        # 计划库存量 = 上期库存量 + 本期订单产出量 + 本期预计入库量 - 毛需求量
        # 净需求量 = 本期毛需求量 - 上期库存量 - 本期预计入库量 + 安全库存量

        db1 = XTDataBase("../../test.db")
        BOM1 = db1.sql_cmd("SELECT ID, parent FROM xt_bom_大众自动钳BOM WHERE LAYER >= 2")
        conn1 = sql.connect(os.path.join("../../cg/cg_db", "Purchase Detail.db"), check_same_thread=False)
        cursor1 = conn1.cursor()
        conn2 = sql.connect(os.path.join("../../kc", "inventory.db"), check_same_thread=False)
        cursor2 = conn2.cursor()
        for i in range(len(BOM1)):
            cursor1.execute(f'SELECT cg_order_lot FROM cg_purchase_detail WHERE material_code={BOM1[i][0]}')  # 采购量
            cursor1.connection.commit()
            table_cg = []
            for each in cursor1:
                table_cg.append(each)
            cursor2.execute(f'SELECT quantity, safe_inventory FROM products WHERE product_id={BOM1[i][0]}') #库存，安全库存
            cursor2.connection.commit()
            table_kc = []
            for each in cursor2:
                table_kc.append(each)
            parent = db1.where("xt_bom_大众自动钳BOM", ["PARENT"], ID=BOM1[i][0])
            relevent = self.where("MRP_table", ["planned_amount", "planned_deadline"], product_id=parent[0][0]) #相关需求
            planned_amount1 = int(relevent[0][0] - table_kc[0][0] - table_kc[0][0] + table_kc[0][1])
            MRP_date = datetime.strptime(relevent[0][1], "%Y-%m-%d")
            cycle = db1.where("xt_bom_大众自动钳BOM", ["CYCLE"], ID=parent[0][0])
            MRP_ddl_date = MRP_date.date() - timedelta(weeks=cycle[0][0])
            self.insert_table("MRP_table", ["product_id", "planned_amount", "planned_deadline"],
                              [BOM1[i][0], planned_amount1, MRP_ddl_date])

    def chejianzuoye_cal(self):
        db1 = XTDataBase("../../test.db")
        BOM_zuoye = db1.where("xt_bom_大众自动钳BOM", ["ID"], BUY=0)
        for i in range(len(BOM_zuoye)):
            info = self.where("MRP_table", ["planned_amount", "planned_deadline"], product_id=BOM_zuoye[i][0])
            zuoye_ddl = datetime.strptime(info[0][1], "%Y-%m-%d")
            zuoye_ddl_date = zuoye_ddl.date()
            line = db1.where("line_xt_bom_大众自动钳BOM", ["LINE_ID"], ID=BOM_zuoye[i][0])
            chejian = db1.where("line", ["CHEJIAN"], LINE_ID=line[0][0])
            self.insert_table("zuoye_table", ["chejian_id", "product_id", "product_amount", "ddl_time"],
                              [chejian[0][0], BOM_zuoye[i][0], info[0][0], zuoye_ddl_date])


    def caigou_cal(self):
        db1 = XTDataBase("../../test.db")
        BOM_caigou = db1.where("xt_bom_大众自动钳BOM", ["ID"], BUY=1)
        for i in range(len(BOM_caigou)):
            info = self.where("MRP_table", ["planned_amount", "planned_deadline"], product_id=BOM_caigou[i][0])
            caigou_ddl = datetime.strptime(info[i][1], "%Y-%m-%d")
            caigou_ddl_date = caigou_ddl.date()
            self.insert_table("caigou_table", ["caigoupin_id", "caigou_amount", "ddl_time"],
                              [BOM_caigou[i][0], info[i][0], caigou_ddl_date])

    def paigong_cal(self):
        chejian = self.find_info("zuoye_table", ["chejian_id", "product_id", "product_amount"])
        db1 = XTDataBase("../../test.db")
        for i in range(len(chejian)):
            line = db1.where("line", ["LINE_ID"], CHEJIAN=chejian[i][0])
            work_ddl = self.where("zuoye_table", ["ddl_time"], chejian_id=chejian[i][0])
            work_place_date = datetime.strptime(work_ddl[i][0], "%Y-%m-%d")
            work_place_ddl_date = work_place_date.date()
            for j in range(len(line)):
                work_place = db1.find_info("work"+"line[i][0]", ["WC", "TIME"], WORK_ID="DESC")
                if j == 0:
                    self.insert_table("paigong_table", ["work_id", "product_id", "work_request", "work_time"],
                                      [work_place[j][0], chejian[i][1], chejian[i][2], work_place_ddl_date])
                else:
                    work_place_ddl_date -= timedelta(weeks=work_place[j-1][1])
                    self.insert_table("paigong_table", ["work_id", "product_id", "work_request", "work_time"],
                                      [work_place[j][0], chejian[i][1], chejian[i][2], work_place_ddl_date])

    def lingliao_cal(self):
        work_place = self.find_info("paigong_table", [])
        db1 = XTDataBase("../../test.db")
        for i in range(len(work_place)):
            work_place_date = datetime.strptime(work_place[i+1][3], "%Y-%m-%d")
            lingliao_ddl_date = work_place_date.date()
            lingliao_id = db1.where("xt_bom_大众自动钳BOM", ["ID"], PARENT=work_place[i][1])
            for j in range(len(lingliao_id)):
                self.insert_table("lingliao_table", ["work_id", "goods_id", "goods_request", "needed_time"],
                              [work_place[i][0], lingliao_id[j][0], work_place[i][2], lingliao_ddl_date])




if __name__ == "__main__":
    db = JHDataBase("JHdatabase.db")

    db.MPS_table("MPS_table")
    db.MRP_table("MRP_table")
    db.chejiancaigou_table("caigou_table")
    db.chejianzuoye_table("zuoye_table")
    db.paigong_table("paigong_table")
    db.lingliao_table("lingliao_table")

    # db.insert_table("MPS_table",["product_id","planned_amount","planned_deadline"],[1, 100, date(2024,12,31)])

    db.MPS_insert()
    db.MRP_calculate()
    db.chejianzuoye_cal()
    db.caigou_cal()
    # db.paigong_cal()
    # db.lingliao_cal()

    # for i in range (20):
    #     db.delete("MPS_table", product_id = i+1)
    #     db.delete("MRP_table", product_id = i+1)