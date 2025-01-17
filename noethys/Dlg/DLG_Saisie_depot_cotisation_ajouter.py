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
import datetime

from Ol import OL_Cotisations_depots

import GestionDB


class Dialog(wx.Dialog):
    def __init__(self, parent, tracks=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_depot_cotisation_ajouter", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.tracks= tracks
        
        self.label_intro = wx.StaticText(self, -1, _(u"Double-cliquez sur une cotisation pour l'affecter ou non au dépôt."), style=wx.ALIGN_CENTER)
        
        self.label_tri = wx.StaticText(self, -1, _(u"Tri par :"))
        self.ctrl_tri = wx.Choice(self, -1, choices = (_(u"Ordre de saisie"), _(u"Date de début de validité"), _(u"Date de fin de validité"), _(u"Nom des titulaires"), _(u"Type de cotisation"), _(u"Nom de cotisation"), _(u"Numéro de carte"), _(u"Date de dépôt")))
        self.ctrl_tri.Select(0) 
        
        self.label_ordre = wx.StaticText(self, -1, _(u"Ordre :"))
        self.ctrl_ordre = wx.Choice(self, -1, choices = (_(u"Ascendant"), _(u"Descendant")))
        self.ctrl_ordre.Select(1) 

        # Cotisations disponibles
        self.staticbox_cotisations_disponibles_staticbox = wx.StaticBox(self, -1, _(u"Cotisations disponibles"))
        self.ctrl_cotisations_disponibles = OL_Cotisations_depots.ListView(self, id=-1, inclus=False, name="OL_cotisations_depot", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        # Commandes
        self.bouton_bas_tout = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_double_bas.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_bas = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_haut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut_rouge.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_haut_tout = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_double_haut_rouge.png"), wx.BITMAP_TYPE_ANY))

        # Reglements du dépôt
        self.staticbox_cotisations_depot_staticbox = wx.StaticBox(self, -1, _(u"Cotisations du dépôt"))
        self.ctrl_cotisations_depot = OL_Cotisations_depots.ListView(self, id=-1, inclus=True, name="OL_cotisations_depot", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonBasTout, self.bouton_bas_tout)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBas, self.bouton_bas)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHaut, self.bouton_haut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHautTout, self.bouton_haut_tout)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChoixTri, self.ctrl_tri)
        self.Bind(wx.EVT_CHOICE, self.OnChoixOrdre, self.ctrl_ordre)

        # Initialisation des contrôles
        self.MAJListes(tracks=self.tracks) 
        

    def __set_properties(self):
        self.SetTitle(_(u"Ajouter ou retirer des cotisations"))
        self.ctrl_tri.SetToolTip(wx.ToolTip(_(u"Sélectionnez le critère de tri")))
        self.ctrl_ordre.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'ordre de tri")))
        self.bouton_bas_tout.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter toutes les cotisations dans le dépôt")))
        self.bouton_bas.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter la cotisation disponible selectionné dans le dépôt")))
        self.bouton_bas_tout.SetMinSize((80, -1))
        self.bouton_bas.SetMinSize((150, -1))
        self.bouton_haut.SetMinSize((150, -1))
        self.bouton_haut_tout.SetMinSize((80, -1))
        self.bouton_haut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour retirer la cotisation sélectionnée du dépôt")))
        self.bouton_haut_tout.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour retirer toutes les cotisations du dépôt")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((950, 680))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Intro
        grid_sizer_intro = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_intro.Add(self.label_intro, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        grid_sizer_intro.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_intro.Add(self.label_tri, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.Add(self.ctrl_tri, 0, 0, 0)
        grid_sizer_intro.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_intro.Add(self.label_ordre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.Add(self.ctrl_ordre, 0, 0, 0)
        grid_sizer_intro.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Cotisations disponibles
        staticbox_reglements_disponibles = wx.StaticBoxSizer(self.staticbox_cotisations_disponibles_staticbox, wx.VERTICAL)
        staticbox_reglements_disponibles.Add(self.ctrl_cotisations_disponibles, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_reglements_disponibles, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Commandes de transfert
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_bas_tout, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_bas, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_haut, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_haut_tout, 0, 0, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_commandes.AddGrowableCol(5)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Cotisations déposées
        staticbox_reglements_depot = wx.StaticBoxSizer(self.staticbox_cotisations_depot_staticbox, wx.VERTICAL)
        staticbox_reglements_depot.Add(self.ctrl_cotisations_depot, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_reglements_depot, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def MAJListes(self, tracks=None, selectionTrack=None, nextTrack=None):
        self.tracks = tracks
        self.ctrl_cotisations_disponibles.MAJ(tracks, selectionTrack=selectionTrack, nextTrack=nextTrack) 
        self.ctrl_cotisations_depot.MAJ(tracks, selectionTrack=selectionTrack, nextTrack=nextTrack) 

    def DeplacerTout(self, inclus=True):
        listeTracks = []
        if self.tracks:
            for track in self.tracks :
                track.inclus = inclus
                listeTracks.append(track)
            self.MAJListes(listeTracks)

    def GetTracks(self):
        return self.tracks

    def OnChoixTri(self, event):
        selection = self.ctrl_tri.GetSelection() 
        self.ctrl_cotisations_disponibles.numColonneTri = selection
        self.ctrl_cotisations_depot.numColonneTri = selection
        self.MAJListes()

    def OnChoixOrdre(self, event):
        selection = self.ctrl_ordre.GetSelection() 
        self.ctrl_cotisations_disponibles.ordreAscendant = selection
        self.ctrl_cotisations_depot.ordreAscendant = selection
        self.MAJListes()

    def OnBoutonBas(self, event): 
        self.ctrl_cotisations_disponibles.Deplacer()

    def OnBoutonHaut(self, event):
        self.ctrl_cotisations_depot.Deplacer()

    def OnBoutonBasTout(self, event): 
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment ajouter toutes les cotisations ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse ==  wx.ID_YES :
            self.DeplacerTout(inclus=True)

    def OnBoutonHautTout(self, event):
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment retirer toutes les cotisations ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse ==  wx.ID_YES :
            self.DeplacerTout(inclus=False)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Gestiondesdptsdecotisations")

    def OnBoutonOk(self, event): 
        self.EndModal(wx.ID_OK)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
