# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QStyleFactory, QFileDialog
# from PyQt5.QtGui import QFont, QPen, QBrush
from campus_network_HCI import Ui_MainWindow

import sys, os, pprint, subprocess, time, base64
from decimal import Decimal

router_num, link_num = 2, 1
edges = []
router_msg = []
router_selected = 1
source, dest = 1, 2

class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r',  encoding='UTF-8') as file:
            return file.read()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        _translate = QtCore.QCoreApplication.translate

    # 关于
    def trigger_actHelp(self):
        QMessageBox.about(self, "About","""校园网路由设计\nBy Rrhar'il Team""")
        return

    # 退出
    def trigger_actExit(self):
        self.close()
        return

    # 重置路由数和链路数
    def trigger_pushButton_reset(self):
        reply = QMessageBox.question(self, "Warning", "确定要重置路由数和链路数吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.spinBox_router_num.setValue(2)
            self.spinBox_link_num.setValue(1)
            # 清空链路信息输入框
            for i in reversed(range(self.scrollAreaWidgetContents_edges.layout().count())):
                widget = self.scrollAreaWidgetContents_edges.layout().itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        # 停用导出按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_exportedges").setEnabled(False)
        self.findChild(QtWidgets.QAction, "action_export").setEnabled(False)
        self.findChild(QtWidgets.QAction, "action_export_to").setEnabled(False)
        # 停用重置链路信息按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_resetedge").setEnabled(False)
        return

    # 设置路由数和链路数
    def trigger_pushButton_setnum(self):
        global router_num, link_num
        router_num = self.spinBox_router_num.value()
        link_num = self.spinBox_link_num.value()
        # 状态栏提示成功消息，等待5秒后消失
        self.statusbar.showMessage("设置成功！！\n路由数：{}  链路数：{}".format(router_num, link_num), 5000)

        # 清空原有的输入框
        for i in reversed(range(self.scrollAreaWidgetContents_edges.layout().count())):
            widget = self.scrollAreaWidgetContents_edges.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 添加各边的输入框
        for i in range(1, link_num + 1):
            widget_edge_i = QtWidgets.QWidget(self.scrollAreaWidgetContents_edges)
            widget_edge_i.setMinimumSize(QtCore.QSize(400, 35))
            widget_edge_i.setObjectName(f"widget_edge_{i}")

            h_layout_i = QtWidgets.QHBoxLayout(widget_edge_i)
            h_layout_i.setContentsMargins(10, 10, 10, 10)
            h_layout_i.setObjectName(f"horizontalLayout_{i}")

            label_i = QtWidgets.QLabel(widget_edge_i)
            label_i.setMinimumSize(QtCore.QSize(80, 25))
            label_i.setObjectName(f"label_{i}")
            label_i.setText(f"第{i}条链路")
            h_layout_i.addWidget(label_i)

            combo_start_i = QtWidgets.QComboBox(widget_edge_i)
            combo_start_i.setMinimumSize(QtCore.QSize(80, 25))
            combo_start_i.setObjectName(f"comboBox_start_{i}")
            h_layout_i.addWidget(combo_start_i)
            combo_start_i.addItems([str(i) for i in range(1, router_num + 1)]) # 列表项目为所有路由器序号

            combo_end_i = QtWidgets.QComboBox(widget_edge_i)
            combo_end_i.setMinimumSize(QtCore.QSize(80, 25))
            combo_end_i.setObjectName(f"comboBox_end_{i}")
            h_layout_i.addWidget(combo_end_i)
            combo_end_i.addItems([str(i) for i in range(1, router_num + 1)])

            spin_cost_i = QtWidgets.QSpinBox(widget_edge_i)
            spin_cost_i.setMinimumSize(QtCore.QSize(80, 25))
            spin_cost_i.setMaximum(65535)
            spin_cost_i.setProperty("value", 1)
            spin_cost_i.setObjectName(f"spinBox_cost_{i}")
            h_layout_i.addWidget(spin_cost_i)

            spin_maxthrput_i = QtWidgets.QSpinBox(widget_edge_i)
            spin_maxthrput_i.setMinimumSize(QtCore.QSize(80, 25))
            spin_maxthrput_i.setMaximum(65535)
            spin_maxthrput_i.setProperty("value", 1)
            spin_maxthrput_i.setObjectName(f"spinBox_maxthrput_{i}")
            h_layout_i.addWidget(spin_maxthrput_i)

            h_layout_i.setStretch(0, 6)
            h_layout_i.setStretch(1, 5)
            h_layout_i.setStretch(2, 5)
            h_layout_i.setStretch(3, 5)
            h_layout_i.setStretch(4, 5)

            v_layout = self.scrollAreaWidgetContents_edges.layout()
            v_layout.addWidget(widget_edge_i)

        # 停用导出按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_exportedges").setEnabled(False)
        self.findChild(QtWidgets.QAction, "action_export").setEnabled(False)
        self.findChild(QtWidgets.QAction, "action_export_to").setEnabled(False)
        # 启用重置链路信息按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_resetedge").setEnabled(True)
        # 限制spinBox_source和spinBox_dest的最大值
        self.spinBox_source.setMaximum(router_num)
        self.spinBox_dest.setMaximum(router_num)
        return

    # 生成全局变量，存放并输出所有链路信息
    def trigger_pushButton_generate(self):
        # 如果scrollAreaWidgetContents_edges中的输入框数量不等于链路数，则弹出警告
        if self.scrollAreaWidgetContents_edges.layout().count() != link_num:
            QMessageBox.warning(self, "Warning", "请先设置链路！", QMessageBox.Yes)
            return

        global edges
        edges = []
        for i in range(1, link_num + 1):
            edges.append([int(self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QComboBox, f"comboBox_start_{i}").currentText()),
                          int(self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QComboBox, f"comboBox_end_{i}").currentText()),
                          self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QSpinBox, f"spinBox_cost_{i}").value(),
                          self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QSpinBox, f"spinBox_maxthrput_{i}").value()])
        # 状态栏提示成功消息，等待5秒后消失
        self.statusbar.showMessage("共有{}条链路添加成功！！".format(link_num), 5000)

        # 在textBrowser_showedges中显示所有全局变量
        str_style = '''<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;margin:0px auto;}
.tg td{border-color:white;border-style:none;border-width:0px;font-size:14px;overflow:hidden;padding:5px 10px;word-break:normal;}
.tg th{border-color:white;border-style:none;border-width:0px;font-size:14px;overflow:hidden;padding:5px 10px;word-break:normal;}
.tg .tg-zv4m{border-color:#ffffff;text-align:left;vertical-align:top}
.tg .tg-8jgo{border-color:#ffffff;text-align:center;vertical-align:top}
@media screen and (max-width: 767px) {.tg {width: auto !important;}.tg col {width: auto !important;}.tg-wrap {overflow-x: auto;-webkit-overflow-scrolling: touch;margin: auto 0px;}}</style>'''
        str_info = [str_style, '<div >路由器数量：{}\t'.format(router_num), '链路数量：{}</div><br />'.format(link_num), '''<table class="tg">
<thead>
    <tr>
        <th class="tg-zv4m">链路信息</th>
        <th class="tg-8jgo">起点</th>
        <th class="tg-8jgo">终点</th>
        <th class="tg-8jgo">造价</th>
        <th class="tg-8jgo">最大吞吐量</th>
    </tr>
</thead>
<tbody>''']
        for i in range(link_num):
            str_info.append("<tr>")
            str_info.append('<td class="tg-zv4m">第{}条链路：</td>'.format(i + 1))
            str_info.append('<td class="tg-8jgo">{}</td>'.format(edges[i][0]))
            str_info.append('<td class="tg-8jgo">{}</td>'.format(edges[i][1]))
            str_info.append('<td class="tg-8jgo">{}</td>'.format(edges[i][2]))
            str_info.append('<td class="tg-8jgo">{}</td>'.format(edges[i][3]))
            str_info.append("</tr>")
        str_info.append("</tbody>\n</table>")
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_showedges"
            ).setHtml("".join(str_info))

        # 绘制拓扑图 # TODO: 拓扑图

        # 启用导出按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_exportedges").setEnabled(True)
        self.findChild(QtWidgets.QAction, "action_export").setEnabled(True)
        self.findChild(QtWidgets.QAction, "action_export_to").setEnabled(True)
        # 启用计算
        self.pushButton_calc_maxthrput.setEnabled(True)
        self.findChild(QtWidgets.QPushButton,"pushButton_calc_kruskal").setEnabled(True)
        self.findChild(QtWidgets.QPushButton,"pushButton_calc_prim").setEnabled(True)
        self.findChild(QtWidgets.QPushButton, "pushButton_cmp").setEnabled(True)
        self.findChild(QtWidgets.QPushButton, "pushButton_cmp_times").setEnabled(True)
        self.findChild(QtWidgets.QSpinBox, "spinBox_kwin_times").setValue(0)
        self.findChild(QtWidgets.QSpinBox, "spinBox_pwin_times").setValue(0)
        self.findChild(QtWidgets.QDoubleSpinBox, "spinBox_rate").setValue(0.00)
        # 启用spinBox_selectrouter和spinBox_selectrouter_tosend，最小值是1，最大值是路由器数
        self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter").setEnabled(True)
        self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter").setMinimum(1)
        self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter").setMaximum(router_num)
        self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter_tosend").setEnabled(True)
        self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter_tosend").setMinimum(1)
        self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter_tosend").setMaximum(router_num)
        self.findChild(QtWidgets.QPushButton, "pushButton_saveall").setEnabled(True)
        self.findChild(QtWidgets.QPushButton, "pushButton_en").setEnabled(True)
        self.findChild(QtWidgets.QPushButton, "pushButton_send").setEnabled(True)
        # 初始化router_msg
        global router_msg
        router_msg = []
        for i in range(router_num + 1):
            router_msg.append(["", "", "", 1, 1, "", "", ""])
        return

    # 重置链路信息，弹出确认窗口
    def trigger_pushButton_resetedges(self):
        reply = QMessageBox.question(self, "Warning", "确定要重置链路信息吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for i in range(1, link_num + 1):
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QComboBox, f"comboBox_start_{i}").setCurrentIndex(0)
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QComboBox, f"comboBox_end_{i}").setCurrentIndex(0)
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QSpinBox, f"spinBox_cost_{i}").setValue(1)
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QSpinBox, f"spinBox_maxthrput_{i}").setValue(1)
            # edges = []

            # 停用导出按钮
            self.findChild(QtWidgets.QPushButton, "pushButton_exportedges").setEnabled(False)
            self.findChild(QtWidgets.QAction, "action_export").setEnabled(False)
            self.findChild(QtWidgets.QAction, "action_export_to").setEnabled(False)
        return

    # 导出链路信息到config/edges.txt
    def trigger_pushButton_exportedges(self):
        # 判断是否有该文件夹，没有则创建
        if not os.path.exists("config"):
            os.mkdir("config")
        with open("config/edges.txt", "w") as f:
            # 写入路由器和链路数量
            f.write("{} {}\n".format(router_num, link_num))
            for edge in edges:
                f.write("{} {} {} {}\n".format(edge[0], edge[1], edge[2], edge[3]))
        # 状态栏提示成功消息，等待5秒后消失
        self.statusbar.showMessage("链路信息已成功导出到config/edges.txt！！", 5000)
        # 启用导入按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_importedges").setEnabled(True)
        self.findChild(QtWidgets.QAction, "action_import").setEnabled(True)
        return
    
    # 导出为...
    def trigger_pushButton_exportedges_to(self):
        # 判断是否有该文件夹，没有则创建
        if not os.path.exists("config"):
            os.mkdir("config")
        # 弹出文件选择窗口
        filename_choose, filetype = QFileDialog.getSaveFileName(self,
                                    "选取文件",
                                    "config/edges.txt",
                                    "Text Files (*.txt);;All Files (*)")
        if filename_choose == "":
            return
        with open(filename_choose, "w") as f:
            # 写入路由器和链路数量
            f.write("{} {}\n".format(router_num, link_num))
            for edge in edges:
                f.write("{} {} {} {}\n".format(edge[0], edge[1], edge[2], edge[3]))
        # 状态栏提示成功消息，等待5秒后消失
        self.statusbar.showMessage("链路信息已成功导出到{}！！".format(filename_choose), 5000)
        # 启用导入按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_importedges").setEnabled(True)
        self.findChild(QtWidgets.QAction, "action_import").setEnabled(True)
        return

    # 从config/edges.txt导入链路信息
    def trigger_pushButton_importedges(self):
        reply = QMessageBox.question(self, "Warning", "确定要导入链路信息吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        router_num_inner, link_num_inner = 0, 0
        if reply == QMessageBox.Yes:
            # 如果文件不合法，弹出警告窗口
            if not check_importedges():
                QMessageBox.warning(self, "Warning", "导入的文件不合法，请重新导入！", QMessageBox.Yes)
                return
            with open("config/edges.txt", "r") as f:
                edges_info = f.readlines()

            edge = edges_info[0]
            router_num_str, link_num_str = edge.split()
            router_num_inner = int(router_num_str)
            link_num_inner = int(link_num_str)
            # 在状态栏显示路由器和链路数量
            self.statusbar.showMessage("路由器数量：{}，链路数量：{}".format(router_num_inner, link_num_inner))
            self.findChild(QtWidgets.QSpinBox, "spinBox_router_num").setValue(router_num_inner)
            self.findChild(QtWidgets.QSpinBox, "spinBox_link_num").setValue(link_num_inner)

            # 清空原有的输入框
            while self.scrollAreaWidgetContents_edges.layout().count() > 0:
                item = self.scrollAreaWidgetContents_edges.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

            # 添加各边的输入框
            for k in range(1, link_num_inner + 1):
                widget_edge_k = QtWidgets.QWidget(self.scrollAreaWidgetContents_edges)
                widget_edge_k.setMinimumSize(QtCore.QSize(400, 35))
                widget_edge_k.setObjectName(f"widget_edge_{k}")

                h_layout_k = QtWidgets.QHBoxLayout(widget_edge_k)
                h_layout_k.setContentsMargins(10, 10, 10, 10)
                h_layout_k.setObjectName(f"horizontalLayout_{k}")

                label_k = QtWidgets.QLabel(widget_edge_k)
                label_k.setMinimumSize(QtCore.QSize(80, 25))
                label_k.setObjectName(f"label_{k}")
                label_k.setText(f"第{k}条链路")
                h_layout_k.addWidget(label_k)

                combo_start_k = QtWidgets.QComboBox(widget_edge_k)
                combo_start_k.setMinimumSize(QtCore.QSize(80, 25))
                combo_start_k.setObjectName(f"comboBox_start_{k}")
                h_layout_k.addWidget(combo_start_k)
                combo_start_k.addItems([str(l) for l in range(1, router_num_inner + 1)])  # 列表项目为所有路由器序号

                combo_end_k = QtWidgets.QComboBox(widget_edge_k)
                combo_end_k.setMinimumSize(QtCore.QSize(80, 25))
                combo_end_k.setObjectName(f"comboBox_end_{k}")
                h_layout_k.addWidget(combo_end_k)
                combo_end_k.addItems([str(l) for l in range(1, router_num_inner + 1)])

                spin_cost_k = QtWidgets.QSpinBox(widget_edge_k)
                spin_cost_k.setMinimumSize(QtCore.QSize(80, 25))
                spin_cost_k.setMaximum(65535)
                spin_cost_k.setProperty("value", 1)
                spin_cost_k.setObjectName(f"spinBox_cost_{k}")
                h_layout_k.addWidget(spin_cost_k)

                spin_maxthrput_k = QtWidgets.QSpinBox(widget_edge_k)
                spin_maxthrput_k.setMinimumSize(QtCore.QSize(80, 25))
                spin_maxthrput_k.setMaximum(65535)
                spin_maxthrput_k.setProperty("value", 1)
                spin_maxthrput_k.setObjectName(f"spinBox_maxthrput_{k}")
                h_layout_k.addWidget(spin_maxthrput_k)

                h_layout_k.setStretch(0, 6)
                h_layout_k.setStretch(1, 5)
                h_layout_k.setStretch(2, 5)
                h_layout_k.setStretch(3, 5)
                h_layout_k.setStretch(4, 5)

                v_layout = self.scrollAreaWidgetContents_edges.layout()
                v_layout.addWidget(widget_edge_k)

            for i, edge in enumerate(edges_info):
                if i == 0:
                    continue
                edge = edge.split()
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QComboBox, f"comboBox_start_{i}").setCurrentIndex(int(edge[0])-1)
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QComboBox, f"comboBox_end_{i}").setCurrentIndex(int(edge[1])-1)
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QSpinBox, f"spinBox_cost_{i}").setValue(int(edge[2]))
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QSpinBox, f"spinBox_maxthrput_{i}").setValue(int(edge[3]))

        global router_num, link_num
        router_num = router_num_inner
        link_num = link_num_inner

        # 启用导出按钮
        self.pushButton_exportedges.setEnabled(True)
        self.action_export.setEnabled(True)
        self.action_export_to.setEnabled(True)
        # 启用重置链路信息按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_resetedge").setEnabled(True)
        # 限制spinBox_source和spinBox_dest的最大值
        self.spinBox_source.setMaximum(router_num)
        self.spinBox_dest.setMaximum(router_num)
        return
    
    # 选择文件导入
    def trigger_pushButton_importedges_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选取文件", "./config", "Text Files (*.txt)")
        if file_name == "":
            return
        reply = QMessageBox.question(self, "Warning", "确定要导入链路信息吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        router_num_inner, link_num_inner = 0, 0
        if reply == QMessageBox.Yes:
            # 如果文件不合法，弹出警告窗口
            if not check_importedges():
                QMessageBox.warning(self, "Warning", "导入的文件不合法，请重新导入！", QMessageBox.Yes)
                return
            with open(file_name, "r") as f:
                edges_info = f.readlines()

            edge = edges_info[0]
            router_num_str, link_num_str = edge.split()
            router_num_inner = int(router_num_str)
            link_num_inner = int(link_num_str)
            # 在状态栏显示路由器和链路数量
            self.statusbar.showMessage("路由器数量：{}，链路数量：{}".format(router_num_inner, link_num_inner))
            self.findChild(QtWidgets.QSpinBox, "spinBox_router_num").setValue(router_num_inner)
            self.findChild(QtWidgets.QSpinBox, "spinBox_link_num").setValue(link_num_inner)

            # 清空原有的输入框
            while self.scrollAreaWidgetContents_edges.layout().count() > 0:
                item = self.scrollAreaWidgetContents_edges.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

            # 添加各边的输入框
            for k in range(1, link_num_inner + 1):
                widget_edge_k = QtWidgets.QWidget(self.scrollAreaWidgetContents_edges)
                widget_edge_k.setMinimumSize(QtCore.QSize(400, 35))
                widget_edge_k.setObjectName(f"widget_edge_{k}")

                h_layout_k = QtWidgets.QHBoxLayout(widget_edge_k)
                h_layout_k.setContentsMargins(10, 10, 10, 10)
                h_layout_k.setObjectName(f"horizontalLayout_{k}")

                label_k = QtWidgets.QLabel(widget_edge_k)
                label_k.setMinimumSize(QtCore.QSize(80, 25))
                label_k.setObjectName(f"label_{k}")
                label_k.setText(f"第{k}条链路")
                h_layout_k.addWidget(label_k)

                combo_start_k = QtWidgets.QComboBox(widget_edge_k)
                combo_start_k.setMinimumSize(QtCore.QSize(80, 25))
                combo_start_k.setObjectName(f"comboBox_start_{k}")
                h_layout_k.addWidget(combo_start_k)
                combo_start_k.addItems([str(l) for l in range(1, router_num_inner + 1)])  # 列表项目为所有路由器序号

                combo_end_k = QtWidgets.QComboBox(widget_edge_k)
                combo_end_k.setMinimumSize(QtCore.QSize(80, 25))
                combo_end_k.setObjectName(f"comboBox_end_{k}")
                h_layout_k.addWidget(combo_end_k)
                combo_end_k.addItems([str(l) for l in range(1, router_num_inner + 1)])

                spin_cost_k = QtWidgets.QSpinBox(widget_edge_k)
                spin_cost_k.setMinimumSize(QtCore.QSize(80, 25))
                spin_cost_k.setMaximum(65535)
                spin_cost_k.setProperty("value", 1)
                spin_cost_k.setObjectName(f"spinBox_cost_{k}")
                h_layout_k.addWidget(spin_cost_k)

                spin_maxthrput_k = QtWidgets.QSpinBox(widget_edge_k)
                spin_maxthrput_k.setMinimumSize(QtCore.QSize(80, 25))
                spin_maxthrput_k.setMaximum(65535)
                spin_maxthrput_k.setProperty("value", 1)
                spin_maxthrput_k.setObjectName(f"spinBox_maxthrput_{k}")
                h_layout_k.addWidget(spin_maxthrput_k)

                h_layout_k.setStretch(0, 6)
                h_layout_k.setStretch(1, 5)
                h_layout_k.setStretch(2, 5)
                h_layout_k.setStretch(3, 5)
                h_layout_k.setStretch(4, 5)

                v_layout = self.scrollAreaWidgetContents_edges.layout()
                v_layout.addWidget(widget_edge_k)

            for i, edge in enumerate(edges_info):
                if i == 0:
                    continue
                edge = edge.split()
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QComboBox, f"comboBox_start_{i}").setCurrentIndex(int(edge[0])-1)
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QComboBox, f"comboBox_end_{i}").setCurrentIndex(int(edge[1])-1)
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QSpinBox, f"spinBox_cost_{i}").setValue(int(edge[2]))
                self.scrollAreaWidgetContents_edges.findChild(QtWidgets.QSpinBox, f"spinBox_maxthrput_{i}").setValue(int(edge[3]))

        global router_num, link_num
        router_num = router_num_inner
        link_num = link_num_inner

        # 启用导出按钮
        self.pushButton_exportedges.setEnabled(True)
        self.action_export.setEnabled(True)
        self.action_export_to.setEnabled(True)
        # 启用重置链路信息按钮
        self.findChild(QtWidgets.QPushButton, "pushButton_resetedge").setEnabled(True)
        # 限制spinBox_source和spinBox_dest的最大值
        self.spinBox_source.setMaximum(router_num)
        self.spinBox_dest.setMaximum(router_num)
        return

    # 打印全局变量
    @staticmethod
    def print_edges():
        pprint.pprint(router_num)
        pprint.pprint(link_num)
        pprint.pprint(edges)

    # 计算最大流
    def calc_maxthrput(self):
        global source, dest
        # 源节点和目的节点
        source = self.spinBox_source.value()
        dest = self.spinBox_dest.value()
        # 调用 dinic.exe
        dinic_exe_path = "./dinic/dinic.exe"
        # 构造输入数据
        input_data = f"{router_num}\n{link_num}\n{source}\n{dest}\n"
        for edge in edges:
            input_data += f"{edge[0]}\n{edge[1]}\n{edge[3]}\n"

        # 执行进程
        with subprocess.Popen(dinic_exe_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
            try:
                stdout, stderr = p.communicate(input_data.encode()) # 将数据写入 stdin 并关闭
                result = str(stdout[82:].decode('GB2312', errors='ignore').split("\r\n")[-2]) # 从stdout中提取结果
                # 输出到textBrowser_calc_maxthrput
                self.findChild(QtWidgets.QTextBrowser, "textBrowser_calc_maxthrput").setMarkdown(result)
            except Exception as e:
                print(f"An error occurred: {e}")
        return

    # 使用kruskal算法计算最小造价
    def calc_cost_kruskal(self):
        # 调用kruskal.exe
        kruskal_exe_path = "./kruskal/kruskal.exe"
        # 构造输入数据
        input_data = f"{router_num} {link_num}\n"
        for edge in edges:
            input_data += f"{edge[0]} {edge[1]} {edge[2]}\n"

        # 执行进程
        start_time = time.time() # 开始计时
        with subprocess.Popen(kruskal_exe_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
            try:
                stdout, stderr = p.communicate(input_data.encode())
                end_time = time.time() # 结束计时
                result = stdout.decode('GB2312', errors='ignore').split("\n")
                min_cost_path = "" # 代价最小的路径
                for line in result[:-2]:
                    min_cost_path += line + "<br />"
                min_cost = result[-2] # 最小代价
                self.findChild(QtWidgets.QTextBrowser, "textBrowser_calc_cost_kruskal_path").setMarkdown(min_cost_path)
                self.findChild(QtWidgets.QTextBrowser, "textBrowser_calc_cost_kruskal_cost").setMarkdown(min_cost)
            except Exception as e:
                print(f"An error occurred: {e}")
        exec_time = end_time - start_time
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_calc_cost_kruskal_time").setMarkdown(str(exec_time) + "s")
        return

    # 使用prim算法计算最小造价
    def calc_cost_prim(self):
        # 调用prim.exe
        prim_exe_path = "./prim/prim.exe"
        # 构造输入数据
        input_data = f"{router_num} {link_num}\n"
        for edge in edges:
            input_data += f"{edge[0]} {edge[1]} {edge[2]}\n"

        # 执行进程
        start_time = time.time() # 开始计时
        with subprocess.Popen(prim_exe_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
            try:
                stdout, stderr = p.communicate(input_data.encode())
                end_time = time.time() # 结束计时
                result = stdout.decode('GB2312', errors='ignore').split("\r\n")
                min_cost_path = "" # 代价最小的路径
                for line in result[:-2]:
                    min_cost_path += line + "<br />"
                min_cost = result[-2] # 最小代价
                self.findChild(QtWidgets.QTextBrowser, "textBrowser_calc_cost_prim_path").setHtml(min_cost_path)
                self.findChild(QtWidgets.QTextBrowser, "textBrowser_calc_cost_prim_cost").setHtml(min_cost)
            except Exception as e:
                print(f"An error occurred: {e}")
        exec_time = end_time - start_time
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_calc_cost_prim_time").setMarkdown(str(exec_time) + "s")
        return

    # 比较两种算法所用时长，从spinBox_times中获取运算次数，对两种算法分别计算指定的次数，分别求取平均数，显示在textBrowser_kruskal_avg和
    # textBrowser_prim_avg中，将用时最少的那个算法的标签文字颜色改为红色
    def calc_cmp_time(self):
        # 初始两个标签都得染成黑色滴
        self.findChild(QtWidgets.QLabel, "label_kruskal").setStyleSheet("color: black")
        self.findChild(QtWidgets.QLabel, "label_prim").setStyleSheet("color: black")

        # 获取运算次数
        times = self.findChild(QtWidgets.QSpinBox, "spinBox_times").value()

        kruskal_exe_path = "./kruskal/kruskal.exe"
        prim_exe_path = "./prim/prim.exe"
        input_data = f"{router_num} {link_num}\n"
        for edge in edges:
            input_data += f"{edge[0]} {edge[1]} {edge[2]}\n"

        exec_time_kruskal = []
        for _ in range(times):
            start_time = time.time()
            with subprocess.Popen(kruskal_exe_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
                try:
                    __, ___ = p.communicate(input_data.encode())
                except Exception as e:
                    print(f"An error occurred: {e}")
            end_time = time.time()
            exec_time_kruskal.append(Decimal(end_time) - Decimal(start_time))
        avg_time_kruskal = Decimal(sum(exec_time_kruskal)) / Decimal(times)
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_kruskal_avg").setMarkdown(str(avg_time_kruskal) + "s")

        exec_time_prim = []
        for _ in range(times):
            start_time = time.time()
            with subprocess.Popen(prim_exe_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
                try:
                    __, ___ = p.communicate(input_data.encode())
                except Exception as e:
                    print(f"An error occurred: {e}")
            end_time = time.time()
            exec_time_prim.append(Decimal(end_time) - Decimal(start_time))
        avg_time_prim = Decimal(sum(exec_time_prim)) / Decimal(times)
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_prim_avg").setMarkdown(str(avg_time_prim) + "s")

        if avg_time_kruskal < avg_time_prim:
            self.findChild(QtWidgets.QLabel, "label_kruskal").setStyleSheet("color: rgb(255, 0, 0);")
            self.findChild(QtWidgets.QSpinBox, "spinBox_kwin_times").setValue(self.findChild(QtWidgets.QSpinBox, "spinBox_kwin_times").value() + 1)
        else:
            self.findChild(QtWidgets.QLabel, "label_prim").setStyleSheet("color: rgb(255, 0, 0);")
            self.findChild(QtWidgets.QSpinBox, "spinBox_pwin_times").setValue(self.findChild(QtWidgets.QSpinBox, "spinBox_pwin_times").value() + 1)
        rate = self.findChild(QtWidgets.QSpinBox, "spinBox_kwin_times").value() / self.findChild(QtWidgets.QSpinBox, "spinBox_pwin_times").value()
        self.findChild(QtWidgets.QDoubleSpinBox, "spinBox_rate").setValue(rate)
        return

    # 重复比较多次
    def calc_cmp_fortimes(self):
        for _ in range(self.findChild(QtWidgets.QSpinBox, "spinBox_cmp_times").value()):
            self.calc_cmp_time()
        return

    # 随spinBox_selectrouter的值而选择路由器的节点
    def select_router(self):
        global router_selected
        router_selected = self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter").value()
        router_index = router_selected - 1
        # router_msg存放每个路由器的消息，包括：
        # 0发送base64的明文字符串、1加密密钥字符串、2发送的加密密文、3接收方、4发送方、5接收的加密密文、6解密密钥、7解密后的base64明文字符串
        # 所有文本信息全部以base64编码存储，显示时需先解密
        send_plain = base64.b64decode(router_msg[router_index][0]).decode()
        enkey = base64.b64decode(router_msg[router_index][1]).decode()
        dekey = base64.b64decode(router_msg[router_index][6]).decode()
        receive_de = base64.b64decode(router_msg[router_index][7]).decode()
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_plain").setPlainText(send_plain)
        self.findChild(QtWidgets.QLineEdit, "lineEdit_enkey").setText(enkey)
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_en").setPlainText(router_msg[router_index][0])
        self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter_tosend").setValue(router_msg[router_index][3])
        self.findChild(QtWidgets.QSpinBox, "spinBox_receive_from").setValue(router_msg[router_index][4])
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_receive_en").setPlainText(receive_de)
        self.findChild(QtWidgets.QLineEdit, "lineEdit_dekey").setText(dekey)
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_receive_de").setPlainText(base64.b64decode(receive_de).decode())
        return

    def select_router_tosend(self):
        global router_msg
        router_msg[router_selected - 1][3] = self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter_tosend").value()
        return

    def save_allinput(self):
        global router_msg
        # textBrowser_send_plain、lineEdit_enkey、textBrowser_send_plain中的文本信息全部以base64编码存储
        router_msg[router_selected - 1][0] = base64.b64encode(self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_plain").toPlainText().encode()).decode()
        router_msg[router_selected - 1][1] = base64.b64encode(self.findChild(QtWidgets.QLineEdit, "lineEdit_enkey").text().encode()).decode()
        router_msg[router_selected - 1][2] = base64.b64encode(self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_en").toPlainText().encode()).decode()
        self.statusBar().showMessage("保存成功", 5000)
        return

    def base64(self):
        send_plain = self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_plain").toPlainText()
        send_plain_based = base64.b64encode(send_plain.encode()).decode()
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_en").setPlainText(send_plain_based)

    # 加密明文信息，调用./aes_128/aes_128.exe
    def aes_encrypt(self):
        target = self.findChild(QtWidgets.QSpinBox, "spinBox_selectrouter_tosend").value()
        send_plain = self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_plain").toPlainText()
        send_plain_based = base64.b64encode(send_plain.encode()).decode()
        enkey = self.findChild(QtWidgets.QLineEdit, "lineEdit_enkey").text()
        enkey_based = base64.b64encode(enkey.encode()).decode()
        # 输入的字符串不能超过64个字符
        if len(send_plain) > 64 or len(enkey) != 16:
            self.statusBar().showMessage("输入的字符串过长，或密钥不为16个字符", 5000)
            return
        if send_plain == "" or enkey == "":
            return

        aes_128_exe = "./aes_128/aes_128.exe"
        # input_data = send_plain + "\n" + enkey
        input_data = send_plain_based
        p = subprocess.Popen(aes_128_exe, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(input=input_data.encode())
        out_str = out.decode()
        out_list = out_str.split("\n")
        # 将out_list中的空字符串去掉
        out_list = [x for x in out_list if x != '']

        # 0发送base64的明文字符串、1加密密钥字符串、2发送的加密密文、3接收方、4发送方、5接收的加密密文、6解密密钥、7解密后的base64明文字符串
        router_msg[router_selected - 1][2] = out_list[5][5:].encode().decode()
        self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_en").setPlainText(send_plain_based)
        router_msg[target - 1][4] = int(router_selected)
        router_msg[target - 1][5] = base64.b64encode(out_list[5][6:].encode()).decode()
        router_msg[target - 1][6] = enkey_based
        router_msg[target - 1][7] = base64.b64encode(out_list[-1][6:-1].encode()).decode()

        router_msg[router_selected - 1][0] = base64.b64encode(self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_plain").toPlainText().encode()).decode()
        router_msg[router_selected - 1][1] = base64.b64encode(self.findChild(QtWidgets.QLineEdit, "lineEdit_enkey").text().encode()).decode()
        router_msg[router_selected - 1][2] = base64.b64encode(self.findChild(QtWidgets.QTextBrowser, "textBrowser_send_en").toPlainText().encode()).decode()
        self.statusBar().showMessage("保存并发送成功！！", 5000)
        return


# 判断导入文件是否合法，不合法则停用导入按钮
def check_importedges():
    if os.path.exists("config/edges.txt"):
        with open("config/edges.txt", "r") as f:
            edges = f.readlines()
        for i, edge in enumerate(edges):
            if i == 0:
                num = edge.split()
                if len(num) != 2:
                    return False
                router_num, link_num = num
                router_num = int(router_num)
                link_num = int(link_num)
                if router_num < 2 or router_num > 1000 or link_num < 1 or link_num > 1000:
                    return False
                continue
            edge = edge.split()
            if len(edge) != 4:
                return False
            if not edge[0].isdigit() or not edge[1].isdigit() or not edge[2].isdigit() or not edge[3].isdigit():
                return False
    else:
        return False
    return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.keys()[2])
    win = MainWindow()
    win.move(int((app.desktop().width() - win.width()) / 2), int((app.desktop().height() - win.height()) / 2))
    win.setWindowTitle("校园网路由设计 - Rrhar'il Team")
    win.setWindowIcon(QtGui.QIcon("resources/icon.png"))
    win.show()
    # 如果配置文件不合法，则停用导入按钮
    if not check_importedges():
        win.findChild(QtWidgets.QPushButton, "pushButton_importedges").setEnabled(False)
        win.findChild(QtWidgets.QAction, "action_import").setEnabled(True)
    sys.exit(app.exec_())

