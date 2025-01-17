#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime




class CTRL_Unite_remplissage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.SetSize((55, -1))
        self.SetMinSize((55, -1))
                
        # Contrôle
        self.ctrl = wx.StaticText(self, -1, u"XXX")
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu.Add( (1, 1), 0, wx.EXPAND|wx.ALL, 0)
        grid_sizer_contenu.Add(self.ctrl, 0, wx.TOP, 1)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
        self.grid_sizer_contenu = grid_sizer_contenu
                
    def SetValeur(self, valeur=""):
        # Label
        self.ctrl.SetLabel(valeur)
        self.SetBackgroundColour(wx.Colour(100, 100, 100))
        self.grid_sizer_contenu.Layout()
        self.Refresh() 

        
# -------------------------------------------------------------------------------------------------------------------



            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, grille=None): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.grille = grille
        self.date = None
        
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(TR_COLUMN_LINES |  wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT | HTL.TR_NO_HEADER)
                    
    def MAJ(self, date=None):
        """ Met à jour (redessine) tout le contrôle """
        if date != None :
            self.date = date
        self.Freeze()
        self.DeleteAllItems()
        for numColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(numColonne)
        # Création de la racine
        self.Remplissage()
        self.Thaw() 

    def Remplissage(self):
        self.dictGroupes = self.grille.dictGroupes
        self.dictActivites = self.grille.dictActivites
        self.listeActivites = self.grille.listeActivites
        self.dictListeUnites = self.grille.dictListeUnites
        self.dictUnites = self.grille.dictUnites
        self.dictRemplissage = self.grille.dictRemplissage
        self.dictRemplissage2 = self.grille.dictRemplissage2
        self.dictUnitesRemplissage = self.grille.dictUnitesRemplissage
        self.dictConsoUnites = self.grille.dictConsoUnites
        
        self.dictBranches = { "activites" : {}, "groupes" : {}, "totaux" : {} }
        
        # tri des groupes par ordre
        listeGroupes = []
        for IDgroupe, dictGroupe in self.dictGroupes.items() :
            listeGroupes.append((dictGroupe["ordre"], IDgroupe))
        listeGroupes.sort()
        
        # Récupération des groupes par activité
        self.dictGroupeTmp = {}
        for ordre, IDgroupe in listeGroupes :
            dictGroupe = self.dictGroupes[IDgroupe]
            IDactivite = dictGroupe["IDactivite"]
            if (IDactivite in self.dictGroupeTmp) == False :
                self.dictGroupeTmp[IDactivite] = []
            self.dictGroupeTmp[IDactivite].append((IDgroupe, dictGroupe["nom"]))
        
        # Si groupe unique
        for IDactivite in self.listeActivites :
            if (IDactivite in self.dictGroupeTmp) == False :
                self.dictGroupeTmp[IDactivite] = [(0, _(u"Groupe unique")),]
        
        # Récupération des unités de remplissage
        self.dictUnitesRemplissageTemp = {}
        for IDunite_remplissage, dictUniteRemplissage in self.dictRemplissage.items() :
            if "IDactivite" in dictUniteRemplissage :
                IDactivite = dictUniteRemplissage["IDactivite"]
                abrege = dictUniteRemplissage["abrege"]
                ordre = dictUniteRemplissage["ordre"]
                if (IDactivite in self.dictUnitesRemplissageTemp) == False :
                    self.dictUnitesRemplissageTemp[IDactivite] = []
                self.dictUnitesRemplissageTemp[IDactivite].append((ordre, IDunite_remplissage, abrege))
                self.dictUnitesRemplissageTemp[IDactivite].sort()
            
        # Préparation des colonnes
        listeColonnes = [
            ( _(u"Groupe"), 150, wx.ALIGN_LEFT),
            ]
        listeNbreUnites = []
        for IDactivite in self.listeActivites :
            nbre = 0
            if IDactivite in self.dictListeUnites :
                nbre += len(self.dictListeUnites[IDactivite])
            if IDactivite in self.dictUnitesRemplissageTemp :
                nbre += len(self.dictUnitesRemplissageTemp[IDactivite])
            listeNbreUnites.append(nbre)
        
        if len(listeNbreUnites) == 0: 
            return
            
        for x in range(0, max(listeNbreUnites)):
            listeColonnes.append((u"", 50, wx.ALIGN_CENTER))
            
        # Création des colonnes
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        # Création des branches
        for IDactivite in self.listeActivites :
            
            # Label activité
            label = self.dictActivites[IDactivite]["nom"] if IDactivite in self.dictActivites else u"?"
            activite = self.AppendItem(self.root, label)
            self.dictBranches["activites"][IDactivite] = activite
            self.SetPyData(activite, IDactivite)
            self.SetItemBold(activite, True)
            self.SetItemBackgroundColour(activite, wx.Colour(200, 200, 200))
            
            # Entete de colonnes : UNITES
            indexColonne = 1
            if IDactivite in self.dictListeUnites:
                for dictUnite in self.dictListeUnites[IDactivite] :
                    nomUnite = dictUnite["abrege"]
                    self.SetItemText(activite, nomUnite, indexColonne)
                    indexColonne += 1
            
            # Entete de colones : UNITES DE REMPLISSAGE
            if IDactivite in self.dictUnitesRemplissageTemp : 
                for ordre, IDunite_remplissage, nomUniteRemplissage in self.dictUnitesRemplissageTemp[IDactivite] :
                    self.SetItemText(activite, nomUniteRemplissage, indexColonne)
                    indexColonne += 1
                
            # Lignes : GROUPES
            dictTotaux = {}
            for IDgroupe, nomGroupe in self.dictGroupeTmp[IDactivite] :
                groupe = self.AppendItem(activite, nomGroupe)
                self.dictBranches["groupes"][IDgroupe] = groupe
                self.SetPyData(groupe, IDgroupe)
                                        
            # Ligne TOTAL
            total = self.AppendItem(activite, _(u"Total"))
            self.dictBranches["totaux"][IDactivite] = total
            self.SetPyData(total, None)
            self.SetItemTextColour(total, wx.RED)
            
        self.ExpandAllChildren(self.root)
        
        # Remplit les chiffres dans le tableau
        self.MAJ_contenu() 

    def MAJ_donnees(self):
        """ Récupère les données """
        self.dictGroupes = self.grille.dictGroupes
        self.dictActivites = self.grille.dictActivites
        self.listeActivites = self.grille.listeActivites
        self.dictListeUnites = self.grille.dictListeUnites
        self.dictUnites = self.grille.dictUnites
        self.dictRemplissage = self.grille.dictRemplissage
        self.dictRemplissage2 = self.grille.dictRemplissage2
        self.dictUnitesRemplissage = self.grille.dictUnitesRemplissage
        self.dictConsoUnites = self.grille.dictConsoUnites

    def MAJ_contenu(self):
        """ Remplissage du tableau avec les chiffres """
        for IDactivite in self.listeActivites :
                
            # Lignes : GROUPES
            dictTotaux = {}
            for IDgroupe, nomGroupe in self.dictGroupeTmp[IDactivite] :
                groupe = self.dictBranches["groupes"][IDgroupe]
                
                # Nbre d'unités
                indexColonne = 1
                if IDactivite in self.dictListeUnites:
                    for dictUnite in self.dictListeUnites[IDactivite] :
                        IDunite = dictUnite["IDunite"]
                        try :
                            nbre = self.dictConsoUnites[IDunite][IDgroupe]
                            if (indexColonne in dictTotaux) == False :
                                dictTotaux[indexColonne] = 0
                            dictTotaux[indexColonne] += nbre
                        except :
                            nbre = 0
                        if nbre != 0 :
                            self.SetItemText(groupe, str(nbre), indexColonne)
                        else:
                            self.SetItemText(groupe, "", indexColonne)
                        indexColonne += 1
                    
                # Total par unité de remplissage
                if IDactivite in self.dictUnitesRemplissageTemp : 
                    for ordre, IDunite_remplissage, nomUniteRemplissage in self.dictUnitesRemplissageTemp[IDactivite] :
                        nbre = 0
                        if IDunite_remplissage in self.dictRemplissage2 :
                            if self.date in self.dictRemplissage2[IDunite_remplissage] :
                                if IDgroupe in self.dictRemplissage2[IDunite_remplissage][self.date] :
                                    d = self.dictRemplissage2[IDunite_remplissage][self.date][IDgroupe]
                                    if "reservation" in d : nbre += d["reservation"]
                                    if "present" in d : nbre += d["present"]
                                    if (indexColonne in dictTotaux) == False :
                                        dictTotaux[indexColonne] = 0
                                    dictTotaux[indexColonne] += nbre
                                    
                        if nbre != 0 :
                            self.SetItemText(groupe, str(nbre), indexColonne)
                        else:
                            self.SetItemText(groupe, "", indexColonne)
                            
                        indexColonne += 1
                
            # Ligne TOTAL
            total = self.dictBranches["totaux"][IDactivite]
            for indexColonne in range(1, self.GetColumnCount()) :
                if indexColonne in dictTotaux :
                    nbre = dictTotaux[indexColonne]
                    if nbre != 0 :
                        self.SetItemText(total, str(nbre), indexColonne)
                else:
                    self.SetItemText(total, "", indexColonne)

                    
    def OnCompareItems(self, item1, item2):
        if self.GetPyData(item1) > self.GetPyData(item2) :
            return 1
        elif self.GetPyData(item1) < self.GetPyData(item2) :
            return -1
        else:
            return 0
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
    

