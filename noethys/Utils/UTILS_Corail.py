#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-21 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
from xml.dom.minidom import Document


def GetXML(dictDonnees={}):
    """ G�n�ration du fichier d'import Corail """
    doc = Document()

    # G�n�ration du document XML
    racine = doc.createElement("ImportCosoluce")
    doc.appendChild(racine)

    # Information
    Information = doc.createElement("Information")
    racine.appendChild(Information)

    # Nom de la collectivit�
    NomCollectivite = doc.createElement("NomCollectivite")
    NomCollectivite.setAttribute("V", dictDonnees["nom_collectivite"])
    Information.appendChild(NomCollectivite)

    # Exercice
    Exercice = doc.createElement("Exercice")
    Exercice.setAttribute("V", dictDonnees["exercice"][:4])
    Information.appendChild(Exercice)

    # Origine
    Origine = doc.createElement("Origine")
    Origine.setAttribute("V", "Noethys")
    Information.appendChild(Origine)

    # DateFichier
    DateFichier = doc.createElement("DateFichier")
    DateFichier.setAttribute("V", dictDonnees["date_emission"])
    Information.appendChild(DateFichier)

    # InfoComplementaire
    InfoComplementaire = doc.createElement("InfoComplementaire")
    InfoComplementaire.setAttribute("V", dictDonnees["objet_dette"])
    Information.appendChild(InfoComplementaire)

    # TypePieceImport
    TypePieceImport = doc.createElement("TypePieceImport")
    racine.appendChild(TypePieceImport)

    # TypePiece
    TypePiece = doc.createElement("TypePiece")
    TypePiece.setAttribute("V", u"Pi�ce EnCours")
    TypePieceImport.appendChild(TypePiece)

    # Sens
    Sens = doc.createElement("Sens")
    Sens.setAttribute("V", "R")
    TypePieceImport.appendChild(Sens)

    for dictPiece in dictDonnees["pieces"]:

        # Piece
        Piece = doc.createElement("Piece")
        TypePieceImport.appendChild(Piece)

        # InfoPiece
        InfoPiece = doc.createElement("InfoPiece")
        Piece.appendChild(InfoPiece)

        # TypeSerieBordereau
        TypeSerieBordereau = doc.createElement("TypeSerieBordereau")
        TypeSerieBordereau.setAttribute("V", "N")
        InfoPiece.appendChild(TypeSerieBordereau)

        # TypeEcriture
        TypeEcriture = doc.createElement("TypeEcriture")
        TypeEcriture.setAttribute("V", "R")
        InfoPiece.appendChild(TypeEcriture)

        # TrainPiece
        TrainPiece = doc.createElement("TrainPiece")
        TrainPiece.setAttribute("V", "Facturation")
        InfoPiece.appendChild(TrainPiece)

        # Tiers
        Tiers = doc.createElement("Tiers")
        InfoPiece.appendChild(Tiers)

        # InfoTiers
        InfoTiers = doc.createElement("InfoTiers")
        Tiers.appendChild(InfoTiers)

        # CatTiers
        CatTiers = doc.createElement("CatTiers")
        CatTiers.setAttribute("V", dictPiece["cattiers_helios"])
        InfoTiers.appendChild(CatTiers)

        # NatJur
        NatJur = doc.createElement("NatJur")
        NatJur.setAttribute("V", dictPiece["natjur_helios"])
        InfoTiers.appendChild(NatJur)

        # TypeTiers
        TypeTiers = doc.createElement("TypeTiers")
        TypeTiers.setAttribute("V", "01")
        InfoTiers.appendChild(TypeTiers)

        # Civilit�
        civilite = dictPiece["titulaire_civilite"]
        if civilite == "M.": civilite = "Mr"
        if civilite == "Melle": civilite = "Mme"
        if civilite not in (None, ""):
            Civilite = doc.createElement("Civilite")
            Civilite.setAttribute("V", civilite[:10])
            InfoTiers.appendChild(Civilite)

        # RaisonSociale
        RaisonSociale = doc.createElement("RaisonSociale")
        if dictPiece["titulaire_prenom"]:
            temp = dictPiece["titulaire_nom"][:38] + " " + dictPiece["titulaire_prenom"]
        else:
            temp = dictPiece["titulaire_nom"][:38]
        RaisonSociale.setAttribute("V", temp)
        InfoTiers.appendChild(RaisonSociale)

        # Nom
        Nom = doc.createElement("Nom")
        Nom.setAttribute("V", dictPiece["titulaire_nom"][:38])
        InfoTiers.appendChild(Nom)

        # Prenom
        prenom = dictPiece["titulaire_prenom"]
        if prenom not in (None, ""):
            Prenom = doc.createElement("Prenom")
            Prenom.setAttribute("V", prenom[:38])
            InfoTiers.appendChild(Prenom)

        # Adresse
        Adresse = doc.createElement("Adresse")
        Tiers.appendChild(Adresse)

        # AdresseEtranger
        AdresseEtranger = doc.createElement("AdresseEtranger")
        AdresseEtranger.setAttribute("V", "N")
        Adresse.appendChild(AdresseEtranger)

        # Rue
        Rue = doc.createElement("Rue")
        Rue.setAttribute("V", dictPiece["titulaire_rue"][:38])
        Adresse.appendChild(Rue)

        # CP
        CP = doc.createElement("CP")
        CP.setAttribute("V", dictPiece["titulaire_cp"][:5])
        Adresse.appendChild(CP)

        # Ville
        Ville = doc.createElement("Ville")
        Ville.setAttribute("V", dictPiece["titulaire_ville"][:38])
        Adresse.appendChild(Ville)

        if dictPiece["prelevement"] == 1:

            # RefBancaire
            RefBancaire = doc.createElement("RefBancaire")
            InfoPiece.appendChild(RefBancaire)

            # Titulaire
            Titulaire = doc.createElement("Titulaire")
            Titulaire.setAttribute("V", dictPiece["prelevement_titulaire"][:32])
            RefBancaire.appendChild(Titulaire)

            # IBAN
            IBAN = doc.createElement("IBAN")
            IBAN.setAttribute("V", dictPiece["prelevement_iban"])
            RefBancaire.appendChild(IBAN)

            # BIC
            BIC = doc.createElement("BIC")
            BIC.setAttribute("V", dictPiece["prelevement_bic"])
            RefBancaire.appendChild(BIC)

        # DatePiece
        DatePiece = doc.createElement("DatePiece")
        DatePiece.setAttribute("V", dictDonnees["date_emission"])
        InfoPiece.appendChild(DatePiece)

        # Objet
        Objet = doc.createElement("Objet")
        Objet.setAttribute("V", dictPiece["objet_piece"][:160])
        InfoPiece.appendChild(Objet)

        # TypePiecePES
        TypePiecePES = doc.createElement("TypePiecePES")
        TypePiecePES.setAttribute("V", "01")
        InfoPiece.appendChild(TypePiecePES)

        # NaturePiecePES
        NaturePiecePES = doc.createElement("NaturePiecePES")
        NaturePiecePES.setAttribute("V", "01")
        InfoPiece.appendChild(NaturePiecePES)

        # PesASAP
        PesASAP = doc.createElement("PesASAP")
        PesASAP.setAttribute("V", "02")
        InfoPiece.appendChild(PesASAP)

        # ASAPEnteteFacturation
        ASAPEnteteFacturation = doc.createElement("ASAPEnteteFacturation")
        InfoPiece.appendChild(ASAPEnteteFacturation)

        # ASAPObjet
        ASAPObjet = doc.createElement("ASAPObjet")
        ASAPObjet.setAttribute("V", dictDonnees["objet_dette"])
        ASAPEnteteFacturation.appendChild(ASAPObjet)

        # ASAPDateDebut
        ASAPDateDebut = doc.createElement("ASAPDateDebut")
        ASAPDateDebut.setAttribute("V", dictDonnees["date_min"].strftime("%Y%m%d"))
        ASAPEnteteFacturation.appendChild(ASAPDateDebut)

        # ASAPDateFin
        ASAPDateFin = doc.createElement("ASAPDateFin")
        ASAPDateFin.setAttribute("V", dictDonnees["date_max"].strftime("%Y%m%d"))
        ASAPEnteteFacturation.appendChild(ASAPDateFin)

        if dictDonnees["pieces_jointes"] != False and len(dictDonnees["pieces_jointes"]) > 0 :

            pj = dictDonnees["pieces_jointes"].get(dictPiece["IDfacture"], None)

            # PJ
            PJ = doc.createElement("PJ")
            Piece.appendChild(PJ)

            # NomPJ
            NomPJ = doc.createElement("NomPJ")
            NomPJ.setAttribute("V", pj["NomPJ"])
            PJ.appendChild(NomPJ)

            # IDPJInterne
            IDPJInterne = doc.createElement("IDPJInterne")
            IDPJInterne.setAttribute("V", pj["IdUnique"])
            PJ.appendChild(IDPJInterne)

            # CheminRelatif
            CheminRelatif = doc.createElement("CheminRelatif")
            CheminRelatif.setAttribute("V", "PJ\\")
            PJ.appendChild(CheminRelatif)

            # TransmettreAHelios
            TransmettreAHelios = doc.createElement("TransmettreAHelios")
            TransmettreAHelios.setAttribute("V", "O")
            PJ.appendChild(TransmettreAHelios)

        if dictPiece["prelevement"] == 1:

            # Prelevement
            Prelevement = doc.createElement("Prelevement")
            Piece.appendChild(Prelevement)

            # NaturePrelevement
            NaturePrelevement = doc.createElement("NaturePrelevement")
            NaturePrelevement.setAttribute("V", "01")
            Prelevement.appendChild(NaturePrelevement)

            # PeriodicitePrelevement
            PeriodicitePrelevement = doc.createElement("PeriodicitePrelevement")
            PeriodicitePrelevement.setAttribute("V", "07")
            Prelevement.appendChild(PeriodicitePrelevement)

            # DatePrelevement
            DatePrelevement = doc.createElement("DatePrelevement")
            DatePrelevement.setAttribute("V", dictDonnees["date_prelevement"])
            Prelevement.appendChild(DatePrelevement)

            # SequencePrelevement
            if dictPiece["sequence"] == "FRST": sequence = "02"
            elif dictPiece["sequence"] == "RCUR": sequence = "03"
            elif dictPiece["sequence"] == "FNAL": sequence = "04"
            else: sequence = "01"
            SequencePrelevement = doc.createElement("SequencePres")
            SequencePrelevement.setAttribute("V", sequence)
            Prelevement.appendChild(SequencePrelevement)

            # RUM
            RUM = doc.createElement("RUM")
            RUM.setAttribute("V", dictPiece["prelevement_rum"])
            Prelevement.appendChild(RUM)

            # RUM
            DateRUM = doc.createElement("DateRUM")
            DateRUM.setAttribute("V", dictPiece["prelevement_date_mandat"])
            Prelevement.appendChild(DateRUM)

            # LibPrelevement
            LibPrelevement = doc.createElement("LibPrelevement")
            LibPrelevement.setAttribute("V", dictPiece["prelevement_libelle"][:140])
            Prelevement.appendChild(LibPrelevement)

        # LignePiece
        LignePiece = doc.createElement("LignePiece")
        Piece.appendChild(LignePiece)

        # Article
        Article = doc.createElement("Article")
        Article.setAttribute("V", dictDonnees["id_poste"][:10])
        LignePiece.appendChild(Article)

        # Fonction
        Fonction = doc.createElement("Fonction")
        Fonction.setAttribute("V", dictDonnees["fonction"])
        LignePiece.appendChild(Fonction)

        # CodeAnalytique1
        if dictDonnees["code_analytique_1"]:
            CodeAnalytique1 = doc.createElement("CodeAnalytique1")
            CodeAnalytique1.setAttribute("V", dictDonnees["code_analytique_1"])
            LignePiece.appendChild(CodeAnalytique1)

        # CodeAnalytique2
        if dictDonnees["code_analytique_2"]:
            CodeAnalytique2 = doc.createElement("CodeAnalytique2")
            CodeAnalytique2.setAttribute("V", dictDonnees["code_analytique_2"])
            LignePiece.appendChild(CodeAnalytique2)

        # MontantHT
        MontantHT = doc.createElement("MontantHT")
        MontantHT.setAttribute("V", dictPiece["montant"])
        LignePiece.appendChild(MontantHT)

        # CodeProduit
        CodeProduit = doc.createElement("CodeProduit")
        CodeProduit.setAttribute("V", dictDonnees["code_prodloc"][:4])
        LignePiece.appendChild(CodeProduit)

        if dictDonnees["inclure_detail"] == True:
            detail = dictDonnees["detail"].get(dictPiece["IDfacture"], None)
            if detail:
                for index, dict_detail in enumerate(detail, start=1):

                    # ASAPLigneFacturation
                    ASAPLigneFacturation = doc.createElement("ASAPLigneFacturation")
                    Piece.appendChild(ASAPLigneFacturation)

                    # ASAPLibelleLigne
                    ASAPLibelleLigne = doc.createElement("ASAPLibelleLigne")
                    ASAPLibelleLigne.setAttribute("V", dict_detail["libelle"][:200])
                    ASAPLigneFacturation.appendChild(ASAPLibelleLigne)

                    # ASAPUnite
                    ASAPUnite = doc.createElement("ASAPUnite")
                    ASAPUnite.setAttribute("V", "")
                    ASAPLigneFacturation.appendChild(ASAPUnite)

                    # ASAPQuantite
                    ASAPQuantite = doc.createElement("ASAPQuantite")
                    ASAPQuantite.setAttribute("V", str(dict_detail["quantite"]))
                    ASAPLigneFacturation.appendChild(ASAPQuantite)

                    # ASAPPrixUnitaire
                    ASAPPrixUnitaire = doc.createElement("ASAPPrixUnitaire")
                    ASAPPrixUnitaire.setAttribute("V", str(dict_detail["montant"]))
                    ASAPLigneFacturation.appendChild(ASAPPrixUnitaire)

                    # ASAPMontantHT
                    ASAPMontantHT = doc.createElement("ASAPMontantHT")
                    ASAPMontantHT.setAttribute("V", str(dict_detail["montant"] * dict_detail["quantite"]))
                    ASAPLigneFacturation.appendChild(ASAPMontantHT)

                    # ASAPTauxTVA
                    ASAPTauxTVA = doc.createElement("ASAPTauxTVA")
                    ASAPTauxTVA.setAttribute("V", "0.00")
                    ASAPLigneFacturation.appendChild(ASAPTauxTVA)

                    # ASAPMontantTVA
                    ASAPMontantTVA = doc.createElement("ASAPMontantTVA")
                    ASAPMontantTVA.setAttribute("V", "0.00")
                    ASAPLigneFacturation.appendChild(ASAPMontantTVA)

    return doc


def EnregistrerXML(doc=None, nomFichier=""):
    """ Enregistre le fichier XML """
    f = open(nomFichier, "w")
    try:
        f.write(doc.toprettyxml(indent="  ", encoding="UTF-8"))
    finally:
        f.close()
