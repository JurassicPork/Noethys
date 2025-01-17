#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB

from Ctrl import CTRL_Grille_periode
from Utils import UTILS_Parametres
import datetime



class CTRL_activites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.SetToolTip(wx.ToolTip(_(u"Cochez les activités à afficher")))
        self.listeActivites = []

    def MAJ(self):
        coches = self.GetIDcoches()
        self.Clear()
        self.listeActivites = self.Importation()
        self.SetListeChoix()
        self.SetIDcoches(coches)
    
    def Importation(self):
        # Récupération des activités
        if self.parent.ctrl_masquer_activites.GetValue() == True :
            conditions = "WHERE date_fin>'%s' " % (datetime.date.today() - datetime.timedelta(days=365*2))
        else :
            conditions = ""
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege, date_debut, date_fin
        FROM activites
        %s
        ORDER BY date_fin DESC, nom;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close()   
        listeActivites = []
        for IDactivite, nom, abrege, date_debut, date_fin in listeDonnees :
            listeActivites.append((nom, IDactivite))
        return listeActivites

    def SetListeChoix(self):
        # Format : (nomItem, date_debut, date_fin)
        listeItems = []
        index = 0
        for nom, IDactivite in self.listeActivites :
            if nom == None : nom = "?"
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeActivites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeActivites[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeActivites)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeActivites)):
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
            
    def SetDictDonnees(self, dictDonnees={}):
        if dictDonnees == None : return
        listeActivites = dictDonnees["listeActivites"]
        self.SetIDcoches(listeActivites)

            

