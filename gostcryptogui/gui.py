#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2017 Борис Макаренко

Данная лицензия разрешает лицам, получившим копию данного программного
обеспечения и сопутствующей документации (в дальнейшем именуемыми «Программное
Обеспечение»), безвозмездно использовать Программное Обеспечение без
ограничений, включая неограниченное право на использование, копирование,
изменение, добавление, публикацию, распространение, сублицензирование и/или
продажу копий Программного Обеспечения, а также лицам, которым предоставляется
данное Программное Обеспечение, при соблюдении следующих условий:

Указанное выше уведомление об авторском праве и данные условия должны быть
включены во все копии или значимые части данного Программного Обеспечения.

ДАННОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО
ГАРАНТИЙ, ЯВНО ВЫРАЖЕННЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ ГАРАНТИИ ТОВАРНОЙ
ПРИГОДНОСТИ, СООТВЕТСТВИЯ ПО ЕГО КОНКРЕТНОМУ НАЗНАЧЕНИЮ И ОТСУТСТВИЯ НАРУШЕНИЙ,
НО НЕ ОГРАНИЧИВАЯСЬ ИМИ. НИ В КАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ НЕ НЕСУТ
ОТВЕТСТВЕННОСТИ ПО КАКИМ-ЛИБО ИСКАМ, ЗА УЩЕРБ ИЛИ ПО ИНЫМ ТРЕБОВАНИЯМ, В ТОМ
ЧИСЛЕ, ПРИ ДЕЙСТВИИ КОНТРАКТА, ДЕЛИКТЕ ИЛИ ИНОЙ СИТУАЦИИ, ВОЗНИКШИМ ИЗ-ЗА
ИСПОЛЬЗОВАНИЯ ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ ИЛИ ИНЫХ ДЕЙСТВИЙ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ..

Copyright (c) 2017 Boris Makarenko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import ConfigParser

from mainwindow import *
from cprocsp import *
from selectcert import *
from viewcert import *


class ViewCert(QtGui.QDialog):
    def __init__(self):
        super(ViewCert, self).__init__()
        self.ui = Ui_cert_view()
        self.ui.setupUi(self)


class ChooseCert(QtGui.QDialog):
    cert = str
    certs_hashes = dict

    def __init__(self, withsecret=bool):
        super(ChooseCert, self).__init__()
        self.ui = Ui_CertForm()
        self.ui.setupUi(self)
        self.certs_hashes = []
        model = QtGui.QStringListModel()
        cert_list = QtCore.QStringList()
        certs_data = CryptoPro().get_store_certs('uMy')
        if not withsecret:
            cert_list.append(u'Из файла...')
        for line in certs_data:
            if withsecret and line['secretKey'] == 'Yes':
                    cert_list.append(
                        u'%s, \nВыдан:%s, \nХэш SHA1: %s\nНе действителен до: %s\nНе действителен после: %s' % (
                            line['subjectCN'], line['issuerCN'], line['thumbprint'], line['notValidBefore'],
                            line['notValidAfter']))
                    self.certs_hashes.append(line)
            else:
                cert_list.append(
                    u'%s, \nВыдан:%s, \nХэш SHA1: %s\nНе действителен до: %s\nНе действителен после: %s' % (
                        line['subjectCN'], line['issuerCN'], line['thumbprint'], line['notValidBefore'],
                        line['notValidAfter']))
                self.certs_hashes.append(line)
        model.setStringList(cert_list)
        self.ui.listView.setModel(model)
        self.ui.cancelButton.clicked.connect(self.close)
        self.ui.okButton.setEnabled(False)
        self.ui.okButton.clicked.connect(self.accept)
        if withsecret:
            self.ui.listView.clicked.connect(self.select_cert_w_secret)
        else:
            self.ui.listView.clicked.connect(self.select_cert)
        self.show()

    def select_cert(self, index):
        if index.row() == 0:
            self.cert = 'file'
        else:
            self.cert = self.certs_hashes[index.row()-1]['thumbprint']
        self.ui.okButton.setEnabled(bool(self.cert))
        print self.cert

    def select_cert_w_secret(self, index):
        self.cert = self.certs_hashes[index.row()]['thumbprint']
        self.ui.okButton.setEnabled(bool(self.cert))

    def getCertificate(self):
        return self.cert


