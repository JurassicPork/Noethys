#!/usr/bin/env python
# -*- coding: utf8 -*-
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
from Ctrl import CTRL_Bandeau
from Ol import OL_Modes_reglements
import GestionDB
import six
from PIL import Image


def Supprime_accent(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"),]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_modes_reglements", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici saisir, modifier ou supprimer des modes de règlements que vous pourrez utiliser lors de la saisie de règlements.")
        titre = _(u"Gestion des modes de règlements")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Mode_reglement.png")
        self.ctrl_listview = OL_Modes_reglements.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.MAJ()
        self.ctrl_recherche = OL_Modes_reglements.CTRL_Outils(self, listview=self.ctrl_listview)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_creer_mode_prelevement = CTRL_Bouton_image.CTRL(self, texte=_(u"Créer un mode Prélèvement"), cheminImage="Images/32x32/Prelevement.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
            
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Creer_mode_prelevement, self.bouton_creer_mode_prelevement)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un mode de règlement")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le mode de règlement sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le mode de règlement sélectionné dans la liste")))
        self.bouton_creer_mode_prelevement.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer automatiquement un mode 'Prélèvement'")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((750, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_droit = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_creer_mode_prelevement, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def Ajouter(self, event):
        self.ctrl_listview.Ajouter(None)
        
    def Modifier(self, event):
        self.ctrl_listview.Modifier(None)

    def Supprimer(self, event):
        self.ctrl_listview.Supprimer(None)
    
    def GetIDmode(self):
        selection = self.ctrl_listview.Selection()
        if len(selection) == 0 :
            return None
        else:
            return selection[0].IDmode
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Modesderglements")

    def Creer_mode_prelevement(self, event=None):
        """ Créer un mode 'Prélèvement automatique' """
        # Vérifie si un mode Prélèvement n'existe pas déjà
        DB = GestionDB.DB()
        req = """SELECT IDmode, label FROM modes_reglements;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        present = False
        for IDmode, label in listeDonnees:
            if "prelevement" in Supprime_accent(label.lower()):
                present = True

        if present == True:
            dlg = wx.MessageDialog(self, _(u"Il semblerait qu'un mode 'Prélèvement automatique' soit déjà présent.\n\nSouhaitez-vous quand même créer un nouveau mode ?"), _(u"Avertissement"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return

        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la création d'un mode de règlement 'Prélèvement automatique' ?"), _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES:
            return

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [("label", _(u"Prélèvement automatique")), ]
        IDmode = DB.ReqInsert("modes_reglements", listeDonnees)

        # Sauvegarde de l'image
        buffer = six.BytesIO()
        img = Image.open(Chemins.GetStaticPath("Images/Special/Prelevement.png"))
        img = img.convert("RGB")
        img.save(buffer, format='JPEG', quality=100)
        buffer.seek(0)
        DB.MAJimage("modes_reglements", "IDmode", IDmode, buffer.read())

        DB.Close()

        # MAJ
        self.ctrl_listview.MAJ()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
