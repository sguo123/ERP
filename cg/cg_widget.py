'''
命名规则：
请购单接收：Requisition Receipt
采购订单管理：Order Management
到货接收：Recieve Upon
供应商管理与评价：Supplier Management
采购业务综合查询：Comprehensive Query

TODO: 貌似很多头函数没用上，后续可能会删除或者精简一下
TODO: 检查所有文件的路径、相对路径/绝对路径、是否有同名文件、是否最新，以及文件名

TODO: 
0.完成日志功能(完成)
1.完善功能：接受请购，发送收获数据(完成)
2.供应商评价页面(功能和bug) 
3.界面美化，使用qfluetwidget库重新生成ui(完成)

FIXME: 库存模块的类传入时，路径好像有问题 LINE402 LINE403
UPDATE: 数据库文件采用绝对路径传入 line50
UPDATE: 所有图标等资源文件建议放入项目根目录下res文件夹再使用
'''

import sys
import os
import time

sys.path.append(os.path.abspath("xt/code"))
sys.path.append(os.path.abspath("kc"))
sys.path.append(os.path.abspath("jh/code"))

from PySide6.QtWidgets import (QApplication, QWidget, QComboBox,
QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QDialog,
QGroupBox, QMainWindow, QRadioButton, QGridLayout, QTableView,
QFormLayout, QStackedLayout, QScrollArea, QFileDialog, 
QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QThread, Signal, Slot, QModelIndex, QDateTime
from PySide6.QtGui import QIcon, QStandardItem, QStandardItemModel, QPixmap, QPainter, QImage, QDoubleValidator
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6 import QtCore
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from cg_database import *
from cg_ui.version3 import Ui_cg_sector
from cg_ui.dialog import Ui_cg_form
from xt_container import OperationCode, XtContainer
from inventory import InventoryManager


# 这是生成采购部门模块的类
class cg_widget(QWidget):
    # 继承父类，并执行类的方法，一些基础的设定
    def __init__(self, detail_file, list_file, receipt_file, supplier_file, user_name, xt_log):
        super().__init__()
        # 定义窗体大小
        self.resize(800, 480)
        # 执行初始化方法
        self.init_ui()
        # 设定左上角标题
        self.setWindowTitle("采购模块")

        self.detail_file = detail_file
        self.receipt_file = receipt_file
        self.list_file = list_file
        self.supplier_file = supplier_file

        # OC = OperationCode()
        self.log = XtContainer(1, xt_log, user_name)

        # 设定左上角图标，图标png文件使用绝对路径
        # icon = QIcon(os.path.abspath(icon))
        # self.setWindowIcon(icon)
        # 定义一个线程的状态
        self.thread_running = False
        self.selected_data = []

    # 一些初始化操作
    def init_ui(self):

        # 实例化Ui_cg_sector
        self.ui = Ui_cg_sector()
        self.ui.setupUi(self)

        # 现在可以直接绑定槽函数
        self.ui.tabWidget.currentChanged.connect(self.tab_changed)
        self.is_btn_receive_connected = False

    # 识别当前窗口的槽函数，并跳转到相应页面的初始化函数
    @Slot()
    def tab_changed(self, x):
        print("Current Change: ", x+1)
        match x:
            case 0:
                self.init_requisition()
            case 1:
                self.init_order()
            case 2:
                self.init_recieve()
            case 3:
                self.init_supplier()
            case 4:
                self.init_query()
            case _:
                print("Unreasonable Error!!!")

    # 1.请购单接收页面
    def init_requisition(self):
        # 直接绑定函数
        self.ui.requisition_receipt_btn.clicked.connect(self.view_requisition_list)
        self.ui.requisition_accept_btn.clicked.connect(self.accept_requisition)

    # 2.采购订单页面
    def init_order(self):
        # TODO: 设定信号，绑定函数
        self.ui.order_search.clicked.connect(self.order_table)
        self.ui.order_add.clicked.connect(self.order_add_table)
        self.ui.order_delete.clicked.connect(self.order_delete_table)
        self.ui.order_save.clicked.connect(self.order_save_table)

    # 3.到货接收页面
    # TODO: 到货接收页面
    def init_recieve(self):
        # 直接绑定槽函数
        self.ui.receive_search.clicked.connect(self.receive_table)
        self.ui.receive_add.clicked.connect(self.receive_add_table)
        self.ui.receive_delete.clicked.connect(self.receive_delete_table)
        self.ui.receive_save.clicked.connect(self.receive_save_table)
        self.ui.receive_btn.clicked.connect(self.receive_to_inver)

    # 4.供应商管理与评价页面
    def init_supplier(self):
        # 连接数据库，因为有一个下拉菜单的内容需要访问数据库
        # 设定数据库类型
        self.supplier_database = QSqlDatabase.addDatabase("QSQLITE")
        # 链接数据库，采用相对路径访问
        filename = self.supplier_file
        self.supplier_database.setDatabaseName(filename)
        # 打开数据库，顺便有一个错误处理
        if not self.supplier_database.open():
            print("Error: Could not open the database")

        # 设定信号，绑定函数
        # TODO: 写这个代码块的注释
        self.ui.supplier_choose_box.clear()
        self.supplier_query = QSqlQuery()
        self.supplier_query.exec("SELECT cg_supplier_name FROM cg_supplier_info")
        while self.supplier_query.next():
            data = self.supplier_query.value(0)
            self.ui.supplier_choose_box.addItem(data)
        self.ui.supplier_choose_box.show()

        self.ui.supplier_choose_box.currentTextChanged.connect(self.update_info)
        # self.ui.supplier_list.clicked.connect(self.supplier_table_view)
        self.ui.supplier_evaluate.clicked.connect(self.supplier_evaluation)        

    # TODO: 采购业务页面的编写
    # 5.采购业务页面
    def init_query(self):
        self.ui.query_choose_btn.clicked.connect(self.query_table)
        self.ui.query_add.clicked.connect(self.query_add_table)
        self.ui.query_delete.clicked.connect(self.query_delete_table)
        self.ui.query_save.clicked.connect(self.query_save_table)


    # 以下是各个页面初始化后需要用到的一些槽函数操作
    # 已经按页面顺序和运行的顺序排好
    # 1的槽函数：点击按钮后接收请购单的方法
    def view_requisition_list(self):
        # 设定数据库类型
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        # 链接数据库
        self.database.setDatabaseName(self.list_file)
        # 一个错误处理
        if not self.database.open():
            print("Error: Could not open the database")
        
        # TODO: 写这个代码块的注释
        # 设置tableView的模型以及表的名称
        self.model = QSqlTableModel(self, self.database)
        self.model.setTable('MPS_table')

        self.model.setHeaderData(0, Qt.Horizontal, "物料编码")
        self.model.setHeaderData(1, Qt.Horizontal, "计划订购量")
        self.model.setHeaderData(2, Qt.Horizontal, "交付最后日期")
        self.model.select()
        # 显示表格
        self.ui.requisition_table_view.setModel(self.model)
        self.ui.requisition_table_view.resizeColumnsToContents()

        # 嵌套了一个槽函数，对选择的行进行判断        
        self.selected_row = None
        self.ui.requisition_table_view.selectionModel().selectionChanged.connect(self.handle_selection_change)

        self.log.generate_log(OperationCode.CG_CHANGE)

    # TODO: 写这个代码块的注释
    # 1的槽函数：选择某行并返回索引
    # 已经在Qt Designer中设置好了每行数据只读，并且按行读，所以直接返回下标就可以
    @Slot()
    def handle_selection_change(self, selected):
        if selected.indexes():
            self.selected_data = []
            index = selected.indexes()[0]
            selected_row = selected.indexes()[0].row()
            self.selected_row = selected_row

            model = self.ui.requisition_table_view.model()

            product_id = model.data(model.index(index.row(), 0))
            planned_amount = model.data(model.index(index.row(), 1))
            planned_deadline = model.data(model.index(index.row(), 2))

            self.selected_data.append((str(product_id), str(planned_amount), str(planned_deadline)))
        
        else:
            self.selected_data = []

        del index

    # TODO: 写这个代码块的注释，以及实现子线程函数操作
    # 1的槽函数：选择某行后再点击确认按钮，就执行此操作
    # 实现交互操作：点击某行，确认，就可以将请购单中的某行内容添加到内部的采购计划表中
    @Slot()
    def accept_requisition(self):
        if self.selected_row is not None:
            print("table: ", detail_file)
            # You can now use self.selected_row to access the selected row
            print(f"Selected Row: {self.selected_row}")
            print(f"selected data is: ", self.selected_data)
            conn = sqlite3.connect(detail_file)
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(cg_purchase_detail_id) FROM cg_purchase_detail")
            max_id = cursor.fetchone()[0]
            add_requisition = cg_purchase_detail(detail_file, 'cg_purchase_detail', 'cg_purchase_detail_id')
            add_requisition.add_item(
                cg_purchase_detail_id = max_id + 1,
                material_code = self.selected_data[0][0],
                cg_order_lot = self.selected_data[0][1],
                cg_order_time = self.selected_data[0][2]
            )
        else:
            print("No row selected")

    # 2的槽函数
    def order_table(self):
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        self.database.setDatabaseName(self.detail_file)
        if not self.database.open():
            print("Error: Could not open the database")

        table_name = self.detect_table_name()
        if table_name:
            model = QSqlTableModel(self, self.database)
            model.setTable(table_name)

            model.setHeaderData(0, Qt.Horizontal, "采购明细号")
            model.setHeaderData(1, Qt.Horizontal, "物料编码")
            model.setHeaderData(2, Qt.Horizontal, "订货批量")
            model.setHeaderData(3, Qt.Horizontal, "商品总价")
            model.setHeaderData(4, Qt.Horizontal, "收货单号")
            model.setHeaderData(5, Qt.Horizontal, "预计到货时间")
            model.setHeaderData(6, Qt.Horizontal, "供应商")
            model.setHeaderData(7, Qt.Horizontal, "备注")
            model.select()
            # 显示表格
            self.ui.order_table_view.setModel(model)
            self.ui.order_table_view.resizeColumnsToContents()
        
        self.ui.order_table_view.selectionModel().selectionChanged.connect(self.order_table_changed)
        self.log.generate_log(OperationCode.CG_CHANGE)

    # 2的槽函数
    def order_add_table(self):
        print("ok")
        model = self.ui.order_table_view.model()
        model.submitAll()
        result = model.insertRows(model.rowCount(), 1)

        if not result:
            self.error_check(model)

    # 2的槽函数
    def order_delete_table(self):
        model = self.ui.order_table_view.model()
        model.removeRow(self.ui.order_table_view.currentIndex().row())
        model.submitAll()
        model.select()

    # 2的槽函数
    def order_save_table(self):
        model = self.ui.order_table_view.model()
        model.database().transaction()
        if model.submitAll():
            model.database().commit()
        else:
            model.database().rollback()

    @Slot()
    def order_table_changed(self, selected, deselected):
        validator = QDoubleValidator()
        validator.setDecimals(2)
        if selected.indexes():
            index = selected.indexes()[0]

            model = self.ui.order_table_view.model()

            detail_id = model.data(model.index(index.row(), 0))
            material_code = model.data(model.index(index.row(), 1))
            order_lot = model.data(model.index(index.row(), 2))
            total_price = model.data(model.index(index.row(), 3))
            receipt_id = model.data(model.index(index.row(), 4))
            order_time = model.data(model.index(index.row(), 5))
            order_supplier = model.data(model.index(index.row(), 6))
            remarks = model.data(model.index(index.row(), 7))
                       
            self.ui.order_total_price.setValidator(validator)
            datetime = QDateTime.fromString(order_time, "yyyy-MM-dd HH:mm:ss")

            self.ui.order_detail_id.setText(str(detail_id))
            self.ui.order_bom.setText(str(material_code))
            self.ui.order_quantity.setText(str(order_lot))
            self.ui.order_total_price.setText(str(total_price))
            self.ui.order_receipt_box.setText(str(receipt_id))
            self.ui.dateTimeEdit.setDateTime(datetime)
            self.ui.order_supplier.setText(str(order_supplier))
            self.ui.order_remarks.setText(str(remarks))
           
        else:
            self.ui.order_detail_id.clear()  
            self.ui.order_bom.clear()
            self.ui.order_quantity.clear()
            self.ui.order_total_price.clear()
            self.ui.order_receipt_box.clear()    
            self.ui.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
            self.ui.order_supplier.clear()   
            self.ui.order_remarks.clear()

    # 3的槽函数
    def receive_table(self):
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        self.database.setDatabaseName(self.receipt_file)
        if not self.database.open():
            print("Error: Could not open the database")

        table_name = self.detect_table_name()
        if table_name:
            model = QSqlTableModel(self, self.database)
            model.setTable(table_name)

            model.setHeaderData(0, Qt.Horizontal, "收货单号")
            model.setHeaderData(1, Qt.Horizontal, "物料编码")
            model.setHeaderData(2, Qt.Horizontal, "到货时间")
            model.setHeaderData(3, Qt.Horizontal, "到货量")
            model.setHeaderData(4, Qt.Horizontal, "合格品数")
            model.setHeaderData(5, Qt.Horizontal, "入库状态")
            model.setHeaderData(6, Qt.Horizontal, "备注")
            model.select()
            # 显示表格
            self.ui.receive_table_view.setModel(model)
            self.ui.receive_table_view.resizeColumnsToContents()

        self.ui.receive_table_view.selectionModel().selectionChanged.connect(self.receive_table_changed)
        self.log.generate_log(OperationCode.CG_CHANGE)

    # 3的槽函数
    def receive_add_table(self):
        print("ok")
        model = self.ui.receive_table_view.model()
        model.submitAll()
        result = model.insertRows(model.rowCount(), 1)

        if not result:
            self.error_check(model)

    # 3的槽函数
    def receive_delete_table(self):
        model = self.ui.receive_table_view.model()
        model.removeRow(self.ui.receive_table_view.currentIndex().row())
        model.submitAll()
        model.select()

    # 3的槽函数
    def receive_save_table(self):
        model = self.ui.receive_table_view.model()
        model.database().transaction()
        if model.submitAll():
            model.database().commit()
        else:
            model.database().rollback()

    @Slot()
    def receive_to_inver(self):
        row = self.index
        # if not self.is_btn_receive_connected:
        #     self.ui.receive_btn.clicked.disconnect(self.receive_to_inver)
        #     self.is_btn_receive_connected = True
        if self.ui.receive_status.isChecked():
            print("ok, the row is: ", row)
            print("the data is:", self.selected_data)

            rec_to_inv = InventoryManager()
            rec_to_inv.add_inventory(self.selected_data[0][0], self.selected_data[0][0], self.selected_data[0][0], "采购")
        else:
            print("not be chosen")

    @Slot()
    def receive_table_changed(self, selected, deselected):
        if selected.indexes():
            self.selected_data = []
            # Get the selected row's index
            index = selected.indexes()[0]
            self.index = selected.indexes()[0].row()
            
            # Assuming you have a QSqlTableModel, you can access the data in the model
            model = self.ui.receive_table_view.model()
            
            # Extract data from the model for the selected row and column
            receipt_id = model.data(model.index(index.row(), 0))
            material_code = model.data(model.index(index.row(), 1))
            arrival_time = model.data(model.index(index.row(), 2))
            arrival_quantity = model.data(model.index(index.row(), 3))
            qualified_products = model.data(model.index(index.row(), 4))
            inbound_status = model.data(model.index(index.row(), 5))
            remarks = model.data(model.index(index.row(), 6))

            datetime = QDateTime.fromString(arrival_time, "yyyy-MM-dd HH:mm:ss")
            
            # Update the QLineEdit and QTextBrowser
            self.ui.receive_id.setText(str(receipt_id))
            self.ui.receive_item.setText(str(material_code))
            self.ui.receive_time.setDateTime(datetime)
            self.ui.receive_quantity.setText(str(arrival_quantity))
            self.ui.receive_qualified.setText(str(qualified_products))
            self.ui.receive_remarks.setText(str(remarks))

            if inbound_status == 1:
                self.ui.receive_status.setChecked(True)
            else:
                self.ui.receive_status.setChecked(False)
            
            self.selected_data.append((str(arrival_time), str(material_code), str(arrival_quantity)))

        else:
            # Clear the QLineEdit and QTextBrowser if no row is selected
            self.ui.receive_id.clear()
            self.ui.receive_time.setDateTime(QDateTime.currentDateTime())
            self.ui.receive_quantity.clear()
            self.ui.receive_qualified.clear()
            self.ui.receive_remarks.clear()
            self.ui.receive_status.clear()
            self.selected_data = []

    # FIXME: 有bug，但是暂时不想改了
    # 4的槽函数：列举供应商信息
    def update_info(self):
        # 读取选取的供应商名字
        selected_supplier_name = self.ui.supplier_choose_box.currentText()
        # 相似的数据库访问操作
        supplier_query = QSqlQuery()
        supplier_query.prepare("SELECT * FROM cg_supplier_info WHERE cg_supplier_name = :supplier_name")
        supplier_query.bindValue(":supplier_name", selected_supplier_name)
        supplier_query.exec()

        # 对当前的供应商信息进行提取，从数据库取出来的数据与各控件对应
        if supplier_query.next():
            company_id = supplier_query.value(0)
            company_tel = supplier_query.value(2)
            company_address = supplier_query.value(3)
            remarks = supplier_query.value(4)

            self.ui.supplier_id.setText(f"{company_id}")
            self.ui.supplier_tel.setText(f"{company_tel}")
            self.ui.supplier_location.setText(f"{company_address}")
            self.ui.supplier_profile.setPlainText(remarks)

            # 同时，加载该供应商的logo图片，图片储存在cg_gr中
            self.load_supplier_logo(company_id)  
            self.ui.supplier_list.clicked.connect(lambda: self.supplier_table_view(company_id))
            # if self.ui.supplier_list.clicked:
            #   print("OKKKKKK!!!! This is: ", company_id)
        self.log.generate_log(OperationCode.CG_CHANGE)
    
    # TODO: 写这个代码块的注释
    # FIXME: 供应商模块还有bug
    # 4的槽函数：加载供应商的logo在控件self.supplier.logo中
    @Slot()
    def load_supplier_logo(self, company_id):
        self.ui.supplier_logo.setScene(None)

        # 从上面传过来供应商id，并且在文件夹中找到同id的png文件
        logo_path = f"cg_gr/{company_id}.png"
        logo_pixmap = QPixmap(logo_path)

        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(logo_pixmap)
        scene.addItem(item)

        self.ui.supplier_logo.setScene(scene)

        del logo_pixmap
        del scene

    def supplier_table_view(self, company_id):
        sup1 = os.path.abspath("cg/cg_db/40004001.db")
        sup2 = os.path.abspath("cg/cg_db/40004002.db")
        sup3 = os.path.abspath("cg/cg_db/40004003.db")
        sup4 = os.path.abspath("cg/cg_db/40004004.db")
        sup5 = os.path.abspath("cg/cg_db/40004005.db")
        dialog = supplier_form(company_id, sup1, sup2, sup3, sup4, sup5)
        dialog.exec()

    # TODO: 写这个代码块
    # FIXME: 调试后可以发现，是因为点击一次后线程已经在运行，点击第二次就会导致堆叠任务导致内存占用过多
    # 4的槽函数，点击后执行子线程，对该供应商进行综合评价，生成3张图标，显示在窗体中
    @Slot()
    def supplier_evaluation(self):
        if not self.thread_running:
            self.supplier_thread = supplier_eval()
            self.supplier_thread.image_generated.connect(self.supplier_diaplay_image)
            self.supplier_thread.finished.connect(self.on_thread_finished)
            self.supplier_thread.start()

            self.thread_running = True
        else:
            print(f"Evaluation is already in progress")

    # 不知道这个槽函数是否需要
    @Slot()
    def on_thread_finished(self):
        self.thread_running = False
        print("Thread finished.")


    # TODO: 写这个代码块
    # 4的槽函数，紧跟在supplier_evaluation后面，访问路径并显示图像    
    def supplier_diaplay_image(self, image_file_name):
        logo_path = image_file_name
        logo_pixmap = QPixmap(logo_path)

        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(logo_pixmap)
        scene.addItem(item)

        self.ui.supplier_graphic_1.setScene(scene)

    # 5的槽函数，点击选择文件后，弹出选择文件的对话框，进行文件的选择
    # TODO: 可能需要优化一下界面以及交互
    def query_table(self):
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        path, _ = QFileDialog.getOpenFileName(self, u"打开sqlite文件",os.getcwd(), "sqlite db(*.db)")
        if path:
            self.data_file = path
            filename = os.path.join(os.path.dirname(__file__),self.data_file)
            self.database.setDatabaseName(filename)

        if not self.database.open():
            print("Error: Could not open the database")

        table_name = self.detect_table_name()
        if table_name:
            # 设置tableView的模型以及表的名称
            model = QSqlTableModel(self, self.database)
            model.setTable(table_name)

            model.select()
            # 显示表格
            self.ui.query_list_view.setModel(model)
            self.ui.query_list_view.resizeColumnsToContents() 
        self.log.generate_log(OperationCode.CG_CHANGE)

    def detect_table_name(self):
        tables = self.database.tables()
        if tables:
            return tables[0]
        else:
            print("No such tables.")
            return None

    def query_add_table(self):
        print("ok")
        model = self.ui.query_list_view.model()
        model.submitAll()
        result = model.insertRows(model.rowCount(), 1)

        if not result:
            self.error_check(model)

    def query_delete_table(self):
        model = self.ui.query_list_view.model()
        model.removeRow(self.ui.query_list_view.currentIndex().row())
        model.submitAll()
        model.select()

    def query_save_table(self):
        model = self.ui.query_list_view.model()
        model.database().transaction()
        if model.submitAll():
            model.database().commit()
        else:
            model.database().rollback()

# TODO: 这里是子线程函数
# 4的子线程，在点击供应商评估后完成对供应商数据的计算，生成图表并展示在窗体上
class supplier_eval(QThread):
    # 自定义一个信号
    image_generated = Signal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            image_file_name = "D:/Python/ERPProject/cg_gr/40004001.png"

            self.image_generated.emit(image_file_name)
        except Exception as e:
            print(f"Exception during evaluation: {str(e)}")
        finally:
            self.quit()

class supplier_form(QDialog):
    def __init__(self, company_id, sup1, sup2, sup3, sup4, sup5):
        super(supplier_form, self).__init__()
        self.ui = Ui_cg_form()
        self.ui.setupUi(self)
        self.company_id = company_id
        self.init_table()
        self.supplier_table = sup1
    
    def init_table(self):
        company_id = self.company_id
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        filename = self.supplier_table
        self.database.setDatabaseName(filename)
        if not self.database.open():
            print("Error: Could not open the database")

        table_name = self.detect_table_name()
        if table_name:
            model = QSqlTableModel(self, self.database)
            model.setTable(table_name)

            model.setHeaderData(0, Qt.Horizontal, "物料名称")
            model.setHeaderData(1, Qt.Horizontal, "物料编码")
            model.setHeaderData(2, Qt.Horizontal, "物料价格")
            model.setHeaderData(3, Qt.Horizontal, "备注")
            model.select()
            # 显示表格
            self.ui.supplier_table_view.setModel(model)
            self.ui.supplier_table_view.resizeColumnsToContents()

        self.ui.supplier_item_add.clicked.connect(self.item_add)
        self.ui.supplier_item_delete.clicked.connect(self.item_delete)
        self.ui.supplier_item_save.clicked.connect(self.item_save)
    

    def detect_table_name(self):
        tables = self.database.tables()
        if tables:
            return tables[0]
        else:
            print("No such tables.")
            return None

    def item_add(self):
        print("add")
        model = self.ui.supplier_table_view.model()
        model.submitAll()
        result = model.insertRows(model.rowCount(), 1)

        if not result:
            self.error_check(model)

    def item_delete(self):
        print("delete")
        model = self.ui.supplier_table_view.model()
        model.removeRow(self.ui.supplier_table_view.currentIndex().row())
        model.submitAll()
        model.select()

    def item_save(self):
        print("save")
        model = self.ui.supplier_table_view.model()
        model.database().transaction()
        if model.submitAll():
            model.database().commit()
        else:
            model.database().rollback()

if __name__ == '__main__':
    detail_file = os.path.abspath("cg/cg_db/Purchase Detail.db")
    list_file = os.path.abspath("jh/code/JHdatabase.db")
    receipt_file = os.path.abspath("cg/cg_db/Purchase Receipt.db")
    supplier_file = os.path.abspath("cg/cg_db/Purchase Supplier.db")

    # 创建一个名为app的实例，代表应用本身，用于设置GUI并处理事件
    app = QApplication(sys.argv)
    # 实例化MyWindow
    widget = cg_widget(detail_file, list_file, receipt_file, supplier_file, '../test.db', "采购")
    # 在屏幕上显示QWiget窗口
    widget.show()
    # 启动QApplication的循环，直到用户关闭窗口
    sys.exit(app.exec())