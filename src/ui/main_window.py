from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QComboBox
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Image Rescaling Benchmark Tool")
        self.resize(1200, 800)


        ## Widgety
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        central_widget.setStyleSheet("background-color: #F0F0F0;")

        self.setCentralWidget(central_widget)
        self._main_layout = QVBoxLayout(central_widget)



        self._info_label = QLabel("Skalowanie obrazu")
        self._info_label.setStyleSheet("color: black")
        # self._info_label.setMinimumSize(400,100)
        self._info_label.setFont(QFont('Arial', 15,QFont.Weight.Bold))
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)




        self._content_layout = QHBoxLayout()
        self._main_layout.addLayout(self._content_layout)


        ## 1 Layout left
        self._left_panel = QWidget()


        self._left_layout = QVBoxLayout(self._left_panel)


        self._left_label = QLabel("Obraz")
        self._left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._left_label.setStyleSheet("background-color: #333333;")

        self._left_layout.addWidget(self._info_label)
        self._left_layout.addWidget(self._left_label,1)
        self._content_layout.addWidget(self._left_panel, 1)




        ## 2 Layout center
        self._center_panel = QWidget()
        self._center_panel.setFixedWidth(190)
        self._center_layout = QVBoxLayout(self._center_panel)
        self._center_panel.setStyleSheet("""
            QPushButton {
                background-color: #E1E1E1;
                border: 1px solid #ADADAD;
                min-height: 40px;
                color:black;
            }
        """)



        self._center_button_load = QPushButton("Wczytaj obraz")
        self._center_button_other = QPushButton("Inny obraz")
        self._center_button_rest = QPushButton("Resetuj")
        self._center_button_export = QPushButton("Export")

        self._center_opis_label = QLabel("Metoda:")
        self._center_opis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._center_opis_label.setStyleSheet("color: black")

        self._center_chose_method = QComboBox()
        self._center_chose_method.addItem("Metoda1:")
        self._center_chose_method.addItem("Metoda2:")

        self._center_chose_method.setMinimumHeight(35)
        self._center_chose_method.setStyleSheet("""
            QComboBox {
                background-color: #E1E1E1;
                color: black;
                border: 1px solid #ADADAD;
            }
            QComboBox QAbstractItemView {
            color: black;
            }
        """)

        self._center_layout.addSpacing(29)
        self._center_layout.addWidget(self._center_button_load)
        self._center_layout.addWidget(self._center_button_other)
        self._center_layout.addWidget(self._center_button_rest)
        self._center_layout.addWidget(self._center_button_export)
        self._center_layout.addWidget(self._center_opis_label)
        self._center_layout.addWidget(self._center_chose_method)

        self._content_layout.addWidget(self._center_panel)
        self._center_layout.addStretch()





        ## 3 Layout right
        self._right_panel = QWidget()
        self._right_panel.setStyleSheet("background-color: white;")

        self._right_layout = QVBoxLayout(self._right_panel)


        self._content_layout.addWidget(self._right_panel, 1)






















