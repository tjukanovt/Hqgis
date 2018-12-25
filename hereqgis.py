# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HEREqgis
                                 A QGIS plugin
 Access the HERE API in QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-12-22
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Riccardo Klinger
        email                : riccardo.klinger@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog
from PyQt5 import QtGui, QtWidgets

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .hereqgis_dialog import HEREqgisDialog
import os.path
import requests, json
from PyQt5.QtCore import QVariant
from qgis.core import QgsPointXY, QgsGeometry, QgsVectorLayer, QgsProject, QgsFeature, QgsField, QgsMessageLog
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *
from qgis.utils import iface


class HEREqgis:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'HEREqgis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = HEREqgisDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&HEREqgis')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'HEREqgis')
        self.toolbar.setObjectName(u'HEREqgis')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('HEREqgis', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/hereqgis/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Access the HERE API'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&HEREqgis'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    def convertGeocodeResponse(self, responseAddress):
        geocodeResponse = {}
        try:
            geocodeResponse["Label"] = responseAddress["Location"]["Address"]["Label"]
        except:
            geocodeResponse["Label"] = ""
        try:
            geocodeResponse["Country"] = responseAddress["Location"]["Address"]["Country"]
        except:
            geocodeResponse["Country"] = ""
        try:
            geocodeResponse["State"] = responseAddress["Location"]["Address"]["State"]
        except:
            geocodeResponse["State"]  = ""
        try:
            geocodeResponse["County"] = responseAddress["Location"]["Address"]["County"]
        except:
            geocodeResponse["County"] = ""
        try:
            geocodeResponse["City"] = responseAddress["Location"]["Address"]["City"]
        except:
            geocodeResponse["City"] = ""
        try:
            geocodeResponse["District"] = responseAddress["Location"]["Address"]["District"]
        except:
            geocodeResponse["District"] = ""
        try:
            geocodeResponse["Street"] = responseAddress["Location"]["Address"]["Street"]
        except:
            geocodeResponse["Street"] = ""
        try:
            geocodeResponse["HouseNumber"] = responseAddress["Location"]["Address"]["HouseNumber"]
        except:
            geocodeResponse["HouseNumber"] = ""
        try:
            geocodeResponse["PostalCode"] = responseAddress["Location"]["Address"]["PostalCode"]
        except:
            geocodeResponse["PostalCode"] = ""
        try:
            geocodeResponse["Relevance"] = responseAddress["Relevance"]
        except:
            geocodeResponse["Relevance"] = None
        try:
            geocodeResponse["CountryQuality"] = responseAddress["MatchQuality"]["Country"]
        except:
            geocodeResponse["CountryQuality"] = None
        try:
            geocodeResponse["CityQuality"] = responseAddress["MatchQuality"]["City"]
        except:
            geocodeResponse["CityQuality"] = None
        try:
            geocodeResponse["StreetQuality"] = responseAddress["MatchQuality"]["Street"][0]
        except:
            geocodeResponse["StreetQuality"] = None
        try:
            geocodeResponse["NumberQuality"] = responseAddress["MatchQuality"]["HouseNumber"]
        except:
            geocodeResponse["NumberQuality"] = None
        try:
            geocodeResponse["MatchType"] = responseAddress["MatchType"]
        except:
            geocodeResponse["MatchType"] = ""
        return(geocodeResponse)
    def createGeocodedLayer(self):
        layer = QgsVectorLayer(
            """Point?
            crs=epsg:4326
            &index=yes""",
            "AddressLayer",
            "memory"
        )
        layer.dataProvider().addAttributes([
            QgsField("id",QVariant.Int),
            QgsField("oldAddress",QVariant.String),
            QgsField("address",QVariant.String),
            QgsField("country",QVariant.String),
            QgsField("state",QVariant.String),
            QgsField("county",QVariant.String),
            QgsField("city",QVariant.String),
            QgsField("district",QVariant.String),
            QgsField("street",QVariant.String),
            QgsField("number",QVariant.String),
            QgsField("zip",QVariant.String),
            QgsField("relevance",QVariant.Double),
            QgsField("qu_country",QVariant.Double),
            QgsField("qu_city",QVariant.Double),
            QgsField("qu_street",QVariant.Double),
            QgsField("qu_number",QVariant.Double),
            QgsField("matchtype",QVariant.String)
        ])
        layer.updateFields()
        return(layer)
    def messageShow(self, progress, count, max):
        if not progress:
            progressMessageBar = iface.messageBar().createMessage("Looping through " + str(max) +" records ...")
            progress = QProgressBar()
            progress.setMaximum(max)
            progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            progressMessageBar.layout().addWidget(progress)
            iface.messageBar().pushWidget(progressMessageBar, level=1)
            iface.mainWindow().repaint()
        #    return progress
        if progress:
            progress.setValue(count)
        return(progress)
    def geocode(self):
        #getting values fronm the dialog:
        #if self.dlg.geocodeMode.currentText()=="single address":
        address = self.dlg.AddressInput.text()
        if address == "":
            address = "11 Wall Street, New York, USA"
        appId = self.dlg.AppId.text()
        appCode = self.dlg.AppCode.text()
        url = "https://geocoder.api.here.com/6.2/geocode.json?app_id=" + appId + "&app_code=" + appCode + "&searchtext=" + address
        print(appCode,appId, address)
        postData = {"app_id":appId, "app_code":appCode, "searchtext":address}
        r = requests.get(url)
        #print(r.json())
        ##
        #print(json.loads(r.text))
        try:
            #ass the response may hold more than one result we only use the best one:
            responseAddress = json.loads(r.text)["Response"]["View"][0]["Result"][0]
            geocodeResponse = self.convertGeocodeResponse(responseAddress)
            lat = responseAddress["Location"]["DisplayPosition"]["Latitude"]
            lng = responseAddress["Location"]["DisplayPosition"]["Longitude"]
            layer = self.createGeocodedLayer()
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lng,lat)))
            fet.setAttributes([
                0,
                address,
                geocodeResponse["Label"],
                geocodeResponse["Country"],
                geocodeResponse["State"],
                geocodeResponse["County"],
                geocodeResponse["City"],
                geocodeResponse["District"],
                geocodeResponse["Street"],
                geocodeResponse["HouseNumber"],
                geocodeResponse["PostalCode"],
                geocodeResponse["Relevance"],
                geocodeResponse["CountryQuality"],
                geocodeResponse["CityQuality"],
                geocodeResponse["StreetQuality"],
                geocodeResponse["NumberQuality"],
                geocodeResponse["MatchType"]
            ])
            #print("feature set")
            pr = layer.dataProvider()
            pr.addFeatures([fet])
            QgsProject.instance().addMapLayer(layer)
        except Exception as e:
            print(e)

    def batchGeocodeField(self):

        appId = self.dlg.AppId.text()
        appCode = self.dlg.AppCode.text()
        #concat addresses for batch requesting
        layer_list = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
        Resultlayer = self.createGeocodedLayer()
        pr = Resultlayer.dataProvider()

        #print(self.dlg.LayerSelect.currentData())
        for layer in layer_list:
            if layer.id() ==self.dlg.LayerSelect.currentData():
                idx = layer.fields().indexFromName(self.dlg.AddressField.currentText())
                features = layer.getFeatures()
                break

        ResultFeatureList = []
        addressList = []
        for fet in features:
            addressList.append(fet.attributes()[idx])
        progressItem = self.messageShow(None,0,len(addressList))
        i = 1
        for address in addressList:
            progressItem = self.messageShow(progressItem,i,len(addressList))
            url = "https://geocoder.api.here.com/6.2/geocode.json?app_id=" + appId + "&app_code=" + appCode + "&searchtext=" + address
            r = requests.get(url)
            try:
                #ass the response may hold more than one result we only use the best one:
                responseAddress = json.loads(r.text)["Response"]["View"][0]["Result"][0]
                geocodeResponse = self.convertGeocodeResponse(responseAddress)
                lat = responseAddress["Location"]["DisplayPosition"]["Latitude"]
                lng = responseAddress["Location"]["DisplayPosition"]["Longitude"]
                ResultFet = QgsFeature()
                ResultFet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lng,lat)))
                ResultFet.setAttributes([
                    fet.id(),
                    address,
                    geocodeResponse["Label"],
                    geocodeResponse["Country"],
                    geocodeResponse["State"],
                    geocodeResponse["County"],
                    geocodeResponse["City"],
                    geocodeResponse["District"],
                    geocodeResponse["Street"],
                    geocodeResponse["HouseNumber"],
                    geocodeResponse["PostalCode"],
                    geocodeResponse["Relevance"],
                    geocodeResponse["CountryQuality"],
                    geocodeResponse["CityQuality"],
                    geocodeResponse["StreetQuality"],
                    geocodeResponse["NumberQuality"],
                    geocodeResponse["MatchType"]
                ])
                ResultFeatureList.append(ResultFet)
                i+=1
            except Exception as e:
                print(e)
        pr.addFeatures(ResultFeatureList)
        iface.messageBar().clearWidgets()
        QgsProject.instance().addMapLayer(Resultlayer)


    def batchGeocodeFields(self):

        #if self.dlg.geocodeMode.currentText()=="single address":
        address = self.dlg.AddressInput.text()
        if address == "":
            address = "11 Wall Street, New York, USA"
        appId = self.dlg.AppId.text()
        appCode = self.dlg.AppCode.text()
        url = "https://geocoder.api.here.com/6.2/geocode.json?app_id=" + appId + "&app_code=" + appCode + "&searchtext=" + address
        print(appCode,appId, address)
        postData = {"app_id":appId, "app_code":appCode, "searchtext":address}
        r = requests.get(url)
        #print(r.json())
        ##
        #print(json.loads(r.text))
        try:
            #ass the response may hold more than one result we only use the best one:
            responseAddress = json.loads(r.text)["Response"]["View"][0]["Result"][0]
            lat = responseAddress["Location"]["DisplayPosition"]["Latitude"]
            lng = responseAddress["Location"]["DisplayPosition"]["Longitude"]
            layer = QgsVectorLayer(
                """Point?crs=epsg:4326&
                field=id:integer
                &field=address:string(200)
                &field=country:string(200)
                &field=state:string(200)
                &field=county:string(200)
                &field=city:string(200)
                &field=district:string(200)
                &field=street:string(200)
                &field=number:string(200)
                &field=zip:string(200)
                &field=relevance:float
                &field=qu_country:float
                &field=qu_city:float
                &field=qu_street:float
                &field=qu_number:float
                &field=matchtype:string(200)
                &index=yes""",
                "AddressLayer",
                "memory"
            )
            layer.commitChanges()
            fet = QgsFeature()
            print(lat,lng)
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lng,lat)))
            print("cords set")
            fet.setAttributes([
                0,   responseAddress["Location"]["Address"]["Label"],
                responseAddress["Location"]["Address"]["Country"],
                responseAddress["Location"]["Address"]["State"],
                responseAddress["Location"]["Address"]["County"],
                responseAddress["Location"]["Address"]["City"],
                responseAddress["Location"]["Address"]["District"],
                responseAddress["Location"]["Address"]["Street"],
                responseAddress["Location"]["Address"]["HouseNumber"],
                responseAddress["Location"]["Address"]["PostalCode"],
                responseAddress["Relevance"],
                responseAddress["MatchQuality"]["Country"],
                responseAddress["MatchQuality"]["City"],
                responseAddress["MatchQuality"]["Street"][0],
                responseAddress["MatchQuality"]["HouseNumber"],
                responseAddress["MatchType"]
            ])
            #print("feature set")
            pr = layer.dataProvider()
            pr.addFeatures([fet])
            QgsProject.instance().addMapLayer(layer)
        except Exception as e:
            print(e)
    def getCredFunction(self):
        import webbrowser
        webbrowser.open('https://developer.here.com/')
    def saveCredFunction(self):
        print("save credits")
        self.dlg.credentialInteraction.setText("")
        fileLocation = os.path.dirname(os.path.realpath(__file__))+ os.sep + "creds"
        with open(fileLocation + os.sep + 'credentials.json', 'w') as outfile:
            stringJSON = {"ID": self.dlg.AppId.text(), "CODE":  self.dlg.AppCode.text()}
            json.dump(stringJSON, outfile)
        self.dlg.credentialInteraction.setText("credentials saved to " + fileLocation + os.sep + 'credentials.json')
    def loadCredFunction(self):
        import json, os
        #fileLocation = QFileDialog.getOpenFileName(self.dlg, "JSON with credentials",os.path.dirname(os.path.realpath(__file__))+ os.sep + "creds", "JSON(*.JSON)")
        #print(fileLocation)
        scriptDirectory = os.path.dirname(os.path.realpath(__file__))
        self.dlg.credentialInteraction.setText("")
        print(scriptDirectory)
        try:
            import os
            scriptDirectory = os.path.dirname(os.path.realpath(__file__))
            with open(scriptDirectory + os.sep + 'creds' + os.sep + 'credentials.json') as f:
                data = json.load(f)
                self.dlg.AppId.setText(data["ID"])
                self.dlg.AppCode.setText(data["CODE"])
            self.dlg.credentialInteraction.setText("credits used from " + scriptDirectory + os.sep + 'creds' + os.sep + 'credentials.json')
        except:
            self.dlg.credentialInteraction.setText("no credits found in. Check for file" + scriptDirectory + os.sep + 'creds' + os.sep + 'credentials.json')
            #self.dlg.geocodeButton.setEnabled(False)

    def searchFieldPopulate(self):
        self.dlg.AddressField.clear()
        layer_list = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
        #print(self.dlg.LayerSelect.currentData())
        for layer in layer_list:
            if layer.id() ==self.dlg.LayerSelect.currentData():
                pr = layer.dataProvider()
                for field in pr.fields():
                    self.dlg.AddressField.addItem(field.name())


    def searchFieldsPopulate(self):
        layer_list = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
        #print(self.dlg.LayerSelect.currentData())
        self.dlg.CountryBox.clear()
        self.dlg.StateBox.clear()
        self.dlg.CountyBox.clear()
        self.dlg.ZipBox.clear()
        self.dlg.CityBox.clear()
        self.dlg.StreetBox.clear()
        self.dlg.NumberBox.clear()
        for layer in layer_list:
            if layer.id() ==self.dlg.LayerSelect_2.currentData():
                pr = layer.dataProvider()
                for field in pr.fields():
                    self.dlg.CountryBox.addItem(field.name())
                    self.dlg.StateBox.addItem(field.name())
                    self.dlg.CountyBox.addItem(field.name())
                    self.dlg.ZipBox.addItem(field.name())
                    self.dlg.CityBox.addItem(field.name())
                    self.dlg.StreetBox.addItem(field.name())
                    self.dlg.NumberBox.addItem(field.name())

    def run(self):
        from qgis.core import QgsProject
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        #try to load credentials:
        self.loadCredFunction()
        #self.geocodeInput()

        #self.dlg.geocodeMode.currentIndexChanged.connect(self.geocodeInput)
        self.dlg.LayerSelect.currentIndexChanged.connect(self.searchFieldPopulate)
        self.dlg.LayerSelect_2.currentIndexChanged.connect(self.searchFieldsPopulate)
        self.dlg.getCreds.clicked.connect(self.getCredFunction)
        self.dlg.saveCreds.clicked.connect(self.saveCredFunction)
        self.dlg.loadCreds.clicked.connect(self.loadCredFunction)
        #fill all layer/attributes
        self.dlg.LayerSelect.clear()
        self.dlg.LayerSelect_2.clear()
        layer_list = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
        for layer in layer_list:
            if layer.type() == 0:
                self.dlg.LayerSelect.addItem(layer.name(), layer.id())
                self.dlg.LayerSelect_2.addItem(layer.name(), layer.id())

        self.dlg.geocodeAddressButton.clicked.connect(self.geocode)
        self.dlg.batchGeocodeFieldButton.clicked.connect(self.batchGeocodeField)
        self.dlg.batchGeocodeFieldsButton.clicked.connect(self.batchGeocodeFields)

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            #get app code/id

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