class Window(QtGui.QMainWindow):
    provider = str
    encoding = str
    signcheck = bool
    dettached = bool

    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        aboutAction = QtGui.QAction(u'&О программе', self)
        aboutAction.setShortcut('Ctrl+Q')
        self.ui.menubar.addAction(aboutAction)
        encodingActionGroup = QtGui.QActionGroup(self)
        self.ui.actionBase64.setActionGroup(encodingActionGroup)
        self.ui.actionDER.setActionGroup(encodingActionGroup)
        providerActionGroup = QtGui.QActionGroup(self)
        self.ui.action_CSP.setActionGroup(providerActionGroup)
        self.ui.actionOpenSSL.setActionGroup(providerActionGroup)
        signcheckActionGroup = QtGui.QActionGroup(self)
        self.ui.actionSignCheckOn.setActionGroup(signcheckActionGroup)
        self.ui.actionSignCheckOff.setActionGroup(signcheckActionGroup)
        dettachedActionGroup = QtGui.QActionGroup(self)
        self.ui.actionDettachedOn.setActionGroup(dettachedActionGroup)
        self.ui.actionDettachedOff.setActionGroup(dettachedActionGroup)
        self.connect(aboutAction, QtCore.SIGNAL('triggered()'), self.aboutProgram)
        self.connect(self.ui.actionDER, QtCore.SIGNAL('triggered()'), self.setOptions)
        self.connect(self.ui.actionBase64, QtCore.SIGNAL('triggered()'), self.setOptions)
        self.connect(self.ui.action_CSP, QtCore.SIGNAL('triggered()'), self.setOptions)
        self.connect(self.ui.actionOpenSSL, QtCore.SIGNAL('triggered()'), self.setOptions)
        self.connect(self.ui.actionSignCheckOn, QtCore.SIGNAL('triggered()'), self.setOptions)
        self.connect(self.ui.actionSignCheckOff, QtCore.SIGNAL('triggered()'), self.setOptions)
        self.connect(self.ui.actionDettachedOn, QtCore.SIGNAL('triggered()'), self.setOptions)
        self.connect(self.ui.actionDettachedOff, QtCore.SIGNAL('triggered()'), self.setOptions)
        self.connect(self.ui.btnSign, QtCore.SIGNAL('clicked()'), self.sign)
        self.connect(self.ui.btnVerify, QtCore.SIGNAL('clicked()'), self.verify)
        self.connect(self.ui.btnEncrypt, QtCore.SIGNAL('clicked()'), self.encrypt)
        self.connect(self.ui.btnDecrypt, QtCore.SIGNAL('clicked()'), self.decrypt)
        self.readConfig()

    def writeConfig(self):
        config = ConfigParser.RawConfigParser()
        config.add_section('gost-crypto-gui')
        config.set('gost-crypto-gui', 'provider', self.provider)
        config.set('gost-crypto-gui', 'encoding', self.encoding)
        config.set('gost-crypto-gui', 'signcheck', 'True' if self.signcheck else 'False')
        config.set('gost-crypto-gui', 'dettached', 'True' if self.dettached else 'False')
        if not os.path.exists(os.path.expanduser('~/.gost-crypto-gui/config.cfg')):
            os.makedirs(os.path.expanduser('~/.gost-crypto-gui/'))
            config.set('gost-crypto-gui', 'provider', 'cprocsp')
            config.set('gost-crypto-gui', 'encoding', 'der')
            config.set('gost-crypto-gui', 'signcheck', 'True')
            config.set('gost-crypto-gui', 'dettached', 'False')
        with open(os.path.expanduser('~/.gost-crypto-gui/config.cfg'), 'wb') as configfile:
            config.write(configfile)

    def readConfig(self):
        try:
            config = ConfigParser.ConfigParser()
            config.read(os.path.expanduser('~/.gost-crypto-gui/config.cfg'))
            self.provider = config.get('gost-crypto-gui', 'provider')
            self.encoding = config.get('gost-crypto-gui', 'encoding')
            self.signcheck = config.getboolean('gost-crypto-gui', 'signcheck')
            self.dettached = config.getboolean('gost-crypto-gui', 'dettached')
        except ConfigParser.NoSectionError:
            return
        self.ui.action_CSP.setChecked(self.provider == 'cprocsp')
        self.ui.actionOpenSSL.setChecked(self.provider == 'openssl')
        self.ui.actionBase64.setChecked(self.encoding == 'base64')
        self.ui.actionDER.setChecked(self.encoding == 'der')
        self.ui.actionSignCheckOn.setChecked(True if self.signcheck else False)
        self.ui.actionSignCheckOff.setChecked(False if self.signcheck else True)
        self.ui.actionDettachedOn.setChecked(True if self.dettached else False)
        self.ui.actionDettachedOff.setChecked(False if self.dettached else True)

    def setOptions(self):
        if self.ui.actionDER.isChecked():
            self.encoding = 'der'
        elif self.ui.actionBase64.isChecked():
            self.encoding = 'base64'
        if self.ui.action_CSP.isChecked():
            self.provider = 'cprocsp'
        if self.ui.actionSignCheckOn.isChecked():
            self.signcheck = True
        elif self.ui.actionSignCheckOff.isChecked():
            self.signcheck = False
        if self.ui.actionDettachedOn.isChecked():
            self.dettached = True
        elif self.ui.actionDettachedOff.isChecked():
            self.dettached = False
        self.writeConfig()

    def sign(self, *args):
        if self.sender():
            file_names = QtGui.QFileDialog().getOpenFileNames(self, u"Выберите файл(ы)", "", "")
            if not file_names:
                return
        else:
            file_names = args
        choose = ChooseCert(True)
        if choose.exec_():
            thumbprint = choose.getCertificate()
        else:
            return
        for filename in file_names:
            try:
                result = CryptoPro().sign(thumbprint, unicode(filename), self.encoding, self.dettached)
                if result[0]:
                    QtGui.QMessageBox().information(self, u"Cообщение",
                                                    u"Файл %s успешно подписан.<br>" % unicode(filename))
                if result[1]:
                    QtGui.QMessageBox().warning(self, u"Предупреждение", result[1])
            except Exception as error:
                QtGui.QMessageBox().warning(self, u"Cообщение", u"Произошла ошибка:\n%s" % error)

    def verify(self, dettach=False, *args):
        if self.sender():
            file_names = QtGui.QFileDialog().getOpenFileNames(self, u"Выберите файл(ы)", "", "*.sig")
            if not file_names:
                return
        else:
            file_names = args
        for filename in file_names:
            try:
                signer, chain, revoked, expired = CryptoPro().verify(unicode(filename), dettach)
                cert_view = ViewCert()
                item = QtGui.QListWidgetItem(cert_view.ui.cert_listview)
                label = QtGui.QLabel()
                label.setText(u'Файл: %s' % unicode(filename))
                cert_view.ui.cert_listview.setItemWidget(item, label)
                item = QtGui.QListWidgetItem(cert_view.ui.cert_listview)
                label = QtGui.QLabel()
                label.setText(u'<b>Информация о сертификате подписи:</b>:')
                cert_view.ui.cert_listview.setItemWidget(item, label)
                for line in signer['signer'].decode('utf-8').split(', '):
                    item = QtGui.QListWidgetItem(cert_view.ui.cert_listview)
                    label = QtGui.QLabel()
                    label.setText(line)
                    cert_view.ui.cert_listview.setItemWidget(item, label)
                item = QtGui.QListWidgetItem(cert_view.ui.cert_listview)
                label = QtGui.QLabel()
                if chain:
                    label.setText(u'<font color="green"><b>Цепочка сертификатов была проверена.</b></font>')
                else:
                    label.setText(u'<font color="orange"><b>ВНИМАНИЕ: Цепочка сертификатов не была проверена.</b></font>')
                cert_view.ui.cert_listview.setItemWidget(item, label)
                item = QtGui.QListWidgetItem(cert_view.ui.cert_listview)
                label = QtGui.QLabel()
                if revoked:
                    label.setText(u'<font color="red"><b>ВНИМАНИЕ: Один или несколько сертификатов в цепочке отозваны!</b></font>')
                elif expired:
                    label.setText(u'<font color="red"><b>ВНИМАНИЕ: Срок действия сертификата истек или еще не наступил!</b></font>')
                elif chain:
                    label.setText(u'<font color="green"><b>Сертификат действителен.</b></font>')
                cert_view.ui.cert_listview.setItemWidget(item, label)
                cert_view.exec_()
            except Exception as error:
                QtGui.QMessageBox().warning(self, u"Cообщение", u"Произошла ошибка:\n%s" % error)

    def encrypt(self, *args):
        if self.sender():
            file_names = QtGui.QFileDialog().getOpenFileNames(self, u"Выберите файл(ы)", "", "")
            if not file_names:
                return
        else:
            file_names = args
        choose = ChooseCert(False)
        if choose.exec_():
            thumbprint = choose.getCertificate()
            if thumbprint == 'file':
                thumbprint = QtGui.QFileDialog().getOpenFileName(self, u"Выберите файл(ы)", "", "*.crt *cer")
                if not thumbprint:
                    return
        else:
            return
        for filename in file_names:
            try:
                encrypted, chain, revoked, expired = CryptoPro().encrypt(unicode(thumbprint), unicode(filename), self.encoding)
                if encrypted:
                    message = u'Файл %s успешно зашифрован.\n' % unicode(filename)
                    if not chain:
                        message += u'ВНИМАНИЕ: Статус отзыва сертификата не был проверен!\n'
                    if revoked:
                        message += u'ВНИМАНИЕ: Один или несколько сертификатов в цепочке отозваны!\n'
                    if expired:
                        message += u'ВНИМАНИЕ: Срок действия сертификата истек или еще не наступил!\n'
                    QtGui.QMessageBox().information(self, u"Cообщение", message)
            except Exception as error:
                QtGui.QMessageBox().warning(self, u"Cообщение", u"Произошла ошибка:\n%s" % error)

    def decrypt(self, *args):
        if self.sender():
            file_names = QtGui.QFileDialog().getOpenFileNames(self, u"Выберите файл(ы)", "", "*.enc *.encr")
            if not file_names:
                return
        else:
            file_names = args
        choose = ChooseCert(True)
        if choose.exec_():
            thumbprint = choose.getCertificate()
        else:
            return
        for filename in file_names:
            try:
                decrypted, chain, revoked, expired = CryptoPro().decrypt(thumbprint, unicode(filename))
                if decrypted:
                    message = u'Файл %s успешно расшифрован.\n' % unicode(filename)
                    if not chain:
                        message += u'ВНИМАНИЕ: Статус отзыва сертификата не был проверен!\n'
                    if revoked:
                        message += u'ВНИМАНИЕ: Один или несколько сертификатов в цепочке отозваны!\n'
                    if expired:
                        message += u'ВНИМАНИЕ: Срок действия сертификата истек или еще не наступил!\n'
                    QtGui.QMessageBox().information(self, u"Cообщение", message)
            except Exception as error:
                QtGui.QMessageBox().warning(self, u"Cообщение", u"Произошла ошибка:\n%s" % error)

    def aboutProgram(self):
        QtGui.QMessageBox().about(self, u"О программе",
                                  u"<b>gost-crypto-gui 0.3a</b><br>"
                                  u"<br>2017г. Борис Макаренко<br>УИТ ФССП России"
                                  u"<br>E-mail: <a href='mailto:makarenko@fssprus.ru'>makarenko@fssprus.ru</a>"
                                  u"<br> <a href='mailto:bmakarenko90@gmail.com'>bmakarenko90@gmail.com</a><br><br>"
                                  u"<a href='http://opensource.org/licenses/MIT'>Лицензия MIT</a>")
