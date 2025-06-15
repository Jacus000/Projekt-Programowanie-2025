
import pandas as pd
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex



class PandasModel(QAbstractTableModel):
    def __init__(self, data=pd.DataFrame()):
        super().__init__()
        self._data=data

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]
    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]
    def data(self,index,role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role==Qt.ItemDataRole.DisplayRole:
                return str(self._data.iloc[index.row(),index.column()])
        return None#section bierze indeks kolumny/wiersza, orientation: vertical/horizontal, rola to wiadomo, funkcja sama sie wykonuje i QTableView sam ja obsluguje
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            elif orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        return None
    def updateData(self, new_data: pd.DataFrame):
        self.beginResetModel()
        self._data=new_data
        self.endResetModel()  


