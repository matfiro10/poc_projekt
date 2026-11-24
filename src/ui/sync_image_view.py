from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QWidget,
)


class SyncImageView(QGraphicsView):
    """Widok obrazu z przybliżaniem scrollem (pod kursor) i przesuwaniem myszką."""

    viewChanged = Signal()

    def __init__(
        self,
        placeholder: str,
        bg_color: str,
        text_color: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._placeholder = placeholder
        self._bg_color = QColor(bg_color)
        self._text_color = QColor(text_color)
        self._syncing = False

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem()
        self._pixmap_item.setTransformationMode(
            Qt.TransformationMode.FastTransformation
        )
        self._scene.addItem(self._pixmap_item)

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setBackgroundBrush(self._bg_color)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.horizontalScrollBar().valueChanged.connect(self._on_scrollbar_changed)
        self.verticalScrollBar().valueChanged.connect(self._on_scrollbar_changed)

    def _on_scrollbar_changed(self) -> None:
        if not self._syncing and self.has_pixmap():
            self.viewChanged.emit()

    def has_pixmap(self) -> bool:
        return not self._pixmap_item.pixmap().isNull()

    def set_pixmap(
        self, pixmap: QPixmap, reference_size: QSize | None = None
    ) -> None:
        self._syncing = True
        try:
            self._pixmap_item.setPixmap(pixmap)
            if pixmap.isNull():
                self._pixmap_item.setScale(1.0)
                self._scene.setSceneRect(QRectF())
                self.resetTransform()
                self.viewport().update()
                return

            if reference_size is not None and pixmap.width() > 0:
                scale_ratio = reference_size.width() / pixmap.width()
                self._pixmap_item.setScale(scale_ratio)
                self._scene.setSceneRect(
                    0.0,
                    0.0,
                    float(reference_size.width()),
                    float(reference_size.height()),
                )
            else:
                self._pixmap_item.setScale(1.0)
                self._scene.setSceneRect(
                    0.0, 0.0, float(pixmap.width()), float(pixmap.height())
                )

            self.viewport().update()
        finally:
            self._syncing = False

    def clear_image(self, placeholder: str | None = None) -> None:
        if placeholder is not None:
            self._placeholder = placeholder
        self.set_pixmap(QPixmap())

    def fit_image(self) -> None:
        if not self.has_pixmap():
            return
        self._syncing = True
        try:
            self.resetTransform()
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        finally:
            self._syncing = False

    def sync_from(self, other: "SyncImageView") -> None:
        if self._syncing or not self.has_pixmap() or not other.has_pixmap():
            return
        self._syncing = True
        try:
            self.setTransform(other.transform())
            self.horizontalScrollBar().setValue(other.horizontalScrollBar().value())
            self.verticalScrollBar().setValue(other.verticalScrollBar().value())
        finally:
            self._syncing = False

    def wheelEvent(self, event: QWheelEvent) -> None:
        if not self.has_pixmap():
            return

        delta = event.angleDelta().y()
        if delta == 0:
            return

        factor = 1.25 if delta > 0 else 1.0 / 1.25
        current_scale = self.transform().m11()

        if (factor > 1.0 and current_scale > 80.0) or (
            factor < 1.0 and current_scale < 0.1
        ):
            return

        self._syncing = True
        try:
            self.scale(factor, factor)
        finally:
            self._syncing = False

        self.viewChanged.emit()
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.has_pixmap():
            self.fit_image()
            self.viewChanged.emit()
        super().mouseDoubleClickEvent(event)

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawForeground(painter, rect)
        if not self.has_pixmap():
            painter.save()
            painter.resetTransform()
            painter.setPen(self._text_color)
            painter.drawText(
                self.viewport().rect(),
                Qt.AlignmentFlag.AlignCenter,
                self._placeholder,
            )
            painter.restore()