"""
The name checker is intended for use by the verbal department within Addison Whitney;
This program offers several major functionalities:
1 - Takes in a list of created names as well as differet letter strings and existing names and checks the created naems against input avoids
  - There are also two other avoids, INN and Pharma, the databases for these are not loaded in here for confidentiality purposes
2 - Allows users to determine the .com domain name availability associated with each name using API request via Dynadot's application
3 - Takes in a list of names and build search keys for those names for either PIU (phonetic screens) or structure, trademark screens
There are
The current UI design is intended for use on Windows and will therefore look slightly wonky otherwise
"""

__author__ = "James Cristini"
__credits__ = ["James Cristini", 'Adam Tilly (for the "Cristini Genie" name)']
__version__ = "1.4"
__maintainer__ = "James Cristini"
__email__ = "jacristi0428@gmail.com"

import os
import sys
import sip
import string
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QThread, SIGNAL
from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QDialog, QTableWidgetItem, QMessageBox
from namechecker_ui import Ui_NameChecker
from build_lists import parse_names, write_avoids, build_project_avoids
from PHARMA_INN_AVOIDS_test import PHARMA_AVOIDS, INN_USAN_AVOIDS
from check_avoids import check_avoids, check_internal_names, check_competitor_names
from check_url import check_domain
from search_keys import get_keys


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        # self.ui = uic.loadUi('genie_ui.ui')
        self.ui = Ui_NameChecker()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('lamp.ico'))

        self.names_list = []
        self.stripped_names = []
        self.project_avoids = {
        "prefix" : [],
        "infix" : [],
        "suffix" : [],
        "anywhere" : [],
        "problems" : []
        }
        self.project_avoids_list = []
        self.internal_names = []
        self.competitor_names = []

        self.pharma_avoids = PHARMA_AVOIDS
        self.inn_avoids = INN_USAN_AVOIDS

        self.pharma_position_checks = [x for x in self.pharma_avoids]

        # Main Tab
        self.ui.commit_names_btn.clicked.connect(self.commit_names)
        self.ui.commit_names_btn.setShortcut("Ctrl+S")

        self.ui.name_rationale_label.mousePressEvent = self.sort_names_list
        self.ui.name_rationale_label_2.mousePressEvent = self.sort_stripped_names

        self.ui.title_btn.clicked.connect(self.all_title_case)
        self.ui.upper_btn.clicked.connect(self.all_upper_case)
        self.ui.lower_btn.clicked.connect(self.all_lower_case)

        self.ui.find_conflicts_btn.clicked.connect(self.find_conflicts)
        self.ui.find_conflicts_btn.setShortcut("Ctrl+Enter")

        self.ui.check_box_all.stateChanged.connect(self.check_uncheck)

        # Add Avoids Tab
        self.ui.save_avoids_btn.clicked.connect(self.save_avoids)
        self.ui.save_avoids_btn.setShortcut("Ctrl+S")
        self.ui.clear_avoids_btn.clicked.connect(self.clear_avoids)
        self.get_avoids_from_file()
        self.show_avoids()

        # URL Tab
        self.ui.get_url_btn.clicked.connect(self.check_url)
        self.ui.get_url_btn.setShortcut("Ctrl+Enter")
        self.ui.url_progress_bar.setRange(0,1)

        # Pharma Avoids Tab
        self.ui.pharma_avoid_table.verticalHeader().hide()
        self.ui.pharma_avoid_table.setSortingEnabled(True)
        self.ui.find_pharma_avoid_btn.clicked.connect(self.search_pharma)
        self.ui.pharma_search_line.returnPressed.connect(self.search_pharma)
        self.show_pharma_avoids()

        # INN Avoids Tab
        self.ui.inn_avoid_table.verticalHeader().hide()
        self.ui.inn_avoid_table.setSortingEnabled(True)
        self.ui.find_inn_avoid_btn.clicked.connect(self.search_inn)
        self.ui.inn_search_line.returnPressed.connect(self.search_inn)
        self.show_inn_avoids()

        # Search Key tab
        self.ui.PIU_radio.setChecked(True)
        self.ui.search_names_label.mousePressEvent = self.sort_search_names
        self.ui.search_key_label.mousePressEvent = self.sort_search_keys
        self.ui.get_keys_btn.clicked.connect(self.get_search_keys)


        # Exit app
        self.ui.exit_btn.clicked.connect(self.close_app)
        self.ui.exit_btn.setShortcut("Ctrl+Q")

        #self.ui.show()

    # ----Main Tab Functions---- #
    def commit_names(self):
        self.stripped_names, self.names_list = parse_names(str(self.ui.textEdit_names.toPlainText()))
        self.ui.textBrowser_url.setText("\n".join(["--- : " + x for x in self.stripped_names]))
        self.ui.plainTextEdit_search_names.setPlainText("\n".join(self.stripped_names))
        self.show_names()

    def all_upper_case(self):
        self.stripped_names = [x.upper() for x in self.stripped_names]
        self.show_names()

    def all_lower_case(self):
        self.stripped_names = [x.lower() for x in self.stripped_names]
        self.show_names()

    def all_title_case(self):
        self.stripped_names = [x.title() for x in self.stripped_names]
        self.show_names()

    def sort_stripped_names(self, event):
        self.stripped_names.sort()
        self.show_names()

    def sort_names_list(self, event):
        self.names_list.sort()
        self.show_names()

    def sort_search_names(self, event):
        search_names_list = str(self.ui.plainTextEdit_search_names.toPlainText()).split("\n")
        self.ui.plainTextEdit_search_names.setPlainText("\n".join(sorted([x.strip(string.whitespace) for x in search_names_list if x.strip(string.whitespace)])))

    def sort_search_keys(self, event):
        search_key_list = str(self.ui.textBrowser_search_keys.toPlainText()).split("\n")
        self.ui.textBrowser_search_keys.setPlainText("\n".join(sorted([x.strip(string.whitespace) for x in search_key_list if x.strip(string.whitespace)])))

    def show_names(self):
        self.ui.textBrowser_stripped.setPlainText("\n".join(self.stripped_names))
        self.ui.textEdit_names.setPlainText("\n".join([x.strip(string.whitespace) for x in self.names_list if x.strip(string.whitespace)]))
        self.ui.plainTextEdit_search_names.setPlainText("\n".join([ x.strip(string.whitespace) for x in self.stripped_names if x.strip(string.whitespace)]))

    def check_uncheck(self):
        if self.ui.check_box_all.isChecked() :
            self.check_all_boxes()
        else :
            self.uncheck_all_boxes()

    def check_all_boxes(self):
        self.ui.check_box_pharma.setChecked(True)
        self.ui.check_box_inn.setChecked(True)
        self.ui.check_box_project.setChecked(True)
        self.ui.check_box_internal.setChecked(True)
        self.ui.check_box_competitor.setChecked(True)

    def uncheck_all_boxes(self):
        self.ui.check_box_pharma.setChecked(False)
        self.ui.check_box_inn.setChecked(False)
        self.ui.check_box_project.setChecked(False)
        self.ui.check_box_internal.setChecked(False)
        self.ui.check_box_competitor.setChecked(False)

    def find_conflicts(self):
        checks = 0
        # Get user's input for stem(s) to ignore
        ignore = self.ui.lineEdit_ignore.text()
        self.save_avoids()
        self.commit_names()

        # Start with blank text each time conflict checks are run
        text = "<p style =\" white-space: pre-wrap;\" >"

        if len(self.names_list) == 0 :
            QMessageBox.warning(self, "No Names", "No names entered")
        else:

            # Check names against INN avoids - return html text with avoid highlighted in red within name
            if self.ui.check_box_inn.isChecked() :
                text += "<h3>INN Avoid Conflicts</h3>" + check_avoids(self.stripped_names, self.inn_avoids, "inn", ignore)
                checks += 1

            # Check names against Pharma avoids - return html text with avoid highlighted in red within name
            if self.ui.check_box_pharma.isChecked() :
                text += "<h3>Pharma Avoid Conflicts</h3>" + check_avoids(self.stripped_names, self.pharma_avoids, "pharma", self.inn_avoids)
                checks += 1

            # Check names against project avoids - return html text with avoid highlighted in red within name
            if self.ui.check_box_project.isChecked() :
                text += "<h3>Project Avoid Conflicts</h3>" + check_avoids(self.stripped_names, self.project_avoids, "project")
                checks += 1

            # Check names against internal/presented names and return html text listing the conflicts
            if self.ui.check_box_internal.isChecked() :
                text += "<h3>Internal/Presented Name Conflicts:</h3>" + check_internal_names(self.stripped_names, self.internal_names)
                checks += 1

            # Check names against competitor names and return html text listing the conflicts and with conflicting strings in red
            if self.ui.check_box_competitor.isChecked() :
                text += "<h3>Competitor Name Conflicts:</h3>" + check_competitor_names(self.stripped_names, self.competitor_names)
                checks += 1
            if checks == 0 :
                QMessageBox.warning(self, "No avoids checked", "No avoids checked!")

        text += "</p>"

        self.ui.textBrowser_conflicts.setText(text)

    def close_app(self):
        choice = QtGui.QMessageBox.question(self, "Quit", "Leave?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if choice == QtGui.QMessageBox.Yes :
            print "Yes: Exiting..."
            sys.exit()
        else :
            print "No: Not exiting..."
            pass

    # ----Avoids Tab Functions---- #
    def save_avoids(self):
        print "SAVING AVOIDS"
        allowed_chars = string.letters + string.digits + '\n-"()/,'

        #First converts any special characters (e.g smart quotes to staright quotes or em dashes to regular deshes) then splits each item into a list
        text_in = (str(self.ui.plainTextEdit_project.toPlainText()).replace(u"\u2018", '"').replace(u"\u2019", '"').\
        replace(u"\u201c",'"').replace(u"\u201d", '"').replace(u"\u2013", "-"))

        # Filters out any non-allowed characters
        p_text = "".join([x for x in text_in if x in allowed_chars or x == " "])

        # Strip each avoid of any extra whitespace characters then send to build_project_avoids to get a sorted dictionary
        self.project_avoids_list = [str(x).strip(string.whitespace) for x in p_text.split("\n") if x.strip()]
        self.project_avoids = build_project_avoids(self.project_avoids_list)
        self.project_avoids_list = \
            sorted([x.lower() + "-" for x in self.project_avoids["prefix"]]) + \
            sorted(['"' + x.lower() + '"' for x in self.project_avoids["anywhere"]]) + \
            sorted(["-" + x.lower() for x in self.project_avoids["suffix"]]) + \
            sorted([x for x in self.project_avoids["problems"]])


        # Take in all names listed under presented/internal names
        if str(self.ui.plainTextEdit_internal.toPlainText()):
            i_text = "".join([x for x in str(self.ui.plainTextEdit_internal.toPlainText()) if x in allowed_chars] or x == " ")
            # Split text on the \n and strips whitespace leaving out any lines that are purely whitespace
            self.internal_names = [x.strip(string.whitespace) for x in i_text.split("\n") if x or x.strip(string.whitespace)]
        else:
            self.internal_names = []

        # Take in all names listed under presented/internal names
        if str(self.ui.plainTextEdit_competitor.toPlainText()):
            c_text = "".join([x for x in str(self.ui.plainTextEdit_competitor.toPlainText()) if x in allowed_chars or x == " "])
            # Split text on the \n and strips whitespace leaving out any lines that are purely whitespace
            self.competitor_names = [x.strip(string.whitespace) for x in c_text.split("\n") if x.strip(string.whitespace)]
        else:
            self.competitor_names = []

        write_avoids(self.project_avoids_list, sorted(set(self.internal_names)), sorted(set(self.competitor_names)))
        self.get_avoids_from_file()
        self.show_avoids()

    def clear_avoids(self):
        choice = QtGui.QMessageBox.question(self, "Quit", "Clear all avoids?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if choice == QtGui.QMessageBox.Yes :
            with open("avoids.txt", "w")as f:
                f.close()
            del self.project_avoids_list[:]
            self.ui.plainTextEdit_project.clear()
            del self.internal_names[:]
            self.ui.plainTextEdit_internal.clear()
            del self.competitor_names[:]
            self.ui.plainTextEdit_competitor.clear()

            # Deleted the avoids.txt file when clearing avoids
            try:
                os.remove("avoids.txt")
            except Exception as e:
                print e
            self.show_avoids()
        else :
            pass

    def get_avoids_from_file(self) :
        try:
            with open("avoids.txt", "r") as f:
                for line in f:
                    if line[0:4] == "Proj":
                        self.project_avoids_list = line.strip("Project:").strip(string.whitespace).split(",")
                    if line[0:4] == "Inte":
                        self.internal_names = line.strip("Internal:").strip(string.whitespace).split(",")
                    if line[0:4] == "Comp":
                        self.competitor_names = line.strip("Competitor:").strip(string.whitespace).split(",")
            f.close()
        except Exception as e:
            print e

    def show_avoids(self):
        if self.project_avoids_list :
            self.ui.plainTextEdit_project.setPlainText("\n".join(self.project_avoids_list))
        if self.internal_names :
            self.ui.plainTextEdit_internal.setPlainText("\n".join(sorted(set(self.internal_names))))
        if self.competitor_names :
            self.ui.plainTextEdit_competitor.setPlainText("\n".join(sorted(set(self.competitor_names))))

    # ----URL Tab Functions---- #
    def check_url(self):
        if self.stripped_names:
            self.ui.url_progress_bar.setRange(0,0)
            self.ui.get_url_btn.setEnabled(False)
            self.ui.commit_names_btn.setEnabled(False)
            self.new_url_thread = CheckUrlThread(self.stripped_names)
            self.connect(self.new_url_thread, SIGNAL("finished()"), self.check_url_done)
            self.new_url_thread.start()
        else:
            QMessageBox.warning(self, "No Names", "No names entered")

    def check_url_done(self):
        self.ui.url_progress_bar.setRange(0,1)
        self.ui.get_url_btn.setEnabled(True)
        self.ui.commit_names_btn.setEnabled(True)
        self.ui.textBrowser_url.setText(self.url_info_text)
        QtGui.QMessageBox.information(self, "Done!", "URL check finished!")

    # ----Pharma/INN Tab Functions---- #
    def search_pharma(self):
        pharma_search_item = str(self.ui.pharma_search_line.text()).strip(string.whitespace).lower()
        for row in xrange(0,self.ui.pharma_avoid_table.rowCount()):
            if self.ui.pharma_avoid_table.item(row, 1).text() == pharma_search_item:
                self.ui.pharma_avoid_table.scrollToItem(self.ui.pharma_avoid_table.item(row, 1), QtGui.QAbstractItemView.PositionAtTop)
                self.ui.pharma_avoid_table.setItemSelected(self.ui.pharma_avoid_table.item(row, 1), True)
                self.ui.pharma_avoid_table.setFocus(True)

    def show_pharma_avoids(self):
        self.ui.pharma_avoid_table.setColumnCount(3)
        self.ui.pharma_avoid_table.setHorizontalHeaderLabels(["Position", "Avoid", "Definiton"])

        for pos in self.pharma_position_checks:
            for avoid in self.pharma_avoids[pos]:
                rowPosition = self.ui.pharma_avoid_table.rowCount()
                self.ui.pharma_avoid_table.insertRow(rowPosition)
                self.ui.pharma_avoid_table.setItem(rowPosition, 0, QTableWidgetItem(pos.title()))
                self.ui.pharma_avoid_table.setItem(rowPosition, 1, QTableWidgetItem(avoid))
                self.ui.pharma_avoid_table.setItem(rowPosition, 2, QTableWidgetItem(self.pharma_avoids[pos][avoid]))

        header = self.ui.pharma_avoid_table.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.ui.pharma_avoid_table.sortItems(0)

    def search_inn(self):
        inn_search_item = str(self.ui.inn_search_line.text()).strip(string.whitespace).lower()
        for row in xrange(0,self.ui.inn_avoid_table.rowCount()):
            if self.ui.inn_avoid_table.item(row, 1).text() == inn_search_item:
                self.ui.inn_avoid_table.scrollToItem(self.ui.inn_avoid_table.item(row, 1), QtGui.QAbstractItemView.PositionAtTop)
                self.ui.inn_avoid_table.setItemSelected(self.ui.inn_avoid_table.item(row, 1), True)
                self.ui.inn_avoid_table.setFocus(True)

    def show_inn_avoids(self):
        self.ui.inn_avoid_table.setColumnCount(3)
        self.ui.inn_avoid_table.setHorizontalHeaderLabels(["Position", "Avoid", "Definiton"])
        checked_positions = []

        for pos in self.inn_avoids:
            for avoid in self.inn_avoids[pos]:
                rowPosition = self.ui.inn_avoid_table.rowCount()
                self.ui.inn_avoid_table.insertRow(rowPosition)
                self.ui.inn_avoid_table.setItem(rowPosition, 0, QTableWidgetItem(pos.title()))
                self.ui.inn_avoid_table.setItem(rowPosition, 1, QTableWidgetItem(avoid))
                self.ui.inn_avoid_table.setItem(rowPosition, 2, QTableWidgetItem(self.inn_avoids[pos][avoid]))

        header = self.ui.inn_avoid_table.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.ui.inn_avoid_table.sortItems(0)

    # ----Search Pal Tab Functions---- #
    def get_search_keys(self):
        names_for_keys, list1 = parse_names(str(self.ui.plainTextEdit_search_names.toPlainText()))
        self.ui.plainTextEdit_search_names.setPlainText("\n".join(names_for_keys))

        if self.ui.structural_radio.isChecked():
            key_type = "structural"
        elif self.ui.or_radio.isChecked():
            key_type = "or"
        elif self.ui.or_asterisk_radio.isChecked():
            key_type = "*or*"
        else:
            key_type = "piu"

        if names_for_keys:
            self.new_search_key_thread = SearchKeyThread(key_type, names_for_keys)
            self.connect(self.new_search_key_thread, SIGNAL("finished()"), self.search_key_done)
            self.new_search_key_thread.start()
        else:
            QMessageBox.warning(self, "No Names", "No names entered!")

    def search_key_done(self):
        print "FINISHED GETTING SEARCH KEYS"
        self.ui.textBrowser_search_keys.setPlainText(self.search_key_text)


class CheckUrlThread(QThread):
    def __init__(self, stripped_names):
        QThread.__init__(self)
        self.stripped_names = stripped_names

    def __del__(self):
        self.wait()

    def run(self):
        url_text = check_domain(self.stripped_names)
        NameChecker.url_info_text = url_text


class SearchKeyThread(QThread):
    def __init__(self, key_type, stripped_names):
        QThread.__init__(self)
        self.stripped_names = stripped_names
        self.key_type = key_type

    def __del__(self):
        self.wait()

    def run(self):
        NameChecker.search_key_text = get_keys(self.key_type, self.stripped_names)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")

    NameChecker = MainWindow()
    NameChecker.show()

    sip.setdestroyonexit(False)
    sys.exit(app.exec_())
