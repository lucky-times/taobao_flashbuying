from PyQt5.Qt import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import time, os
import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(988, 757)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # 确认按钮设置
        self.confirm_btn = QtWidgets.QPushButton(self.centralwidget)
        self.confirm_btn.setGeometry(QtCore.QRect(180, 280, 93, 28))
        self.confirm_btn.setObjectName("pushButton")
        # 退出按钮设置
        self.stop_btn = QtWidgets.QPushButton(self.centralwidget)
        self.stop_btn.setGeometry(QtCore.QRect(180, 550, 93, 28))
        self.stop_btn.setInputMethodHints(QtCore.Qt.ImhNoAutoUppercase)
        self.stop_btn.setObjectName("pushButton_2")
        # 输入时间条设置
        self.time_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.time_edit.setGeometry(QtCore.QRect(310, 280, 451, 31))
        self.time_edit.setText("")
        self.time_edit.setObjectName("lineEdit")
        # 当前时间展示标签
        self.currenttime_label = QtWidgets.QLabel(self.centralwidget)
        self.currenttime_label.setGeometry(QtCore.QRect(190, 170, 71, 61))
        self.currenttime_label.setObjectName("shijian")
        # 商品购买信息情况
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(310, 360, 451, 171))
        self.textBrowser.setObjectName("textBrowser")
        # 商品情况标签
        self.dialog = QtWidgets.QLabel(self.centralwidget)
        self.dialog.setGeometry(QtCore.QRect(180, 390, 101, 51))
        self.dialog.setObjectName("dialog")
        # LCD展示当前时间
        self.data_time = QtWidgets.QLCDNumber(self.centralwidget)
        self.data_time.setGeometry(QtCore.QRect(300, 170, 621, 41))
        self.data_time.setAutoFillBackground(False)
        self.data_time.setDigitCount(25)
        self.data_time.setObjectName("data_time")
        # 计时器
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.clock)
        # MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 988, 26))
        self.menubar.setObjectName("menubar")
        # MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        self.stop_btn.clicked.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        #启动一个新的线程
        self.work = WorkThread()
        self.confirm_btn.clicked.connect(self.execute)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "淘宝限时抢购助手"))
        MainWindow.setWindowIcon(QIcon("icon.jpg"))
        self.confirm_btn.setText(_translate("MainWindow", "确认"))
        self.stop_btn.setText(_translate("MainWindow", "退出"))
        self.time_edit.setPlaceholderText(_translate("MainWindow", "请输入抢购时间，格式如：2020-02-25 20:13:30"))
        self.currenttime_label.setText(_translate("MainWindow", "当前时间"))
        self.textBrowser.setPlaceholderText(_translate("MainWindow", "暂时无"))
        self.dialog.setText(_translate("MainWindow", "商品抢购情况"))
    def clock(self):
        t = time.strftime('%Y-%m-%d  %H:%M:%S')
        self.data_time.display(t)

    def execute(self):
        self.work.buytime=self.time_edit.text()
        # 启动线程
        self.work.start()
        # 线程自定义信号连接的槽函数
        self.work.trigger.connect(self.printf)

    def printf(self, str):
        self.textBrowser.append(str)  # 在指定的区域显示提示信息
        self.cursot = self.textBrowser.textCursor()
        self.textBrowser.moveCursor(self.cursot.End)  # 光标移到最后，这样就会自动显示出来


class WorkThread(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    trigger = pyqtSignal(str)
    buytime = ''
    def __int__(self):
        # 初始化函数
        super(WorkThread, self).__init__()

    def run(self):
        # 重写线程执行的run函数
        buytime = self.buytime
        self.trigger.emit(buytime)
        buy_time_object = datetime.datetime.strptime(buytime, '%Y-%m-%d %H:%M:%S.%f')
        now_time = datetime.datetime.now()
        login_success = False
        if now_time > buy_time_object:
            self.trigger.emit("当前已过抢购时间，请确认抢购时间是否填错...")
            exit(0)
        self.trigger.emit("抢购时间输入合法，正在运行")
        self.trigger.emit("正在打开chrome浏览器...")
        driver = webdriver.Chrome(executable_path='chromedriver.exe')
        driver.maximize_window()
        self.trigger.emit("chrome浏览器已经打开...")
        self.login(driver, login_success)
        self.keep_login_and_wait(buy_time_object, driver)
        self.buy(driver, buy_time_object)

    def login(self, driver, login_success):
        while True:
            driver.get("https://www.taobao.com")
            try:
                if driver.find_element_by_link_text("亲，请登录"):
                    driver.find_element_by_link_text("亲，请登录").click()
                    self.trigger.emit("请使用手机淘宝扫描屏幕上的二维码进行登录...（请在10秒内完成）")
                    time.sleep(15)
            except:
                self.trigger.emit("已登录，开始执行跳转...")
                time.sleep(0.2)
                login_success = True
            if login_success:
                time.sleep(0.2)
                self.trigger.emit("登录成功")
                break
            else:
                self.trigger.emit("等待登录中...")

        time.sleep(2)
        now = datetime.datetime.now()
        self.trigger.emit('login success:'+now.strftime('%Y-%m-%d %H:%M:%S.%f'))

    def keep_login_and_wait(self, buy_time_object, driver):
        while True:
            currentTime = datetime.datetime.now()
            if (buy_time_object - currentTime).seconds > 180:
                self.trigger.emit("当前距离抢购时间点还有较长时间，开始定时刷新防止登录超时...")
                driver.get("https://cart.taobao.com/cart.htm")
                self.trigger.emit("刷新购物车界面，防止登录超时...")
                time.sleep(60)
            else:
                self.trigger.emit("抢购时间点将近，停止自动刷新，准备进入抢购阶段...")
                break

    def buy(self, driver, buy_time_object):
        # 打开购物车
        driver.get("https://cart.taobao.com/cart.htm")
        time.sleep(1)
        # 点击购物车里全选按钮
        if driver.find_element_by_id("J_SelectAll1"):
            driver.find_element_by_id("J_SelectAll1").click()
            self.trigger.emit("已经选中购物车中全部商品 ...")
        submit_succ = False
        while True:
            now = datetime.datetime.now()
            if now >= buy_time_object:
                if submit_succ:
                    self.trigger.emit("订单已经提交成功，请抓紧时间付款吧！")
                    break
                try:
                    # 点击结算按钮
                    if driver.find_element_by_id("J_Go"):
                        driver.find_element_by_id("J_Go").click()
                        self.trigger.emit("已经点击结算按钮...")
                        while True:
                            time.sleep(0.01)
                            try:
                                if driver.find_element_by_class_name("go-btn"):
                                    driver.find_element_by_class_name("go-btn").click()
                                    self.trigger.emit("已经点击提交订单按钮")
                                    submit_succ = True
                                    break
                                else:
                                    self.trigger.emit("未找到提交订单按钮")
                            except Exception as ee:
                                os.system('pause')
                                self.trigger.emit("没发现提交订单按钮，可能页面还没加载出来，重试...")#此处留有问题
                except Exception as e:
                    self.trigger.emit("不好，挂了，提交订单失败了...")

            time.sleep(0.1)
        # 触发自定义信号


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)
    widget.show()
    sys.exit(app.exec_())