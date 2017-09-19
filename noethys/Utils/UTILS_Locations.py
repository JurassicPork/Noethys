#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from UTILS_Traduction import _
import wx
import GestionDB
import traceback
import datetime
import copy
import sys
import cStringIO
from Utils import UTILS_Dates
from Utils import UTILS_Texte
from Utils import UTILS_Filtres_questionnaires

from UTILS_Decimal import FloatToDecimal as FloatToDecimal

from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
import UTILS_Titulaires
import UTILS_Questionnaires
import UTILS_Dates
from Dlg import DLG_Apercu_location
import UTILS_Conversion
import UTILS_Infos_individus
import UTILS_Divers
import UTILS_Fichiers




class Location():
    def __init__(self):
        """ R�cup�ration de toutes les donn�es de base """

        DB = GestionDB.DB()

        # R�cup�ration des infos sur l'organisme
        req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape
        FROM organisateur
        WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictOrganisme = {}
        for nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape in listeDonnees:
            self.dictOrganisme["nom"] = nom
            self.dictOrganisme["rue"] = rue
            self.dictOrganisme["cp"] = cp
            if ville != None: ville = ville.capitalize()
            self.dictOrganisme["ville"] = ville
            self.dictOrganisme["tel"] = tel
            self.dictOrganisme["fax"] = fax
            self.dictOrganisme["mail"] = mail
            self.dictOrganisme["site"] = site
            self.dictOrganisme["num_agrement"] = num_agrement
            self.dictOrganisme["num_siret"] = num_siret
            self.dictOrganisme["code_ape"] = code_ape

        DB.Close()

        # Get noms Titulaires et individus
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires()
        self.dictIndividus = UTILS_Titulaires.GetIndividus()

        # R�cup�ration des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations()

        # R�cup�ration des questionnaires
        self.Questionnaires_familles = UTILS_Questionnaires.ChampsEtReponses(type="famille")
        self.Questionnaires_locations = UTILS_Questionnaires.ChampsEtReponses(type="location")
        self.Questionnaires_produits = UTILS_Questionnaires.ChampsEtReponses(type="produit")

    def Supprime_accent(self, texte):
        liste = [(u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"a"), (u"�", u"u"), (u"�", u"o"), (u"�", u"c"), (u"�", u"i"), (u"�", u"i"), ]
        for a, b in liste:
            texte = texte.replace(a, b)
            texte = texte.replace(a.upper(), b.upper())
        return texte

    def EcritStatusbar(self, texte=u""):
        try:
            topWindow = wx.GetApp().GetTopWindow()
            topWindow.SetStatusText(texte)
        except:
            pass

    def GetDonneesImpression(self, listeLocations=[]):
        """ Impression des locations """
        dlgAttente = wx.BusyInfo(_(u"Recherche des donn�es..."), None)

        # R�cup�re les donn�es de la facture
        if len(listeLocations) == 0:
            conditions = "()"
        elif len(listeLocations) == 1:
            conditions = "(%d)" % listeLocations[0]
        else:
            conditions = str(tuple(listeLocations))

        DB = GestionDB.DB()

        # Recherche les locations
        req = """SELECT locations.IDlocation, locations.IDfamille, locations.IDproduit, 
        locations.observations, locations.date_debut, locations.date_fin,
        produits.nom,
        produits_categories.nom
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE IDlocation IN %s;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0:
            del dlgAttente
            return False

        dictDonnees = {}
        dictChampsFusion = {}
        for item in listeDonnees:

            IDlocation = item[0]
            IDfamille = item[1]
            IDproduit = item[2]
            observations = item[3]
            date_debut = item[4]
            date_fin = item[5]

            if isinstance(date_debut, str) or isinstance(date_debut, unicode):
                date_debut = datetime.datetime.strptime(date_debut, "%Y-%m-%d %H:%M:%S")
            date_debut_texte = datetime.datetime.strftime(date_debut, "%d/%m/%Y")
            heure_debut_texte = datetime.datetime.strftime(date_debut, "%Hh%M")

            if isinstance(date_fin, str) or isinstance(date_fin, unicode):
                date_fin = datetime.datetime.strptime(date_fin, "%Y-%m-%d %H:%M:%S")
                date_fin_texte = datetime.datetime.strftime(date_fin, "%d/%m/%Y")
                heure_fin_texte = datetime.datetime.strftime(date_fin, "%Hh%M")
            if date_fin == None :
                date_fin_texte = ""
                heure_fin_texte = ""

            nomProduit = item[6]
            nomCategorie = item[7]

            # if IDindividu != None and self.dictIndividus.has_key(IDindividu):
            #     beneficiaires = self.dictIndividus[IDindividu]["nom_complet"]
            #     rue = self.dictIndividus[IDindividu]["rue"]
            #     cp = self.dictIndividus[IDindividu]["cp"]
            #     ville = self.dictIndividus[IDindividu]["ville"]

            # Famille
            if IDfamille != None:
                nomTitulaires = self.dictTitulaires[IDfamille]["titulairesAvecCivilite"]
                famille_rue = self.dictTitulaires[IDfamille]["adresse"]["rue"]
                famille_cp = self.dictTitulaires[IDfamille]["adresse"]["cp"]
                famille_ville = self.dictTitulaires[IDfamille]["adresse"]["ville"]
            else:
                nomTitulaires = "Famille inconnue"
                famille_rue = ""
                famille_cp = ""
                famille_ville = ""

            # Facturation
            # montant = 0.0
            # ventilation = 0.0
            # dateReglement = None
            # modeReglement = None
            #
            # if dictFacturation.has_key(IDcotisation):
            #     montant = dictFacturation[IDcotisation]["montant"]
            #     ventilation = dictFacturation[IDcotisation]["ventilation"]
            #     dateReglement = dictFacturation[IDcotisation]["dateReglement"]
            #     modeReglement = dictFacturation[IDcotisation]["modeReglement"]
            #
            # solde = float(FloatToDecimal(montant) - FloatToDecimal(ventilation))
            #
            # montantStr = u"%.02f %s" % (montant, SYMBOLE)
            # regleStr = u"%.02f %s" % (ventilation, SYMBOLE)
            # soldeStr = u"%.02f %s" % (solde, SYMBOLE)
            # montantStrLettres = UTILS_Conversion.trad(montant, MONNAIE_SINGULIER, MONNAIE_DIVISION)
            # regleStrLettres = UTILS_Conversion.trad(ventilation, MONNAIE_SINGULIER, MONNAIE_DIVISION)
            # soldeStrLettres = UTILS_Conversion.trad(solde, MONNAIE_SINGULIER, MONNAIE_DIVISION)


            # M�morisation des donn�es
            dictDonnee = {
                "select": True,
                "{IDLOCATION}": str(IDlocation),
                "{IDPRODUIT}": str(IDproduit),
                "{DATE_DEBUT}": date_debut_texte,
                "{DATE_FIN}": date_fin_texte,
                "{HEURE_DEBUT}": heure_debut_texte,
                "{HEURE_FIN}": heure_fin_texte,
                "{NOM_PRODUIT}": nomProduit,
                "{NOM_CATEGORIE}": nomCategorie,
                "{NOTES}": observations,
                "{IDFAMILLE}": str(IDfamille),
                "{FAMILLE_NOM}": nomTitulaires,
                "{FAMILLE_RUE}": famille_rue,
                "{FAMILLE_CP}": famille_cp,
                "{FAMILLE_VILLE}": famille_ville,

                # "{MONTANT_FACTURE}": montantStr,
                # "{MONTANT_REGLE}": regleStr,
                # "{SOLDE_ACTUEL}": soldeStr,
                # "{MONTANT_FACTURE_LETTRES}": montantStrLettres.capitalize(),
                # "{MONTANT_REGLE_LETTRES}": regleStrLettres.capitalize(),
                # "{SOLDE_ACTUEL_LETTRES}": soldeStrLettres.capitalize(),
                # "{DATE_REGLEMENT}": UTILS_Dates.DateDDEnFr(dateReglement),

                "{ORGANISATEUR_NOM}": self.dictOrganisme["nom"],
                "{ORGANISATEUR_RUE}": self.dictOrganisme["rue"],
                "{ORGANISATEUR_CP}": self.dictOrganisme["cp"],
                "{ORGANISATEUR_VILLE}": self.dictOrganisme["ville"],
                "{ORGANISATEUR_TEL}": self.dictOrganisme["tel"],
                "{ORGANISATEUR_FAX}": self.dictOrganisme["fax"],
                "{ORGANISATEUR_MAIL}": self.dictOrganisme["mail"],
                "{ORGANISATEUR_SITE}": self.dictOrganisme["site"],
                "{ORGANISATEUR_AGREMENT}": self.dictOrganisme["num_agrement"],
                "{ORGANISATEUR_SIRET}": self.dictOrganisme["num_siret"],
                "{ORGANISATEUR_APE}": self.dictOrganisme["code_ape"],

                "{DATE_EDITION_COURT}": UTILS_Dates.DateDDEnFr(datetime.date.today()),
                "{DATE_EDITION_LONG}": UTILS_Dates.DateComplete(datetime.date.today()),
            }

            # Ajoute les informations de base individus et familles
            # if IDindividu != None:
            #     dictDonnee.update(self.infosIndividus.GetDictValeurs(mode="individu", ID=IDindividu, formatChamp=True))
            if IDfamille != None:
                dictDonnee.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))

            # Ajoute les r�ponses des questionnaires
            for dictReponse in self.Questionnaires_familles.GetDonnees(IDfamille):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            for dictReponse in self.Questionnaires_locations.GetDonnees(IDlocation):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            for dictReponse in self.Questionnaires_produits.GetDonnees(IDproduit):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            dictDonnees[IDlocation] = dictDonnee

            # Champs de fusion pour Email
            dictChampsFusion[IDlocation] = {}
            for key, valeur in dictDonnee.iteritems():
                if key[0] == "{":
                    dictChampsFusion[IDlocation][key] = valeur

        del dlgAttente
        return dictDonnees, dictChampsFusion

    def Impression(self, listeLocations=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des locations """
        import UTILS_Impression_location

        # R�cup�ration des donn�es � partir des IDlocation
        resultat = self.GetDonneesImpression(listeLocations)
        if resultat == False:
            return False
        dictLocations, dictChampsFusion = resultat

        # R�cup�ration des param�tres d'affichage
        if dictOptions == None:
            if afficherDoc == False:
                dlg = DLG_Apercu_location.Dialog(None, titre=_(u"S�lection des param�tres de la location"), intro=_(u"S�lectionnez ici les param�tres d'affichage de la location."))
                dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
            else:
                dlg = DLG_Apercu_location.Dialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                dictOptions = dlg.GetParametres()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False

        # Cr�ation des PDF � l'unit�
        def CreationPDFunique(repertoireCible=""):
            dictPieces = {}
            dlgAttente = wx.BusyInfo(_(u"G�n�ration des PDF � l'unit� en cours..."), None)
            try:
                index = 0
                for IDlocation, dictLocation in dictLocations.iteritems():
                    if dictLocation["select"] == True:
                        nomTitulaires = self.Supprime_accent(dictLocation["{FAMILLE_NOM}"])
                        nomFichier = _(u"Location %d - %s") % (IDlocation, nomTitulaires)
                        cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                        dictComptesTemp = {IDlocation: dictLocation}
                        self.EcritStatusbar(_(u"Edition de la location %d/%d : %s") % (index, len(dictLocation), nomFichier))
                        UTILS_Impression_location.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                        dictPieces[IDlocation] = cheminFichier
                        index += 1
                self.EcritStatusbar("")
                del dlgAttente
                return dictPieces
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"D�sol�, le probl�me suivant a �t� rencontr� dans l'�dition des locations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # R�pertoire souhait� par l'utilisateur
        if repertoire != None:
            resultat = CreationPDFunique(repertoire)
            if resultat == False:
                return False

        # R�pertoire TEMP (pour Emails)
        dictPieces = {}
        if repertoireTemp == True:
            dictPieces = CreationPDFunique(UTILS_Fichiers.GetRepTemp())
            if dictPieces == False:
                return False

        # Sauvegarde dans un porte-documents
        if dictOptions["questionnaire"] != None :
            # Cr�ation des PDF
            if len(dictPieces) == 0 :
                dictPieces = CreationPDFunique(UTILS_Fichiers.GetRepTemp())

            # Recherche des IDreponse
            IDquestion = dictOptions["questionnaire"]
            DB = GestionDB.DB()
            req = """SELECT IDreponse, IDdonnee
            FROM questionnaire_reponses
            WHERE IDquestion=%d
            ;""" % IDquestion
            DB.ExecuterReq(req)
            listeReponses = DB.ResultatReq()
            DB.Close()
            dictReponses = {}
            for IDreponse, IDlocation in listeReponses :
                dictReponses[IDlocation] = IDreponse

            DB = GestionDB.DB(suffixe="DOCUMENTS")
            for IDlocation, cheminFichier in dictPieces.iteritems():
                # Pr�paration du blob
                fichier = open(cheminFichier, "rb")
                data = fichier.read()
                fichier.close()
                buffer = cStringIO.StringIO(data)
                blob = buffer.read()
                # Recherche l'IDreponse
                if dictReponses.has_key(IDlocation):
                    IDreponse = dictReponses[IDlocation]
                else :
                    # Cr�ation d'une r�ponse de questionnaire
                    listeDonnees = [
                        ("IDquestion", IDquestion),
                        ("reponse", "##DOCUMENTS##"),
                        ("type", "location"),
                        ("IDdonnee", IDlocation),
                        ]
                    DB2 = GestionDB.DB()
                    IDreponse = DB2.ReqInsert("questionnaire_reponses", listeDonnees)
                    DB2.Close()
                # Sauvegarde du document
                listeDonnees = [("IDreponse", IDreponse), ("type", "pdf"), ("label", dictOptions["nomModele"]), ("last_update", datetime.datetime.now())]
                IDdocument = DB.ReqInsert("documents", listeDonnees)
                DB.MAJimage(table="documents", key="IDdocument", IDkey=IDdocument, blobImage=blob, nomChampBlob="document")
            DB.Close()

        # Fabrication du PDF global
        if repertoireTemp == False:
            dlgAttente = wx.BusyInfo(_(u"Cr�ation du PDF en cours..."), None)
            self.EcritStatusbar(_(u"Cr�ation du PDF des locations en cours... veuillez patienter..."))
            try:
                UTILS_Impression_location.Impression(dictLocations, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, u"D�sol�, le probl�me suivant a �t� rencontr� dans l'�dition des locations : \n\n%s" % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces







# -------------------------------------------------------------------------------------------------------------------------------------------

def GetProduitsLoues(DB=None, date_reference=datetime.datetime.now()):
    """ Recherche les produits lou�s � la date de r�f�rence """
    if DB == None:
        DBT = GestionDB.DB()
    else:
        DBT = DB

    # Recherche les locations � la date de r�f�rence
    req = """SELECT IDlocation, IDproduit, IDfamille, date_debut, date_fin
    FROM locations
    WHERE date_debut<='%s' AND (date_fin IS NULL OR date_fin>='%s')
    ;""" % (date_reference, date_reference)
    DBT.ExecuterReq(req)
    listeLocations = DBT.ResultatReq()
    dictLocations = {}
    for IDlocation, IDproduit, IDfamille, date_debut, date_fin in listeLocations:
        date_debut = UTILS_Dates.DateEngEnDateDDT(date_debut)
        date_fin = UTILS_Dates.DateEngEnDateDDT(date_fin)
        if dictLocations.has_key(IDproduit) == False:
            dictLocations[IDproduit] = []
            dictLocations[IDproduit] = {"IDlocation": IDlocation, "IDfamille": IDfamille, "date_debut": date_debut, "date_fin": date_fin}

    if DB == None:
        DBT.Close()

    return dictLocations



def GetPropositionsLocations(dictFiltresSelection={}, dictDemandeSelection=None, uniquement_disponibles=True):
    DB = GestionDB.DB()

    # Importation des questionnaires des produits
    req = """SELECT IDreponse, IDquestion, reponse, IDdonnee
    FROM questionnaire_reponses
    WHERE type='produit';"""
    DB.ExecuterReq(req)
    listeReponses = DB.ResultatReq()
    dictReponses = {}
    for IDreponse, IDquestion, reponse, IDproduit in listeReponses :
        dictTemp = {"IDreponse" : IDreponse, "IDquestion" : IDquestion, "reponse" : reponse}
        if dictReponses.has_key(IDproduit) == False :
            dictReponses[IDproduit] = []
        dictReponses[IDproduit].append(dictTemp)

    # Recherche les produits non disponibles
    dictLocations = GetProduitsLoues(DB=DB)

    # Importation des produits
    req = """SELECT IDproduit, IDcategorie, nom
    FROM produits;"""
    DB.ExecuterReq(req)
    listeProduitsTemp = DB.ResultatReq()
    listeProduits = []
    for IDproduit, IDcategorie, nom in listeProduitsTemp :

        # Recherche les r�ponses au questionnaire du produit
        if dictReponses.has_key(IDproduit) :
            reponses = dictReponses[IDproduit]
        else :
            reponses = []

        # Recherche les locations en cours du produit
        if dictLocations.has_key(IDproduit):
            disponible = False
        else :
            disponible = True

        if uniquement_disponibles == False or disponible == True :
            dictTemp = {"IDproduit" : IDproduit, "IDcategorie" : IDcategorie, "disponible" : disponible, "nom" : nom, "reponses" : reponses}
            listeProduits.append(dictTemp)

    # Recherche les filtres de questionnaires
    req = """SELECT IDfiltre, questionnaire_filtres.IDquestion, choix, criteres, IDdonnee, 
    questionnaire_categories.type, controle
    FROM questionnaire_filtres
    LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_filtres.IDquestion
    LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
    WHERE categorie='location_demande';"""
    DB.ExecuterReq(req)
    listeFiltres = DB.ResultatReq()
    dictFiltres = {}
    for IDfiltre, IDquestion, choix, criteres, IDdemande, type, controle in listeFiltres :
        if dictFiltres.has_key(IDdemande) == False :
            dictFiltres[IDdemande] = []
        dictFiltres[IDdemande].append({"IDfiltre":IDfiltre, "IDquestion":IDquestion, "choix":choix, "criteres":criteres, "type":type, "controle":controle})

    # Ajoute ou remplace avec le dictDemandeSelection
    if dictFiltresSelection != None :
        for IDdemande, listeFiltres in dictFiltresSelection.iteritems() :
            dictFiltres[IDdemande] = listeFiltres


    # Importation des demandes de locations
    # if dictDemande == None :
    #     req = """SELECT IDdemande, date, IDfamille, categories, produits
    #     FROM locations_demandes
    #     WHERE statut='attente'
    #     ORDER BY IDdemande;"""
    #     DB.ExecuterReq(req)
    #     listeDemandes = DB.ResultatReq()
    # else :
    #     listeDemandes = [dictDemande,]

    req = """SELECT IDdemande, date, IDfamille, categories, produits
    FROM locations_demandes
    WHERE statut='attente' 
    ORDER BY IDdemande;"""
    DB.ExecuterReq(req)
    listeDemandes = DB.ResultatReq()

    if dictDemandeSelection != None and dictDemandeSelection["IDdemande"] == None :
        listeDemandes.append(dictDemandeSelection)

    DB.Close()

    # Parcours les demandes
    dictPropositions = {}
    dictPositions = {}
    for demande in listeDemandes :

        # Met les donn�es dans un dict
        if not isinstance(demande, dict) :
            categories = UTILS_Texte.ConvertStrToListe(demande[3], siVide=[])
            produits = UTILS_Texte.ConvertStrToListe(demande[4], siVide=[])
            dictDemandeTemp = {"IDdemande" : demande[0], "date" : demande[1], "IDfamille" : demande[2], "categories" : categories, "produits": produits}
        else :
            dictDemandeTemp = demande

        if dictDemandeSelection != None and dictDemandeSelection["IDdemande"] == dictDemandeTemp["IDdemande"]:
            dictDemandeTemp = dictDemandeSelection

        IDdemande = dictDemandeTemp["IDdemande"]

        # Parcours les produits
        for dictProduit in listeProduits :
            valide = True

            # V�rifie si le produit est dans la liste des cat�gories souhait�es
            if dictDemandeTemp["categories"] != [] and dictProduit["IDcategorie"] not in dictDemandeTemp["categories"] :
                valide = False

            # V�rifie si le produit est dans la liste des produits souhait�s
            if dictDemandeTemp["produits"] != [] and dictProduit["IDproduit"] not in dictDemandeTemp["produits"] :
                valide = False

            # V�rifie si le produit r�pond aux filtres de la demande
            if dictFiltres.has_key(IDdemande):
                for dictFiltre in dictFiltres[IDdemande]:
                    for dictReponse in dictProduit["reponses"]:
                        resultat = UTILS_Filtres_questionnaires.Filtre(controle=dictFiltre["controle"], choix=dictFiltre["choix"], criteres=dictFiltre["criteres"], reponse=dictReponse["reponse"])
                        if resultat == False:
                            valide = False

            # M�morisation de la proposition
            if valide == True :

                # Position dans la liste du produit
                if dictPositions.has_key(dictProduit["IDproduit"]) == False :
                    dictPositions[dictProduit["IDproduit"]] = 0
                dictPositions[dictProduit["IDproduit"]] += 1
                position = dictPositions[dictProduit["IDproduit"]]

                # Proposition
                dictProduit = copy.deepcopy(dictProduit)
                if dictPropositions.has_key(IDdemande) == False :
                    dictPropositions[IDdemande] = []
                dictProduit["position"] = position
                dictPropositions[IDdemande].append(dictProduit)

    return dictPropositions

def GetMeilleurePosition(dictPropositions={}, IDdemande=None):
    position = None
    if dictPropositions.has_key(IDdemande):
        for dictProduit in dictPropositions[IDdemande] :
            if position == None or dictProduit["position"] < position :
                position = dictProduit["position"]
    return position



if __name__=='__main__':
    print len(GetPropositionsLocations(uniquement_disponibles=False))