class Dialog(wx.Dialog):
    def __init__(self, parent, dictDonnees = {}, afficheLargeurColonneUnite=True, afficheAbregeGroupes=True, totaux=True, abregeGroupes=False, affichePresents=1, afficheTotaux=True, maj_auto_remplissage=0):
        wx.Dialog.__init__(self, parent, -1, name="parametres_remplissage", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.afficheLargeurColonneUnite = afficheLargeurColonneUnite
        
        # Périodes
        self.staticbox_periodes_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.ctrl_periodes = CTRL_Grille_periode.CTRL(self)
        self.ctrl_periodes.SetMinSize((220, 230))
        
        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_activites(self)
        self.ctrl_activites.SetMinSize((300, 150))
        
        self.ctrl_masquer_activites = wx.CheckBox(self, -1, _(u"Masquer les anciennes activités"))
        self.ctrl_masquer_activites.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="parametres_remplissage", nom="masquer_anciennes_activites", valeur=0))
        self.ctrl_masquer_activites.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        
        # Options d'affichage
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        
        self.label_abregeGroupes = wx.StaticText(self, -1, _(u"Utiliser le nom abrégé des groupes :"))
        self.ctrl_abregeGroupes_oui = wx.RadioButton(self, -1, _(u"Oui"), style = wx.RB_GROUP)
        self.ctrl_abregeGroupes_non = wx.RadioButton(self, -1, _(u"Non"))
        if abregeGroupes == True :
            self.ctrl_abregeGroupes_oui.SetValue(True)
        else:
            self.ctrl_abregeGroupes_non.SetValue(True)

        self.label_affichePresents = wx.StaticText(self, -1, _(u"Afficher les présents en temps réel :"))
        self.ctrl_affichePresents_oui = wx.RadioButton(self, -1, _(u"Oui"), style = wx.RB_GROUP)
        self.ctrl_affichePresents_non = wx.RadioButton(self, -1, _(u"Non"))
        if affichePresents == True :
            self.ctrl_affichePresents_oui.SetValue(True)
        else:
            self.ctrl_affichePresents_non.SetValue(True)

        self.label_afficheTotaux = wx.StaticText(self, -1, _(u"Afficher les colonnes des totaux :"))
        self.ctrl_afficheTotaux_oui = wx.RadioButton(self, -1, _(u"Oui"), style = wx.RB_GROUP)
        self.ctrl_afficheTotaux_non = wx.RadioButton(self, -1, _(u"Non"))
        if totaux == True :
            self.ctrl_afficheTotaux_oui.SetValue(True)
        else:
            self.ctrl_afficheTotaux_non.SetValue(True)

        self.label_maj_auto = wx.StaticText(self, -1, _(u"Mise à jour auto de l'affichage :"))
        self.liste_choix_maj_auto = [
            (0, _(u"Jamais")),
            # (1000 * 60, _("Toutes les minutes")),
            (1000 * 60 * 2, _(u"Toutes les 2 minutes")),
            (1000 * 60 * 5, _(u"Toutes les 5 minutes")),
            (1000 * 60 * 10, _(u"Toutes les 10 minutes")),
            (1000 * 60 * 30, _(u"Toutes les 30 minutes")),
            (1000 * 60 * 60, _(u"Toutes les heures")),
        ]
        self.ctrl_maj_auto = wx.Choice(self, -1, choices=[label for valeur, label in self.liste_choix_maj_auto])
        try:
            self.ctrl_maj_auto.Select([index for index, (valeur, label) in enumerate(self.liste_choix_maj_auto) if valeur == maj_auto_remplissage][0])
        except:
            pass

        if afficheAbregeGroupes == False :
            self.label_abregeGroupes.Show(False)
            self.ctrl_abregeGroupes_oui.Show(False)
            self.ctrl_abregeGroupes_non.Show(False)

        if afficheTotaux == False :
            self.label_afficheTotaux.Show(False)
            self.ctrl_afficheTotaux_oui.Show(False)
            self.ctrl_afficheTotaux_non.Show(False)

        if self.afficheLargeurColonneUnite == False and afficheAbregeGroupes == False and afficheTotaux == False :
            self.label_affichePresents.Show(False)
            self.ctrl_affichePresents_oui.Show(False)
            self.ctrl_affichePresents_non.Show(False)
            self.staticbox_options_staticbox.Show(False)

            self.label_maj_auto.Show(False)
            self.ctrl_maj_auto.Show(False)


        # Boutons de commandes 
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckMasquerActivites, self.ctrl_masquer_activites)
        
        # Init contrôles
        self.ctrl_activites.MAJ() 
        
        # Applique les valeurs par défaut
        self.ctrl_periodes.SetDictDonnees(dictDonnees)
        self.ctrl_activites.SetDictDonnees(dictDonnees)

    def __set_properties(self):
        self.SetTitle(_(u"Paramètres d'affichage"))
        self.ctrl_masquer_activites.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour masquer de cette liste les activités vieilles de plus de 2 ans")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((640, 450))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
    
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Période
        staticbox_periodes = wx.StaticBoxSizer(self.staticbox_periodes_staticbox, wx.VERTICAL)
        staticbox_periodes.Add(self.ctrl_periodes, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_contenu.Add(staticbox_periodes, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        grid_sizer_activites = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_activites.Add(self.ctrl_activites, 1, wx.EXPAND, 0)
        grid_sizer_activites.Add(self.ctrl_masquer_activites, 0, wx.EXPAND, 0)
        grid_sizer_activites.AddGrowableRow(0)
        grid_sizer_activites.AddGrowableCol(0)
        staticbox_activites.Add(grid_sizer_activites, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_droit.Add(staticbox_activites, 1, wx.EXPAND, 0)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)

        grid_sizer_abregeGroupes = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_abregeGroupes.Add(self.label_abregeGroupes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_abregeGroupes.Add(self.ctrl_abregeGroupes_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_abregeGroupes.Add(self.ctrl_abregeGroupes_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_options.Add(grid_sizer_abregeGroupes, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)

        grid_sizer_affichePresents = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_affichePresents.Add(self.label_affichePresents, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichePresents.Add(self.ctrl_affichePresents_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichePresents.Add(self.ctrl_affichePresents_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_options.Add(grid_sizer_affichePresents, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)

        grid_sizer_afficheTotaux = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_afficheTotaux.Add(self.label_afficheTotaux, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_afficheTotaux.Add(self.ctrl_afficheTotaux_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_afficheTotaux.Add(self.ctrl_afficheTotaux_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_options.Add(grid_sizer_afficheTotaux, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)

        grid_sizer_maj_auto = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_maj_auto.Add(self.label_maj_auto, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_maj_auto.Add(self.ctrl_maj_auto, 0, wx.ALIGN_CENTER_VERTICAL |wx.EXPAND, 0)
        staticbox_options.Add(grid_sizer_maj_auto, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)

        grid_sizer_droit.Add(staticbox_options, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Commandes
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnCheckMasquerActivites(self, event):
        self.ctrl_activites.MAJ() 
        
    def GetListeActivites(self):
        return self.ctrl_activites.GetIDcoches()
    
    def GetListePeriodes(self):
        return self.ctrl_periodes.GetDatesSelections() 
    
    def GetDictDonnees(self):
        dictDonnees = self.ctrl_periodes.GetDictDonnees()
        dictDonnees["listeActivites"] = self.ctrl_activites.GetIDcoches()
        return dictDonnees

    def GetAbregeGroupes(self):
        return int(self.ctrl_abregeGroupes_oui.GetValue())

    def GetAffichePresents(self):
        return int(self.ctrl_affichePresents_oui.GetValue())

    def GetAfficheTotaux(self):
        return int(self.ctrl_afficheTotaux_oui.GetValue())

    def GetMAJautoRemplissage(self):
        index = self.ctrl_maj_auto.GetSelection()
        return self.liste_choix_maj_auto[index][0]

    def OnBoutonOk(self, event):
        # Mémorisation paramètres
        UTILS_Parametres.Parametres(mode="set", categorie="parametres_remplissage", nom="masquer_anciennes_activites", valeur=int(self.ctrl_masquer_activites.GetValue()))
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dictDonnees = {
        "page" : 0,
        "listeSelections" : [2, 3, 5],
        "annee" : 2009,
        "dateDebut" : None,
        "dateFin" : None,
        "listePeriodes" : [],
        "listeActivites" : [1, 17],
        }
    frame_1 = Dialog(None, dictDonnees)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
