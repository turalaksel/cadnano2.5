
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QFont, QPen, QPolygonF, QPainterPath, QFontMetrics
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsSimpleTextItem, QUndoCommand, QGraphicsRectItem

from cadnano.enum import StrandType
from cadnano.gui.palette import getPenObj, getBrushObj, getSolidBrush
from . import pathstyles as styles
from .prexoveritem import PreXoverItem


# construct paths for breakpoint handles
def _hashMarkGen(path, p1, p2, p3):
    path.moveTo(p1)
    path.lineTo(p3)
# end

# create hash marks QPainterPaths only once
_PP_RECT = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
_PATH_CENTER = QPointF(styles.PATH_BASE_WIDTH / 2,\
                          styles.PATH_BASE_WIDTH / 2)
_PATH_U_CENTER = QPointF(styles.PATH_BASE_WIDTH / 2, 0)
_PATH_D_CENTER = QPointF(styles.PATH_BASE_WIDTH / 2, styles.PATH_BASE_WIDTH)
_PPATH_LU = QPainterPath()
_hashMarkGen(_PPATH_LU, _PP_RECT.bottomLeft(), _PATH_D_CENTER, _PATH_CENTER)
_PPATH_RU = QPainterPath()
_hashMarkGen(_PPATH_RU, _PP_RECT.bottomRight(), _PATH_D_CENTER, _PATH_CENTER)
_PPATH_RD = QPainterPath()
_hashMarkGen(_PPATH_RD, _PP_RECT.topRight(), _PATH_U_CENTER, _PATH_CENTER)
_PPATH_LD = QPainterPath()
_hashMarkGen(_PPATH_LD, _PP_RECT.topLeft(), _PATH_U_CENTER, _PATH_CENTER)

_SCAF_PEN = getPenObj(styles.PXI_SCAF_STROKE,
                    styles.PATH_STRAND_STROKE_WIDTH,
                    capstyle=Qt.FlatCap,
                    joinstyle=Qt.RoundJoin)
_STAP_PEN = getPenObj(styles.PXI_STAP_STROKE,
    styles.PATH_STRAND_STROKE_WIDTH,
    capstyle=Qt.FlatCap,
    joinstyle=Qt.RoundJoin)
_DISAB_PEN = getPenObj(styles.PXI_DISAB_STROKE,
            styles.PATH_STRAND_STROKE_WIDTH,
            capstyle=Qt.FlatCap,
            joinstyle=Qt.RoundJoin)
_DISAB_BRUSH = getBrushObj(styles.PXI_DISAB_STROKE)  # For the helix number label
_ENAB_BRUSH = getSolidBrush()  # Also for the helix number label
_BASE_WIDTH = styles.PATH_BASE_WIDTH
_RECT = QRectF(0, 0, styles.PATH_BASE_WIDTH, 1.2*styles.PATH_BASE_WIDTH)
_TO_HELIX_NUM_FONT = styles.XOVER_LABEL_FONT
# precalculate the height of a number font.  Assumes a fixed font
# and that only numbers will be used for labels
_FM = QFontMetrics(_TO_HELIX_NUM_FONT)


class PreXoverPItem(PreXoverItem):
    def __init__(self, from_virtual_helix_item, to_virtual_helix_item, index, strand_type, is_low_idx):
        super().__init__(from_virtual_helix_item, to_virtual_helix_item, index, strand_type, is_low_idx)
    # end def

    ### DRAWING METHODS ###
    def setPainterPath(self):
        """
        Sets the PainterPath according to the index (low = Left, high = Right)
        and strand position (top = Up, bottom = Down).
        """
        path_LUT = (_PPATH_RD, _PPATH_RU, _PPATH_LD, _PPATH_LU)  # Lookup table
        vhi = self._from_vh_item
        st = self._strand_type
        path = path_LUT[2*int(self._is_low_index) + int(vhi.isStrandTypeOnTop(st))]
        self.setPath(path)
    # end def

    def updateStyle(self):
        """
        If a PreXover can be installed the pen is a bold color,
        otherwise the PreXover is drawn with a disabled or muted color
        """
        from_vh = self._from_vh_item.virtualHelix()
        to_vh = self._to_vh_item.virtualHelix()
        part = self._from_vh_item.part()
        pen = _DISAB_PEN
        self._label_brush = _DISAB_BRUSH
        if part.isPossibleXoverP(from_vh, to_vh, self._strand_type, self._idx):
            pen = self._pen
            self._is_active = True
            self._label_brush = _ENAB_BRUSH
        self.setPen(pen)
    # end def

    ### TOOL METHODS ###

    def mousePress(self, event):
        if event.button() != Qt.LeftButton:
            return QGraphicsPathItem.mousePressEvent(self, event)

        if event.modifiers() & Qt.ShiftModifier:
            return  # ignore shift click, user is probably trying to merge

        if self._is_active:
            from_vh = self._from_vh_item.virtualHelix()
            to_vh = self._to_vh_item.virtualHelix()
            from_ss = from_vh.getStrandSetByType(self._strand_type)
            to_ss = to_vh.getStrandSetByType(self._strand_type)
            from_strand = from_ss.getStrand(self._idx)
            to_strand = to_ss.getStrand(self._idx)
            part = self._from_vh_item.part()
            # determine if we are a 5' or a 3' end
            if self.path() in [_PPATH_LU, _PPATH_RD]:  # 3' end of strand5p clicked
                strand5p = from_strand
                strand3p = to_strand
            else:  # 5'
                strand5p = to_strand
                strand3p = from_strand

            from_idx = self._idx
            from_strand = from_ss.getStrand(from_idx)

            part = self._from_vh_item.part()

            # determine if we are a 5' or a 3' end
            if self.path() in [_PPATH_LU, _PPATH_RD]:  # 3' end of strand5p clicked
                if self.path() == _PPATH_LU: # on top
                    to_idx = from_idx + 1
                else:
                    to_idx = from_idx - 1

                to_strand = to_ss.getStrand(to_idx)

                strand5p = from_strand
                strand3p = to_strand
                idx5p = from_idx
                idx3p = to_idx
            else:  # 5'
                if self.path() == _PPATH_RU: # on top
                    to_idx = from_idx - 1
                else:
                    to_idx = from_idx + 1

                to_strand = to_ss.getStrand(to_idx)

                strand5p = to_strand
                strand3p = from_strand
                idx5p = to_idx
                idx3p = from_idx

            # Gotta clear selections when installing a prexover
            # otherwise parenting is screwed up
            self._from_vh_item.viewroot().clearStrandSelections()
            part.createXover(strand5p, idx5p, strand3p, idx3p)
        else:
            event.setAccepted(False)
    # end def