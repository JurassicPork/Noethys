#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import os
import six
import GestionDB
import datetime, calendar
import shutil
import os.path
import wx.propgrid as wxpg
from Ctrl import CTRL_Propertygrid
from Ctrl.CTRL_Propertygrid import Propriete_date
from Utils import UTILS_Dates, UTILS_Texte, UTILS_Fichiers
from Data import DATA_Bic
import FonctionsPerso
import wx.lib.dialogs as dialogs
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Facturation
from Utils import UTILS_Organisateur
from Utils import UTILS_Parametres
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Dlg import DLG_Saisie_lot_tresor_public

if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DP_DROPDOWN as DP_DROPDOWN
    from wx.adv import DP_SHOWCENTURY as DP_SHOWCENTURY
else :
    from wx import DP_DROPDOWN as DP_DROPDOWN
    from wx import DP_SHOWCENTURY as DP_SHOWCENTURY



class CTRL_Parametres(DLG_Saisie_lot_tresor_public.CTRL_Parametres):
    def __init__(self, parent, IDlot=None):
        DLG_Saisie_lot_tresor_public.CTRL_Parametres.__init__(self, parent, IDlot=IDlot)
        self.parent = parent

    def Remplissage(self):
        # Bordereau
        self.Append(wxpg.PropertyCategory(_(u"Généralités")))
        
        propriete = wxpg.IntProperty(label=_(u"Exercice"), name="exercice", value=datetime.date.today().year)
        propriete.SetHelpString(_(u"Saisissez l'année de l'exercice")) 
        self.Append(propriete)
        self.SetPropertyEditor("exercice", "SpinCtrl")
        
        listeMois = [u"_", _(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")]
        propriete = wxpg.EnumProperty(label=_(u"Mois"), name="mois", labels=listeMois, values=range(0, 13) , value=datetime.date.today().month)
        propriete.SetHelpString(_(u"Sélectionnez le mois"))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Objet"), name="objet_dette", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'objet du bordereau (Ex : 'Cantine décembre 2020')"))
        self.Append(propriete)

        # Dates
        self.Append( wxpg.PropertyCategory(_(u"Dates")) )

        propriete = Propriete_date(label=_(u"Date d'émission (JJ/MM/AAAA)"), name="date_emission", value=datetime.date.today())
        self.Append(propriete)

        propriete = Propriete_date(label=_(u"Date du prélèvement (JJ/MM/AAAA)"), name="date_prelevement", value=datetime.date.today())
        self.Append(propriete)

        propriete = Propriete_date(label=_(u"Avis d'envoi (JJ/MM/AAAA)"), name="date_envoi", value=datetime.date.today())
        self.Append(propriete)

        # Collectivité
        self.Append( wxpg.PropertyCategory(_(u"Identification")) )

        propriete = wxpg.StringProperty(label=_(u"Code Collectivité"), name="code_collectivite", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Collectivité")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Code Budget"), name="code_budget", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Budget")) 
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Poste par défaut"), name="id_poste", value=u"")
        propriete.SetHelpString(_(u"Saisissez le poste par défaut. C'est celui qui sera utilisé si le champ 'code comptable' n'est pas renseigné dans la prestation ou dans le paramétrage de l'activité."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Code Produit Local par défaut"), name="code_prodloc", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Produit Local. C'est celui qui sera utilisé si le champ 'code produit local' n'est pas renseigné dans la prestation ou dans le paramétrage de l'activité."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Code Service par défaut"), name="service", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code du service. C'est celui qui sera utilisé si le champ 'code service' n'est pas renseigné dans le paramétrage de l'activité."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Opération"), name="operation", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code de l'opération."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Fonction"), name="fonction", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code de la fonction."))
        self.Append(propriete)

        # Options
        self.Append(wxpg.PropertyCategory(_(u"Options")))

        propriete = wxpg.BoolProperty(label=_(u"Titre payable par internet"), name="tipi", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si l'usager peut payer sur internet avec TIPI (PayFip)"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        choix = [
            ("", _(u"ASAP non dématérialisé")),
            ("01", _(u"01-ASAP dématérialisé à éditer par le centre éditique")),
            ("02", _(u"02-ASAP dématérialisé à destination d'une entité publique référencée dans Chorus Pro")),
            ("03", _(u"03-ASAP ORMC Chorus Pro")),
            ("04", _(u"04-ASAP sans traitement DGFIP")),
        ]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Edition ASAP"), name="edition_asap", liste_choix=choix, valeur="01")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Indiquez si l'ASAP doit être édité ou non par le centre éditique (Balise Edition dans bloc pièce du PES Titre)"))
        self.Append(propriete)

        propriete = wxpg.BoolProperty(label=_(u"Inclure le détail des factures"), name="inclure_detail", value=False)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys intègre le détail des prestations de chaque facture"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        propriete = wxpg.BoolProperty(label=_(u"Inclure les factures au format PDF"), name="inclure_pieces_jointes", value=False)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys intègre les factures au format PDF"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        choix = [
            ("002", _(u"Recette")),
            ("006", _(u"Facture PES")),
            ("007", _(u"Facture ORMC")),
            ("008", _(u"Document compl�mentaire ASAP")),
        ]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Type de la pi�ce jointe"), name="type_pj", liste_choix=choix, valeur="006")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"S�lectionnez le type de la pi�ce jointe"))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Nom du tribunal de recours"), name="tribunal", value=_(u"le tribunal administratif"))
        propriete.SetHelpString(_(u"Saisissez le nom du tribunal"))
        self.SetPropertyMaxLength(propriete, 100)
        self.Append(propriete)

        propriete = wxpg.BoolProperty(label=_(u"Utiliser code comptable familial comme code tiers"), name="code_compta_as_alias", value=True)
        propriete.SetHelpString(_(u"Utiliser le code comptable de la famille (Fiche famille > Onglet Divers) comme code tiers (ou alias). Sinon un code de type FAM000001 sera généré automatiquement."))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Libellés
        self.Append( wxpg.PropertyCategory(_(u"Libellés")) )

        propriete = wxpg.StringProperty(label=_(u"Objet de la pièce"), name="objet_piece", value=_(u"FACTURE NUM{NUM_FACTURE} {MOIS_LETTRES} {ANNEE}"))
        propriete.SetHelpString(_(u"Saisissez l'objet de la pièce (en majuscules et sans accents). Vous pouvez personnaliser ce libellé grâce aux mots-clés suivants : {NOM_ORGANISATEUR} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Libellé du prélèvement"), name="prelevement_libelle", value=u"{NOM_ORGANISATEUR} - {OBJET_PIECE}")
        propriete.SetHelpString(_(u"Saisissez le libellé du prélèvement qui apparaîtra sur le relevé de compte de la famille. Vous pouvez personnaliser ce libellé grâce aux mots-clés suivants : {NOM_ORGANISATEUR} {OBJET_PIECE} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
        self.Append(propriete)

        # Règlement automatique
        self.Append( wxpg.PropertyCategory(_(u"Règlement automatique")) )
        
        propriete = wxpg.BoolProperty(label=_(u"Régler automatiquement"), name="reglement_auto", value=False)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys créé un règlement automatiquement pour les prélèvements")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        propriete = wxpg.EnumProperty(label=_(u"Compte à créditer"), name="IDcompte")
        propriete.SetHelpString(_(u"Sélectionnez le compte bancaire à créditer dans le cadre du règlement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_comptes() 

        propriete = wxpg.EnumProperty(label=_(u"Mode de règlement"), name="IDmode")
        propriete.SetHelpString(_(u"Sélectionnez le mode de règlement à utiliser dans le cadre du règlement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_modes()

        # Préférences
        self.SetPropertyValue("tipi", UTILS_Parametres.Parametres(mode="get", categorie="export_magnus", nom="tipi", valeur=True))
        self.SetPropertyValue("edition_asap", UTILS_Parametres.Parametres(mode="get", categorie="export_magnus", nom="edition_asap", valeur="01"))
        self.SetPropertyValue("type_pj", UTILS_Parametres.Parametres(mode="get", categorie="export_magnus", nom="type_pj", valeur="006"))
        self.SetPropertyValue("inclure_pieces_jointes", UTILS_Parametres.Parametres(mode="get", categorie="export_magnus", nom="inclure_pieces_jointes", valeur=False))
        self.SetPropertyValue("inclure_detail", UTILS_Parametres.Parametres(mode="get", categorie="export_magnus", nom="inclure_detail", valeur=False))
        self.SetPropertyValue("tribunal", UTILS_Parametres.Parametres(mode="get", categorie="export_magnus", nom="tribunal", valeur=u"le tribunal administratif"))
        self.SetPropertyValue("code_compta_as_alias", UTILS_Parametres.Parametres(mode="get", categorie="export_magnus", nom="code_compta_as_alias", valeur=True))
        self.SetPropertyValue("service", UTILS_Parametres.Parametres(mode="get", categorie="export_magnus", nom="service", valeur=u""))



# ---------------------------------------------------------------------------------------------------------------------------------


class Dialog(DLG_Saisie_lot_tresor_public.Dialog):
    def __init__(self, parent, IDlot=None, format=None):
        DLG_Saisie_lot_tresor_public.Dialog.__init__(self, parent, IDlot=IDlot, format=format, ctrl_parametres=CTRL_Parametres)
        self.parent = parent


    def ValidationDonnees(self):
        """ Vérifie que les données saisies sont exactes """
        # Généralités
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de lot (Ex : 'Janvier 2013'...) !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
 
        for caract in nom :
            if caract in ("_",) :
                dlg = wx.MessageDialog(self, _(u"Le caractère '%s' n'est pas autorisé dans le nom du lot !") % caract, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_nom.SetFocus() 
                return False

        # Vérifie que le nom n'est pas déjà attribué
        if self.IDlot == None :
            IDlotTemp = 0
        else :
            IDlotTemp = self.IDlot
        DB = GestionDB.DB()
        req = """SELECT IDlot, nom
        FROM pes_lots
        WHERE nom='%s' AND IDlot!=%d;""" % (nom, IDlotTemp)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce nom de lot a déjà été attribué à un autre lot.\n\nChaque lot doit avoir un nom unique. Changez le nom."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
        
        observations = self.ctrl_observations.GetValue()
        
        if self.ctrl_verrouillage.GetValue() == True :
            verrouillage = 1
        else :
            verrouillage = 0

        # Récupération des données du CTRL Paramètres
        exercice = self.ctrl_parametres.GetPropertyValue("exercice")
        mois = self.ctrl_parametres.GetPropertyValue("mois")
        objet_dette = self.ctrl_parametres.GetPropertyValue("objet_dette")
        date_emission = self.ctrl_parametres.GetPropertyValue("date_emission")
        date_prelevement = self.ctrl_parametres.GetPropertyValue("date_prelevement")
        date_envoi = self.ctrl_parametres.GetPropertyValue("date_envoi")
        id_poste = self.ctrl_parametres.GetPropertyValue("id_poste")
        code_collectivite = self.ctrl_parametres.GetPropertyValue("code_collectivite")
        code_budget = self.ctrl_parametres.GetPropertyValue("code_budget")
        code_prodloc = self.ctrl_parametres.GetPropertyValue("code_prodloc")
        operation = self.ctrl_parametres.GetPropertyValue("operation")
        service = self.ctrl_parametres.GetPropertyValue("service")
        fonction = self.ctrl_parametres.GetPropertyValue("fonction")
        reglement_auto = int(self.ctrl_parametres.GetPropertyValue("reglement_auto"))
        IDcompte = self.ctrl_parametres.GetPropertyValue("IDcompte")
        IDmode = self.ctrl_parametres.GetPropertyValue("IDmode")
        tribunal = self.ctrl_parametres.GetPropertyValue("tribunal")
        
        # Vérification du compte à créditer
        if reglement_auto == 1 :
            if IDcompte == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un compte à créditer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if IDmode == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un mode de règlement pour le règlement automatique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Vérification des paramètres du bordereau
        listeVerifications = [
            (exercice, "exercice", _(u"l'année de l'exercice")),
            (mois, "mois", _(u"le mois")),
            (objet_dette, "objet_dette", _(u"l'objet de la dette")),
            (date_emission, "date_emission", _(u"la date d'émission")),
            (date_prelevement, "date_prelevement", _(u"la date souhaitée du prélèvement")),
            (date_envoi, "date_envoi", _(u"la date d'envoi")),
            (id_poste, "id_poste", _(u"l'ID poste")),
            (code_collectivite, "code_collectivite", _(u"le Code Collectivité")),
            (code_budget, "code_budget", _(u"le Code Bugdet")),
            (code_prodloc, "code_prodloc", _(u"le code Produit Local")),
            (tribunal, "tribunal", _(u"le tribunal de recours")),
            ]
            
        for donnee, code, label in listeVerifications :
            if donnee == None or donnee == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir %s dans les paramètres du lot !") % label, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code == "id_bordereau" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur numérique valide pour le paramètre de bordereau 'ID Bordereau' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

            if code == "id_collectivite" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur numérique valide pour le paramètre de bordereau 'ID Collectivité' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        # Vérification des pièces
        listeErreurs = []
        listeTemp1 = []
        for track in self.ctrl_pieces.GetObjects() :

            if track.analysePiece == False :
                listeErreurs.append(_(u"- Facture n°%s : %s") % (track.IDfacture, track.analysePieceTexte))
                
            # Vérifie qu'un OOFF ou un FRST n'est pas attribué 2 fois à un seul mandat
            if track.prelevement == 1 :
                if track.prelevement_sequence in ("OOFF", "FRST") :
                    key = (track.prelevement_IDmandat, track.prelevement_sequence)
                    if key in listeTemp1 :
                        if track.prelevement_sequence == "OOFF" : 
                            listeErreurs.append(_(u"- Facture n°%s : Le mandat n°%s de type ponctuel a déjà été utilisé une fois !") % (track.IDfacture, track.prelevement_IDmandat))
                        if track.prelevement_sequence == "FRST" : 
                            listeErreurs.append(_(u"- Facture n°%s : Mandat n°%s déjà initialisé. La séquence doit être définie sur 'RCUR' !") % (track.IDfacture, track.prelevement_IDmandat))
                    listeTemp1.append(key)
            
        if len(listeErreurs) > 0 :
            message1 = _(u"Le bordereau ne peut être validé en raison des erreurs suivantes :")
            message2 = "\n".join(listeErreurs)
            dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Erreur"), msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Ok")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            return False

        return True

    def Memorisation_parametres(self):
<<<<<<< HEAD
        # Mémorisation des préférences
        for code in ("tipi", "edition_asap", "inclure_detail", "inclure_pieces_jointes", "tribunal", "code_compta_as_alias", "service"):
=======
        # M�morisation des pr�f�rences
        for code in ("tipi", "edition_asap", "type_pj", "inclure_detail", "inclure_pieces_jointes", "tribunal", "code_compta_as_alias", "service"):
>>>>>>> ff5d149acb272662379069f7d1c9a97262e6fc88
            UTILS_Parametres.Parametres(mode="set", categorie="export_magnus", nom=code, valeur=self.ctrl_parametres.GetPropertyValue(code))

    def OnBoutonFichier(self, event):
        """ Génération d'un fichier normalisé """
        # Validation des données
        if self.ValidationDonnees() == False:
            return False

        # Vérifie que des pièces existent
        if not(self.ctrl_pieces.GetObjects()):
            dlg = wx.MessageDialog(self, _(u"Vous devez ajouter au moins une pièce !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Récupération des infos sur la remise
        remise_nom = DLG_Saisie_lot_tresor_public.Supprime_accent(self.ctrl_nom.GetValue())
        nom_fichier = remise_nom

        nomOrganisateur = UTILS_Organisateur.GetNom()

        # Création d'un répertoire temporaire
        rep_temp = UTILS_Fichiers.GetRepTemp("export_magnus")
        if os.path.isdir(rep_temp):
            shutil.rmtree(rep_temp)
        os.mkdir(rep_temp)

        # Génération des pièces jointes
        dict_pieces_jointes = {}
        if self.ctrl_parametres.GetPropertyValue("inclure_pieces_jointes") == True :
            dict_pieces_jointes = self.GenerationPiecesJointes(repertoire=rep_temp)
            if not dict_pieces_jointes:
                return False

        # Récupération des transactions à effectuer
        montantTotal = FloatToDecimal(0.0)
        nbreTotal = 0
        listeAnomalies = []
        listePieces = []
        for track in self.ctrl_pieces.GetObjects():
            montant = FloatToDecimal(track.montant)

            if track.analysePiece == False:
                listeAnomalies.append(u"%s : %s" % (track.libelle, track.analysePieceTexte))

            # Objet de la pièce
            objet_piece = self.ctrl_parametres.GetPropertyValue("objet_piece")
            objet_piece = DLG_Saisie_lot_tresor_public.Supprime_accent(objet_piece).upper()
            objet_piece = objet_piece.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            objet_piece = objet_piece.replace("{NUM_FACTURE}", str(track.numero))
            objet_piece = objet_piece.replace("{LIBELLE_FACTURE}", track.libelle)
            objet_piece = objet_piece.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            objet_piece = objet_piece.replace("{MOIS_LETTRES}", DLG_Saisie_lot_tresor_public.GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            objet_piece = objet_piece.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))

            # Création du libellé du prélèvement
            prelevement_libelle = self.ctrl_parametres.GetPropertyValue("prelevement_libelle")
            prelevement_libelle = prelevement_libelle.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            prelevement_libelle = prelevement_libelle.replace("{OBJET_PIECE}", objet_piece)
            prelevement_libelle = prelevement_libelle.replace("{LIBELLE_FACTURE}", track.libelle)
            prelevement_libelle = prelevement_libelle.replace("{NUM_FACTURE}", str(track.numero))
            prelevement_libelle = prelevement_libelle.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            prelevement_libelle = prelevement_libelle.replace("{MOIS_LETTRES}", DLG_Saisie_lot_tresor_public.GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            prelevement_libelle = prelevement_libelle.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))

            dictPiece = {
                "id_piece": str(track.IDfacture),
                "objet_piece": objet_piece,
                "num_dette": str(track.numero),
                "montant": montant,
                "sequence": track.prelevement_sequence,
                "prelevement": track.prelevement,
                "prelevement_date_mandat": str(track.prelevement_date_mandat),
                "prelevement_rum": track.prelevement_rum,
                "prelevement_bic": track.prelevement_bic,
                "prelevement_iban": track.prelevement_iban,
                "prelevement_titulaire": track.prelevement_titulaire,
                "prelevement_libelle": prelevement_libelle,
                "titulaire_civilite": track.titulaireCivilite,
                "titulaire_nom": track.titulaireNom,
                "titulaire_prenom": track.titulairePrenom,
                "titulaire_rue": track.titulaireRue,
                "titulaire_cp": track.titulaireCP,
                "titulaire_ville": track.titulaireVille,
                "idtiers_helios": track.idtiers_helios,
                "natidtiers_helios": track.natidtiers_helios,
                "reftiers_helios": track.reftiers_helios,
                "cattiers_helios": track.cattiers_helios,
                "natjur_helios": track.natjur_helios,
                "IDfacture" : track.IDfacture,
                "code_compta" : track.code_compta,
                "code_tiers": track.code_tiers,
            }
            listePieces.append(dictPiece)
            montantTotal += montant
            nbreTotal += 1

        if len(listeAnomalies) > 0:
            import wx.lib.dialogs as dialogs
            message = "\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, _(u"Le fichier ne peut être généré en raison des anomalies suivantes :"), caption=_(u"Génération impossible"), msg2=message, style=wx.ICON_ERROR | wx.OK, icon=None, btnLabels={wx.ID_OK: _(u"Fermer")})
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Mémorisation de toutes les données
        dictDonnees = {
            "nom_fichier": nom_fichier,
            "date_emission": UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_emission")).strftime("%Y-%m-%d"),
            "date_envoi": UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_envoi")).strftime("%Y-%m-%d"),
            "date_prelevement": UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_prelevement")).strftime("%Y-%m-%d"),
            "id_poste": self.ctrl_parametres.GetPropertyValue("id_poste"),
            "code_collectivite": self.ctrl_parametres.GetPropertyValue("code_collectivite"),
            "code_budget": self.ctrl_parametres.GetPropertyValue("code_budget"),
            "operation": self.ctrl_parametres.GetPropertyValue("operation"),
            "service": self.ctrl_parametres.GetPropertyValue("service"),
            "fonction": self.ctrl_parametres.GetPropertyValue("fonction"),
            "exercice": str(self.ctrl_parametres.GetPropertyValue("exercice")),
            "mois": str(self.ctrl_parametres.GetPropertyValue("mois")),
            "montant_total": str(montantTotal),
            "objet_dette": self.ctrl_parametres.GetPropertyValue("objet_dette"),
            "code_prodloc": self.ctrl_parametres.GetPropertyValue("code_prodloc"),
            "tribunal": self.ctrl_parametres.GetPropertyValue("tribunal"),
            "tipi": self.ctrl_parametres.GetPropertyValue("tipi"),
            "edition_asap": self.ctrl_parametres.GetPropertyValue("edition_asap"),
            "type_pj": self.ctrl_parametres.GetPropertyValue("type_pj"),
            "pieces": listePieces,
            "pieces_jointes" : dict_pieces_jointes,
        }

        # Calcul des dates extrêmes du mois
        nbreJoursMois = calendar.monthrange(int(dictDonnees["exercice"]), int(dictDonnees["mois"]))[1]
        dictDonnees["date_min"] = datetime.date(int(dictDonnees["exercice"]), int(dictDonnees["mois"]), 1)
        dictDonnees["date_max"] = datetime.date(int(dictDonnees["exercice"]), int(dictDonnees["mois"]), nbreJoursMois)

        # Récupération du détail des factures
        detail_factures, dict_prestations_factures = self.Get_detail_pieces(dictDonnees)
        dictDonnees["detail"] = detail_factures
        dictDonnees["prestations"] = dict_prestations_factures

        # Recherche poste et code local
        dict_codes = {}
        for IDfacture, liste_prestations in dict_prestations_factures.items():
            if IDfacture not in dict_codes:
                dict_codes[IDfacture] = {}
            for dict_prestation in liste_prestations:
                key = (dict_prestation["id_poste"], dict_prestation["code_prodloc"], dict_prestation["code_service"])
                if key not in dict_codes[IDfacture]:
                    dict_codes[IDfacture][key] = FloatToDecimal(0.0)
                dict_codes[IDfacture][key] += dict_prestation["montant"]

        dictDonnees["codes"] = dict_codes

        # Génération des fichiers
        resultat = self.Generer_fichier(dictDonnees, repertoire=rep_temp)
        if not resultat:
            return False

        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier ZIP (*.zip)|*.zip| All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message=_(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"),
            defaultDir=cheminDefaut,
            defaultFile=nom_fichier,
            wildcard=wildcard,
            style=wx.FD_SAVE
        )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True:
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), _(u"Attention !"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO:
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Création du fichier ZIP
        shutil.make_archive(cheminFichier.replace(".zip", ""), "zip", rep_temp)

        # Confirmation de création du fichier
        dlg = wx.MessageDialog(self, _(u"Le fichier a été créé avec succès.\n\nPensez à décompresser ce fichier avant l'import dans Magnus."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


    def Get_detail_pieces(self, dict_donnees={}):
        listeIDfacture = [piece["IDfacture"] for piece in dict_donnees["pieces"]]

        if len(listeIDfacture) == 0: conditionFactures = "()"
        elif len(listeIDfacture) == 1: conditionFactures = "(%d)" % listeIDfacture[0]
        else: conditionFactures = str(tuple(listeIDfacture))

        DB = GestionDB.DB()
        req = """SELECT 
        prestations.IDprestation, prestations.date, prestations.montant, prestations.IDfacture, prestations.label,
        prestations.IDindividu, individus.nom, individus.prenom,
        SUM(ventilation.montant) AS montant_ventilation,
        prestations.code_compta, prestations.code_produit_local,
        activites.code_comptable, activites.code_produit_local, activites.code_service
        FROM prestations
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        LEFT JOIN ventilation ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        WHERE prestations.IDfacture IN %s
        GROUP BY prestations.IDprestation
        ;""" % conditionFactures
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dict_resultats = {}
        dict_prestations_factures = {}
        for IDprestation, date, montant, IDfacture, label, IDindividu, nom, prenom, montant_ventilation, code_compta, code_produit_local, activite_code_compta, activite_code_produit_local, activite_code_service in listeDonnees:
            montant = FloatToDecimal(montant)

            # Recherche le code compta et le code prod local
            id_poste = dict_donnees["id_poste"]
            code_prodloc = dict_donnees["code_prodloc"]
            code_service = dict_donnees["service"]
            if activite_code_compta: id_poste = activite_code_compta
            if activite_code_produit_local: code_prodloc = activite_code_produit_local
            if activite_code_service: code_service = activite_code_service
            if code_compta: id_poste = code_compta
            if code_produit_local: code_prodloc = code_produit_local

            if IDfacture not in dict_prestations_factures:
                dict_prestations_factures[IDfacture] = []
            dict_prestations_factures[IDfacture].append({"IDprestation": IDprestation, "label": label, "montant": montant, "id_poste": id_poste, "code_prodloc": code_prodloc, "code_service": code_service})

            # Définit le label
            if IDindividu:
                label = u"%s - %s" % (label, prenom)
            libelle = (label, montant)

            if IDfacture not in dict_resultats:
                dict_resultats[IDfacture] = {}
            if IDindividu not in dict_resultats[IDfacture]:
                dict_resultats[IDfacture][IDindividu] = {}
            if libelle not in dict_resultats[IDfacture][IDindividu]:
                dict_resultats[IDfacture][IDindividu][libelle] = 0
            dict_resultats[IDfacture][IDindividu][libelle] += 1

        dict_resultats2 = {}
        for IDfacture, dict_facture in dict_resultats.items():
            if IDfacture not in dict_resultats2:
                dict_resultats2[IDfacture] = []
            for IDindividu, dict_individu in dict_facture.items():
                for (libelle, montant), quantite in dict_individu.items():
                    dict_resultats2[IDfacture].append({"libelle": libelle, "quantite": quantite, "montant": montant})
                dict_resultats2[IDfacture].sort(key=lambda x: x["libelle"])

        return dict_resultats2, dict_prestations_factures

    def GenerationPiecesJointes(self, repertoire=""):
        """ Génération des pièces jointes """
        IDfichier = FonctionsPerso.GetIDfichier()

        listeIDfacture = []
        dictTracks = {}
        for track in self.ctrl_pieces.GetObjects():
            listeIDfacture.append(track.IDfacture)
            dictTracks[track.IDfacture] = track

        # Création du répertoire
        repertoire_pj = os.path.join(UTILS_Fichiers.GetRepTemp("export_magnus"), "PJ")
        if not os.path.isdir(repertoire_pj):
            os.mkdir(repertoire_pj)

        # Génération des factures au format PDF
        nomFichierUnique = u"F{NUM_FACTURE}_{NOM_TITULAIRES_MAJ}"

        facturation = UTILS_Facturation.Facturation()
        resultat = facturation.Impression(listeFactures=listeIDfacture, nomFichierUnique=nomFichierUnique, afficherDoc=False, repertoireTemp=True)
        if resultat == False:
            return False
        dictChampsFusion, dictPieces = resultat

        # Conversion des fichiers en GZIP/base64
        dict_pieces_jointes = {}
        for IDfacture, cheminFichier in dictPieces.items() :
            NomPJ = os.path.basename(cheminFichier)
            numero_facture = dictTracks[IDfacture].numero
            IdUnique = IDfichier + str(numero_facture)
            shutil.move(cheminFichier, os.path.join(repertoire_pj, NomPJ))

            dict_pieces_jointes[IDfacture] = {"NomPJ": NomPJ, "IdUnique": IdUnique, "numero_facture": numero_facture}

        return dict_pieces_jointes

    def Generer_fichier(self, dict_donnees={}, repertoire=""):

        def ConvertToTexte(valeur, majuscules=False):
            if majuscules and valeur:
                valeur = UTILS_Texte.Supprime_accent(valeur.upper())
            valeur = u'"%s"' % valeur
            valeur = valeur.replace("\n", " ")
            valeur = valeur.replace("\r", " ")
            valeur = valeur.strip()
            return valeur

        lignes = []
        lignes_pj = []
        lignes_detail = []
        for IdEcriture, piece in enumerate(dict_donnees["pieces"], start=1):
            num_sous_ligne = 1
            if piece["IDfacture"] in dict_donnees["codes"]:
                for (IDposte, code_produit_local, code_service), montant in dict_donnees["codes"][piece["IDfacture"]].items():
                    ligne = {}

                    # IDEcriture - Texte (50)
                    ligne[1] = ConvertToTexte(IdEcriture)

                    # Type - Texte (1)
                    ligne[2] = ConvertToTexte("T")

                    # Reelle - Texte (1)
                    ligne[3] = ConvertToTexte("O")

                    # Collectivité - Texte (10)
                    ligne[4] = ConvertToTexte(dict_donnees["code_collectivite"][:10])

                    # Budget - Texte (10)
                    ligne[5] = ConvertToTexte(dict_donnees["code_budget"][:10])

                    # Exercice - Entier
                    ligne[6] = ConvertToTexte(dict_donnees["exercice"])

                    # Multiple - Texte (1)
                    ligne[7] = ConvertToTexte("M" if num_sous_ligne == 1 else "S")

                    # CodeTiers - Texte (15)
                    ligne[8] = ConvertToTexte(piece["code_tiers"][:15])
                    if self.ctrl_parametres.GetPropertyValue("code_compta_as_alias") == True and piece["code_compta"]:
                        ligne[8] = ConvertToTexte(piece["code_compta"][:15])

                    # Designation1 - Texte (50)
                    ligne[10] = ConvertToTexte(piece["titulaire_nom"][:50], majuscules=True)

                    # Designation2 - Texte (50)
                    ligne[11] = ConvertToTexte(piece["titulaire_prenom"][:50], majuscules=True)

                    # AdrLig1, AdrLig2, et AdrLig3 - Texte (50)
                    if piece["titulaire_rue"]:
                        lignes_rue = piece["titulaire_rue"].split("\n")
                        for idx, valeur in enumerate(lignes_rue[:3], 12):
                            ligne[idx] = ConvertToTexte(valeur[:50], majuscules=True)

                    # Codepostal - Texte (10)
                    ligne[15] = ConvertToTexte(piece["titulaire_cp"][:10])

                    # Ville - Texte (50)
                    ligne[16] = ConvertToTexte(piece["titulaire_ville"][:50])

                    # Libelle1 - Texte (50)
                    ligne[18] = ConvertToTexte(dict_donnees["objet_dette"][:50])

                    # PièceJustificative1 - Texte (50)
                    ligne[20] = ConvertToTexte(piece["objet_piece"][:50])

                    # Sens - Texte (1)
                    ligne[24] = ConvertToTexte("R")

                    # Date - Texte (10)
                    ligne[25] = ConvertToTexte(UTILS_Dates.DateEngFr(dict_donnees["date_emission"]))

                    # Article - Texte (10)
                    ligne[26] = ConvertToTexte(IDposte[:10])

                    # Opération - Texte (10)
                    ligne[27] = ConvertToTexte(dict_donnees["operation"][:10])

                    # Service - Texte (15)
                    ligne[28] = ConvertToTexte(code_service[:15])

                    # Fonction - Texte (10)
                    ligne[29] = ConvertToTexte(dict_donnees["fonction"][:10])

                    # Montant HT - Monétaire (,4)
                    ligne[30] = ConvertToTexte(str(montant))

                    # Montant TVA - Monétaire (,4)
                    ligne[31] = ConvertToTexte("0.00")

                    # Solder - O/N
                    ligne[32] = ConvertToTexte("0")

                    # Priorité - Entier
                    ligne[33] = ConvertToTexte("0")

                    # Accepté
                    ligne[35] = ConvertToTexte("")

                    # Erroné
                    ligne[36] = ConvertToTexte("")

                    # NJ - Texte (2)
                    ligne[38] = ConvertToTexte(piece["natjur_helios"][:2])

                    # TvaTaux - Reel Simple (5)
                    ligne[40] = ConvertToTexte("0.00")

                    # Mixte - Texte (1)
                    ligne[44] = ConvertToTexte("N")

                    # Imprévisible - Texte (1)
                    ligne[45] = ConvertToTexte("N")

                    # CodeAlim - Texte (1)
                    ligne[46] = ConvertToTexte("N")

                    # MarcheSim - Texte (1)
                    ligne[47] = ConvertToTexte("N")

                    # SuiviDelai - Texte (1)
                    ligne[50] = ConvertToTexte("N")

                    # DelaiPaiement - Entier
                    ligne[51] = ConvertToTexte("0")

                    # CPL - Texte (4)
                    ligne[54] = ConvertToTexte(code_produit_local[:4])

                    # Prélèvement :
                    if piece["prelevement"] == 1:

                        # CodeEtab - Texte (5)
                        ligne[59] = ConvertToTexte(piece["prelevement_iban"][4:9])

                        # CodeGuic - Texte (5)
                        ligne[60] = ConvertToTexte(piece["prelevement_iban"][9:14])

                        # IdCpte - Texte (11)
                        ligne[61] = ConvertToTexte(piece["prelevement_iban"][14:25])

                        # CleRib - Texte (2)
                        ligne[62] = ConvertToTexte(piece["prelevement_iban"][25:27])

                        # LibBanc - Texte (24)
                        infos_banque = DATA_Bic.RechercherBIC(piece["prelevement_bic"])
                        nom_banque = infos_banque[0] if infos_banque else ""
                        ligne[63] = ConvertToTexte(nom_banque[:24])

                        # TitCpte - Texte (32)
                        ligne[64] = ConvertToTexte(piece["prelevement_titulaire"][:32], majuscules=True)

                        # IBAN - Texte (34)
                        ligne[65] = ConvertToTexte(piece["prelevement_iban"][:34])

                        # BIC - Texte (11)
                        ligne[66] = ConvertToTexte(piece["prelevement_bic"][:11])

                    # Tribunal - Texte (100)
                    ligne[68] = ConvertToTexte(dict_donnees["tribunal"][:100])

                    # Civilité - Texte (32)
                    if piece["titulaire_civilite"] == u"M.": ligne[69] = ConvertToTexte("M")
                    if piece["titulaire_civilite"] == u"Mme": ligne[69] = ConvertToTexte("MME")
                    if piece["titulaire_civilite"] == u"Melle": ligne[69] = ConvertToTexte("MLLE")

                    # TIPI - O/N
                    ligne[70] = ConvertToTexte("O" if dict_donnees["tipi"] else "N")

                    # PrelevementSEPA - O/N
                    ligne[71] = ConvertToTexte("O" if piece["prelevement"] == 1 else "N")

                    # DatePrel - Texte (10)
                    if piece["prelevement"] == 1:
                        ligne[72] = ConvertToTexte(UTILS_Dates.DateEngFr(dict_donnees["date_prelevement"]))

                        # PeriodicitePrel - Texte (2)
                        ligne[73] = ConvertToTexte("02") # Mensuel

                        # ICS - Texte (13)
                        IDcompte = self.ctrl_parametres.GetPropertyValue("IDcompte")
                        if not IDcompte:
                            dlg = wx.MessageDialog(self, _(u"Au moins un prélèvement SEPA est demandé. Vous devez donc sélectionner un compte bancaire créditeur dans les paramètres !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                            dlg.ShowModal()
                            dlg.Destroy()
                            return False

                        dict_compte = self.ctrl_parametres.dictComptes[IDcompte]
                        if not dict_compte["code_ics"]:
                            dlg = wx.MessageDialog(self, _(u"Au moins un prélèvement SEPA est demandé. Vous devez donc renseigner le numéro ICS dans les paramètres du compte bancaire créditeur !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                            dlg.ShowModal()
                            dlg.Destroy()
                            return False

                        ligne[74] = ConvertToTexte(dict_compte["code_ics"]) if dict_compte["code_ics"] else ""

                        # RUM - Texte (35)
                        ligne[75] = ConvertToTexte(piece["prelevement_rum"])

                    # RUMMigre - O/N
                    ligne[76] = ConvertToTexte("N")

                    # RUM - Texte (35)
                    if piece["prelevement"] == 1:
                        ligne[77] = ConvertToTexte(UTILS_Dates.DateEngFr(piece["prelevement_date_mandat"]))

                        # LibellePrel - Texte (140)
                        ligne[78] = ConvertToTexte(piece["prelevement_libelle"][:140])

                        # SequencePrel - Texte (02)
                        if piece["sequence"] == "FRST":
                            sequence = "02"
                        elif piece["sequence"] == "RCUR":
                            sequence = "03"
                        elif piece["sequence"] == "FNAL":
                            sequence = "04"
                        else:
                            sequence = "01"
                        ligne[79] = ConvertToTexte(sequence)

                    # TitCpteDiff - O/N
                    ligne[80] = ConvertToTexte("N")

                    # AncienBanque - O/N
                    ligne[84] = ConvertToTexte("N")

                    # Version - Numérique (3)
                    ligne[90] = ConvertToTexte("18")

                    # CategorieTiersPES - Numérique (2)
                    ligne[91] = ConvertToTexte(piece["cattiers_helios"])

                    # NatJuridiqueTiersPES - Numérique (2)
                    ligne[92] = ConvertToTexte(piece["natjur_helios"])

                    # Civilité - Texte (32)
                    if piece["titulaire_civilite"] == u"M.": ligne[93] = ConvertToTexte("M")
                    if piece["titulaire_civilite"] == u"Mme": ligne[93] = ConvertToTexte("MME")
                    if piece["titulaire_civilite"] == u"Melle": ligne[93] = ConvertToTexte("MLLE")

                    # NatIdentifiantTiers - Numérique (2)
                    ligne[94] = ConvertToTexte(piece["natidtiers_helios"])

                    # IdentifiantTiers - Texte (18)
                    ligne[95] = ConvertToTexte(piece["idtiers_helios"][:18])

                    # CodeResident - Numérique (3)
                    ligne[97] = ConvertToTexte("0")

                    # TypeTiersPES - Numérique (2)
                    ligne[98] = ConvertToTexte("01")

                    # TitreASAP - O/N
                    ligne[108] = ConvertToTexte("O")

                    # TIP ASAP - O/N
                    ligne[109] = ConvertToTexte("N")

                    # NumeroFacture - Texte (50)
                    ligne[111] = ConvertToTexte(piece["num_dette"])

                    # EditionASAP - Numérique (2)
                    ligne[112] = ConvertToTexte(dict_donnees["edition_asap"])

                    # DateEnvoiASAP - Texte (10)
                    ligne[113] = ConvertToTexte(dict_donnees["date_envoi"].replace("-", ""))

                    # Formatage de la ligne
                    texte_ligne = ['""' for x in range(0, 123)]
                    for index, valeur in ligne.items():
                        texte_ligne[index-1] = valeur
                    lignes.append(";".join(texte_ligne))

                    # Incrémente sous-ligne
                    num_sous_ligne += 1


                # Création de la ligne de détail
                if self.ctrl_parametres.GetPropertyValue("inclure_detail") == True:
                    detail = dict_donnees["detail"].get(piece["IDfacture"], None)
                    if detail:
                        for index, dict_detail in enumerate(detail, start=1):
                            ligne_detail = {}

                            # Version - Numérique (3)
                            ligne_detail[1] = ConvertToTexte("18")

                            # RefIdEcriture - Texte (50)
                            ligne_detail[2] = ligne[1]

                            # DateDebut - Date
                            ligne_detail[3] = ConvertToTexte(UTILS_Dates.DateEngFr(dict_donnees["date_min"]))

                            # DateFin - Date
                            ligne_detail[4] = ConvertToTexte(UTILS_Dates.DateEngFr(dict_donnees["date_max"]))

                            # Libelle - Texte (200)
                            ligne_detail[5] = ConvertToTexte(dict_detail["libelle"][:200])

                            # Quantite - Numérique (5)
                            ligne_detail[6] = str(dict_detail["quantite"])

                            # MtUnitaire - Monétaire
                            ligne_detail[10] = str(dict_detail["montant"])

                            # MtHTaxe - Monétaire
                            ligne_detail[13] = str(dict_detail["montant"] * dict_detail["quantite"])

                            # MtTTC - Monétaire
                            ligne_detail[16] = str(dict_detail["montant"] * dict_detail["quantite"])

                            # Ordre - Numérique (3)
                            ligne_detail[17] = str(index)

                            # Formatage de la ligne de détail
                            texte_ligne_detail = ['""' for x in range(0, 17)]
                            for index, valeur in ligne_detail.items():
                                texte_ligne_detail[index-1] = valeur
                            lignes_detail.append(";".join(texte_ligne_detail))

            # Création de la pièce jointe
            ligne_pj = {}
            pj = dict_donnees["pieces_jointes"].get(piece["IDfacture"], None)
            if pj:

                # RefIdEcriture - Texte (50)
                ligne_pj[1] = ligne[1]

                # NomPJ - Texte (100)
                ligne_pj[2] = ConvertToTexte(pj["NomPJ"][:100])

                # DescriptionPJ - Texte (255)
                ligne_pj[3] = ConvertToTexte(piece["objet_piece"][:255])

                # TypPJPES - Texte (3)
                ligne_pj[4] = ConvertToTexte(dict_donnees["type_pj"])

                # TypDoc - Texte (2)
                ligne_pj[6] = ConvertToTexte("02")

                # TypFichier - Texte (2)
                ligne_pj[7] = ConvertToTexte("06")

                # Version - Numérique (3)
                ligne_pj[8] = ConvertToTexte("18")

                # Formatage de la ligne PJ
                texte_ligne_pj = ['""' for x in range(0, 8)]
                for index, valeur in ligne_pj.items():
                    texte_ligne_pj[index-1] = valeur
                lignes_pj.append(";".join(texte_ligne_pj))


        # Enregistrement du fichier ECRITURES
        if lignes:
            contenu_lignes = u"\n".join(lignes)
            with open(os.path.join(repertoire, "WTAMC001.txt"), 'w') as fichier:
                if six.PY2:
                    contenu_lignes = contenu_lignes.encode("utf8")
                fichier.write(contenu_lignes)

        # Enregistrement du fichier ECRITURES_ASAP (Détail)
        if lignes_detail:
            contenu_lignes_detail = u"\n".join(lignes_detail)
            with open(os.path.join(repertoire, "WTAMC001AS.txt"), 'w') as fichier:
                if six.PY2:
                    contenu_lignes_detail = contenu_lignes_detail.encode("utf8")
                fichier.write(contenu_lignes_detail)

        # Enregistrement du fichier ECRITURES_PJ
        if lignes_pj:
            contenu_lignes_pj = u"\n".join(lignes_pj)
            with open(os.path.join(repertoire, "WTAMC001PJ.txt"), 'w') as fichier:
                if six.PY2:
                    contenu_lignes_pj = contenu_lignes_pj.encode("utf8")
                fichier.write(contenu_lignes_pj)

        return True




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDlot=3, format="magnus")
    filtres = [
        {"type": "numero_intervalle", "numero_min": 1983, "numero_max": 2051},
    ]
    dlg.Assistant(filtres=filtres, nomLot="Nom de lot exemple")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()


