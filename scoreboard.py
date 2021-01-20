import sys
import sqlite3
from PyQt5.QtWidgets import *

#DB연결
conn = sqlite3.connect("./resource/records.db", isolation_level=None)
cursor = conn.cursor()

cursor.execute('select * from records')

db_length = len(cursor.fetchall())          #현재 있는 DB 행의 개수


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setTable()
        self.setWindowTitle('ScoreBoard')
        self.move(750, 100)
        self.resize(600, 800)
        self.show()
    
    def setTable(self):
      
        self.tableWidget = QTableWidget(self)
        self.tableWidget.resize(600,500)
        self.tableWidget.move(0,20)
        self.tableWidget.setColumnCount(4)  #테이블 가로 개수
        self.tableWidget.setRowCount(db_length) #테이블 세로 개수
        
        #table 헤더 라벨
        self.tableWidget.setHorizontalHeaderLabels(['이름','나이'])

        
        #테이블 아이템 입력



        #테이블 각 셀의 스타일 세팅
        # 셀의 백그라운드 설정
        #UI_set.tableWidget.item(0, 0).setBackground(QtGui.QColor("#FF0000"))
        #셀안의 텍스트의 정렬 설정
        #UI_set.tableWidget.item(0, 0).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        #셀안의 텍스트 폰트 설정
        #font = QtGui.QFont("맑은 고딕", 16, QtGui.QFont.Normal)
        #UI_set.tableWidget.item(0, 0).setFont(font)
        #테이블 값 입력
        #UI_set.tableWidget.item(0, 0).setText("홍길동")

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyWindow()
   sys.exit(app.exec_())