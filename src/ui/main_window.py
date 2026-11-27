from PySide6 import QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,

)



from src.core.image_upscaler import ImageUpscaler, InterpolationAlgorithm, ScaleFactor
from src.ui.sync_image_view import SyncImageView
from src.ui.ui_helpers import (
    ask_open_image_path,
    ask_save_image_path,
    format_resolution_banner,
    show_info,
    show_warning,
)
from src.ui.translations import (text)
from src.utils.qt_image_utils import ImageIOError
from pathlib import Path



ICONS_DIR = Path(__file__).resolve().parent.parent / "icons"


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self._upscaler = ImageUpscaler()
        self._lang = "pl"
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
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
        self._info_label.setFont(QFont('Arial', 15, QFont.Weight.Bold))
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._info_label)




        self._content_layout = QHBoxLayout()
        self._main_layout.addLayout(self._content_layout, 1)


        ## 1 Layout left
        self._left_panel = QWidget()


        self._left_layout = QVBoxLayout(self._left_panel)


        self._left_view = SyncImageView(
            placeholder="Obraz", bg_color="#333333", text_color="#FFFFFF"
        )

        self._left_layout.addWidget(self._left_view, 1)
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
            QPushButton:hover {
                background-color: #D5D5D5;
            }
        """)



        self._center_button_load = QPushButton("Wczytaj obraz")
        self._center_button_other = QPushButton("Skaluj")
        self._center_button_rest = QPushButton("Resetuj")
        self._center_button_export = QPushButton("Export")
        self._center_button_fit = QPushButton("Dopasuj widok")

        self._center_opis_label = QLabel("Metoda:")
        self._center_opis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._center_opis_label.setStyleSheet("color: black")

        self._center_chose_method = QComboBox()
        for algo in InterpolationAlgorithm:
            self._center_chose_method.addItem(algo.label, algo)

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

        self._center_scale_label = QLabel("Skala:")
        self._center_scale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._center_scale_label.setStyleSheet("color: black")

        self._center_chose_scale = QComboBox()
        for factor in ScaleFactor:
            self._center_chose_scale.addItem(factor.label, factor)
        self._center_chose_scale.setCurrentIndex(
            list(ScaleFactor).index(self._upscaler.scale)
        )
        self._center_chose_scale.setMinimumHeight(35)
        self._center_chose_scale.setStyleSheet("""
            QComboBox {
                background-color: #E1E1E1;
                color: black;
                border: 1px solid #ADADAD;
            }
            QComboBox QAbstractItemView {
                color: black;
            }
        """)

        self._center_button_change = QPushButton("")
        self._center_button_change.setIcon(QIcon(str(ICONS_DIR / "pl.svg")))
        self._center_button_change.setStyleSheet("""
            border: none;
            background-color: #F0F0F0;
        """)
        self._center_button_change.setIconSize(QSize(70, 60))


        self._center_layout.addWidget(self._center_button_load)
        self._center_layout.addWidget(self._center_button_other)
        self._center_layout.addWidget(self._center_button_rest)
        self._center_layout.addWidget(self._center_button_export)
        self._center_layout.addWidget(self._center_button_fit)
        self._center_layout.addWidget(self._center_opis_label)
        self._center_layout.addWidget(self._center_chose_method)
        self._center_layout.addWidget(self._center_scale_label)
        self._center_layout.addWidget(self._center_chose_scale)
        self._center_layout.addWidget(self._center_button_change)

        self._content_layout.addWidget(self._center_panel)
        self._center_layout.addStretch()





        ## 3 Layout right
        self._right_panel = QWidget()
        self._right_panel.setStyleSheet("background-color: white;")

        self._right_layout = QVBoxLayout(self._right_panel)

        self._right_view = SyncImageView(
            placeholder="Wynik", bg_color="#FFFFFF", text_color="#666666"
        )
        self._right_layout.addWidget(self._right_view, 1)

        self._content_layout.addWidget(self._right_panel, 1)

        self._apply_language()




    def _connect_signals(self) -> None:
        self._center_button_load.clicked.connect(self._on_load_image)
        self._center_button_other.clicked.connect(self._on_process_image)
        self._center_button_rest.clicked.connect(self._on_reset)
        self._center_button_export.clicked.connect(self._on_export)
        self._center_button_fit.clicked.connect(self._on_fit_view)
        self._center_button_change.clicked.connect(self._on_change_language)
        self._center_chose_method.currentIndexChanged.connect(self._on_method_changed)
        self._center_chose_scale.currentIndexChanged.connect(self._on_scale_changed)


        self._left_view.viewChanged.connect(
            lambda: self._right_view.sync_from(self._left_view)
        )
        self._right_view.viewChanged.connect(
            lambda: self._left_view.sync_from(self._right_view)
        )

    def _on_load_image(self) -> None:
        file_path = ask_open_image_path(self)
        if not file_path:
            return

        try:
            self._upscaler.load_image(file_path)
        except ImageIOError as exc:
            show_warning(self, self.t["msg_load_error"], str(exc))
            return

        orig_pixmap = self._upscaler.get_original_pixmap()
        self._left_view.set_pixmap(orig_pixmap)
        self._left_view.fit_image()

        self._right_view.clear_image(self.t["right_view_scale"])
        self._info_label.setText(
            f"Oryginał: {orig_pixmap.width()}x{orig_pixmap.height()} px"
        )

    def _on_process_image(self) -> None:
        if not self._upscaler.has_image:
            show_info(self, self.t["msg_info_title"], self.t["msg_no_image"])
            return

        try:
            res = self._upscaler.process()
        except ImageIOError as exc:
            show_warning(self, self.t["msg_process_error"], str(exc))
            return

        orig_pixmap = self._upscaler.get_original_pixmap()
        res_pixmap = self._upscaler.get_result_pixmap(auto_process=False)

        self._right_view.set_pixmap(res_pixmap, reference_size=orig_pixmap.size())
        self._right_view.sync_from(self._left_view)

        rh, rw = res.shape[:2]
        self._info_label.setText(
            format_resolution_banner(
                orig_pixmap.width(),
                orig_pixmap.height(),
                rw,
                rh,
                self._upscaler.algorithm.label,
                self._upscaler.scale.label,
            )
        )

    def _on_reset(self) -> None:
        self._upscaler = ImageUpscaler(
            default_scale=ScaleFactor(self._center_chose_scale.currentData()),
            default_algorithm=InterpolationAlgorithm(
                self._center_chose_method.currentData()
            ),
        )
        self._left_view.clear_image("")
        self._right_view.clear_image("")
        self._info_label.setText("")

        self._apply_language()


    def _on_export(self) -> None:
        if not self._upscaler.has_image:
            show_info(self, "Export", "Najpierw wczytaj obraz.")
            return

        save_path = ask_save_image_path(self)
        if not save_path:
            return

        try:
            self._upscaler.save_result(save_path, auto_process=True)
            if not self._right_view.has_pixmap():
                orig_pixmap = self._upscaler.get_original_pixmap()
                res_pixmap = self._upscaler.get_result_pixmap(auto_process=False)
                self._right_view.set_pixmap(
                    res_pixmap, reference_size=orig_pixmap.size()
                )
                self._right_view.sync_from(self._left_view)
        except ImageIOError as exc:
            show_warning(self, self.t["msg_save_error"], str(exc))

    def _on_fit_view(self) -> None:
        self._left_view.fit_image()
        self._right_view.fit_image()

    def _on_method_changed(self) -> None:
        selected_algo = InterpolationAlgorithm(self._center_chose_method.currentData())
        self._upscaler.algorithm = selected_algo
        if self._upscaler.has_image:
            self._right_view.clear_image(f"Zmieniono metodę na: {selected_algo.label}")

    def _on_scale_changed(self) -> None:
        selected_scale = ScaleFactor(self._center_chose_scale.currentData())
        self._upscaler.scale = selected_scale
        if self._upscaler.has_image:
            self._right_view.clear_image(f"Zmieniono skalę na: {selected_scale.label}")


    def _apply_language(self) -> None:
        self.t = text[self._lang]

        self.setWindowTitle(self.t["window_title"])
        self._center_button_load.setText(self.t["button_load"])
        self._center_button_other.setText(self.t["button_other"])
        self._center_button_rest.setText(self.t["button_rest"])
        self._center_button_export.setText(self.t["button_export"])
        self._center_button_fit.setText(self.t["button_fit"])
        self._center_opis_label.setText(self.t["opis_label"])
        self._center_scale_label.setText(self.t["scale_label"])

        self._flag_on_change()

        if not self._upscaler.has_image:
            self._info_label.setText(self.t["info_label"])


        if not self._left_view.has_pixmap():
            self._left_view.clear_image(self.t["left_view"])

        if not self._right_view.has_pixmap():
            if self._upscaler.has_image:
                self._right_view.clear_image(self.t["right_view_scale"])
            else:
                self._right_view.clear_image(self.t["right_view"])












    def _on_change_language(self) -> None:
        if self._lang == "pl":
            self._lang = "en"
        else:
            self._lang = "pl"

        self._apply_language()


    def _flag_on_change(self) -> None:
        if self._lang == "pl":
            self._center_button_change.setIcon(QIcon(str(ICONS_DIR / "pl.svg")))
        else:
            self._center_button_change.setIcon(QIcon(str(ICONS_DIR / "gb.svg")))







