from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import *
import vector_model


# self.sri_type.addItem('Modelo Vectorial')
#         self.dataset.addItem('cranfield')

#         vectormodel= vector_model.VectorModel()

#         self.models= {'VectorModel':vectormodel}

#         self.run.clicked.connect(lambda: click_search(self.query,
#                                             self.sri_type,
#                                             self.dataset,
#                                             self.umbral,
#                                             self.umbralCheck,
#                                             self.sensitive,
#                                             self.alpha,
#                                             self.alphaCheck,
#                                             self.lim,
#                                             self.limCheck,
#                                             self.output,
#                                             self.models))



def click_search(query:QLineEdit,
                sri_model:QComboBox,
                dataset:QComboBox,
                umbral:QDoubleSpinBox,
                umbralCheck:QCheckBox,
                sensitive:QCheckBox,
                alpha:QDoubleSpinBox,
                alphaCheck:QCheckBox,
                lim:QSpinBox,
                limCheck:QCheckBox,
                output:QListWidget,
                models:dict):
    query = get_query(query)
    sri_model = get_sri(sri_model)
    dataset = get_dataset(dataset)
    umbral = get_umbral(umbral, umbralCheck)
    sensitive = get_sensitive(sensitive)
    alpha = get_alpha(alpha, alphaCheck)
    lim = get_lim(lim, limCheck)
    
    
    if sri_model == 'Modelo Vectorial':
        model = models['VectorModel']
    
    items= model.run(query=query, dataset=dataset, umbral=umbral, sensitive=sensitive, alpha=alpha, limit=lim)
    output.clear()
    for item in items:
        output.addItem('doc: ' +  str(item[0]) + '            ' + 'similarity: ' +str(item[1]))


def get_query(query:QLineEdit):
    return query.text()

def get_umbral(umbral:QDoubleSpinBox, umbralCheck:QCheckBox):
    if umbralCheck.isChecked():
        return umbral.value()
    return None

def get_sensitive(sensitive:QCheckBox):
    return sensitive.isChecked()

def get_alpha(alpha:QDoubleSpinBox, alphaCheck:QCheckBox):
    if alphaCheck.isChecked():
        return alpha.value()
    return 0.5

def get_lim(lim:QSpinBox, limCheck:QCheckBox):
    if limCheck.isChecked():
        return lim.value()
    return None

def get_sri(sri_model:QComboBox):
    return sri_model.currentText()

def get_dataset(dataset:QComboBox):
    return dataset.currentText()

def output():
    raise NotImplementedError