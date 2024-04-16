from flask import Flask, jsonify, render_template, request ,redirect, url_for
from flask_bootstrap import Bootstrap
from dataclasses import dataclass, field
from typing import List
from openai import OpenAI
from dataclasses import dataclass, field
from typing import List
import os
import re
import ast
import textwrap
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import utils
from reportlab.pdfgen import canvas
from flask import send_file
from flask import request
from werkzeug.utils import secure_filename
#commentaire de julien
import time

app = Flask(__name__)
bootstrap = Bootstrap(app)

@dataclass
class Erreur:
    typeErreur: str
    descriptionErreur: str
    supprimer : False

@dataclass
class Phrase:
    contenu: str
    fautes: List[Erreur] = field(default_factory=list)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle the form submission here
        # For example, redirect to another page or perform some action
        return redirect(url_for('index'))  # Replace 'index' with the appropriate route
    else:
        # Handle GET request (display the form)
        return render_template('index.html')
    
## --------------------------------------------------------------- ##
## -----------------  FONCTIONS LIEES AU BACKEND ----------------- ##
## --------------------------------------------------------------- ##


##  ----- Variables globales
client = OpenAI(
    # This is the default and can be omitted
    api_key='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',
)
typeFaute = ["Grammaticale","Orthographe","Conjugaison","Syntaxe"]


phrases_exemple = []
## Definition des structures de donnees
@dataclass
class Erreur:
    typeErreur: str
    descriptionErreur: str
def __init__(self, typeErreur, descriptionErreur):
        self.typeErreur = typeErreur
        self.descriptionErreur = descriptionErreur

@dataclass
class Phrase:
    contenu: str
    fautes: List[Erreur] = field(default_factory=list)
    nb_erreurs: int = field(init=False)

    def __post_init__(self):
        self.nb_erreurs = len(self.fautes)


##  ----- Fonctions liees a l'API OpenAI
## Jugement des fautes
convJuge = []
roleJuge = f"Ton role est de juger si une phrase contient des fautes de langue francaises (Voici les type de fautes {typeFaute}) sois plus ou moins souple sachant qu'il s'agit d'un niveau collegial. Tu reponds False si la phrase contient une ou plus de faute sinon tu repond True. "
convJuge.append({"role": "system", "content": f"{roleJuge}"})

def communicationJuge(messageF):
    reponse = ""

    # Utilisez append au lieu de push
    convJuge.append({"role": "user", "content": f"{messageF}"})

    # Appel à l'API
    chat_completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=convJuge
    )

    # Imprimez la structure complète de la réponse pour comprendre sa structure
    for choice in chat_completion.choices:
        if choice.message.role == "assistant":
            reponse += choice.message.content  # Utilisez += pour concaténer les chaînes de caractères
        
    return reponse

def juger_phrase(phrase):
    return communicationJuge(phrase)

## Detection des fautes
convDetecteur = []
roleDetecteur = f"Ton role est de detecter les fautes de langue francaises contenue dans une phrase. Tu repond seulement une liste python contenant les fautes (seulement la description de la faute) UTILISE AUCUN CARACTERE SPECIAL DANS TA REPONSE. "
convDetecteur.append({"role": "system", "content": f"{roleDetecteur}"})

def communicationDetecteur(messageF):
    reponse = ""

    # Utilisez append au lieu de push
    convDetecteur.append({"role": "user", "content": f"{messageF}"})

    # Appel à l'API
    chat_completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=convDetecteur
    )

    # Imprimez la structure complète de la réponse pour comprendre sa structure
    for choice in chat_completion.choices:
        if choice.message.role == "assistant":
            reponse += choice.message.content  # Utilisez += pour concaténer les chaînes de caractères
        
    return reponse

def detecter_phrase(phrase):
    return communicationDetecteur(phrase)

## Classification des fautes
convClasseur = []
roleClasseur = f"Ton role est de recevoir des message contenant une description de faute de francais, Tu dois juger a quel type de faute correspond le mieux la description de la faute.Reponds 1 si c'est une faute de grammaire, 2 si c'est une faute d'orthographe, 3 si c'est une faute de conjugaison. Repond seulement le chiffre correspondant"
convClasseur.append({"role": "system", "content": f"{roleClasseur}"})

def communicationClasseur(messageF):
    reponse = ""

    # Utilisez append au lieu de push
    convClasseur.append({"role": "user", "content": f"{messageF}"})

    # Appel à l'API
    chat_completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=convClasseur
    )

    # Imprimez la structure complète de la réponse pour comprendre sa structure
    for choice in chat_completion.choices:
        if choice.message.role == "assistant":
            reponse += choice.message.content  # Utilisez += pour concaténer les chaînes de caractères
        
    return reponse

def classer_phrase(phrase):
    return communicationClasseur(phrase)

## Remarques sur le texte
convConseil = []
roleConseil = f"Ton role est de donner faire des remarques pedagogiques sur le texte (fautes de syntaxes, orthographes, conjugaison et grammaire). Tu dois donner des conseils pour ameliorer le texte de niveau universitaire. Ton reponse est un court paragraphe de 2-3 phrases)"
convConseil.append({"role": "system", "content": f"{roleConseil}"})

def communicationConseil(messageF):
    reponse = ""

    # Utilisez append au lieu de push
    convConseil.append({"role": "user", "content": f"{messageF}"})

    # Appel à l'API
    chat_completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=convConseil
    )

    # Imprimez la structure complète de la réponse pour comprendre sa structure
    for choice in chat_completion.choices:
        if choice.message.role == "assistant":
            reponse += choice.message.content  # Utilisez += pour concaténer les chaînes de caractères
        
    return reponse

def conseiller_texte(texte):
    # Vérifier si le texte est supérieur à 2000 caractères
    if len(texte) > 2000:
        # Prend seulement les 2000 premiers caractères
        texte = texte[:2000]
    
    # Construire le message de conseil
    message_conseil = "Voici le texte à conseiller : " + texte
    # Appel à la fonction fictive communicationConseil (à remplacer par la fonction réelle que vous utilisez)
    return communicationConseil(message_conseil)

## Bonnes pratiques detectees sur le texte
convBonnePratique = []
roleBonnePratique = f"Ton role est de detecter les bonnes pratiques sur le texte. Tu dois repondre par un court paragraphe de 2-3 phrases"
convBonnePratique.append({"role": "system", "content": f"{roleBonnePratique}"})

def communicationBonnePratique(messageF):
    reponse = ""

    # Utilisez append au lieu de push
    convBonnePratique.append({"role": "user", "content": f"{messageF}"})

    # Appel à l'API
    chat_completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=convBonnePratique
    )

    # Imprimez la structure complète de la réponse pour comprendre sa structure
    for choice in chat_completion.choices:
        if choice.message.role == "assistant":
            reponse += choice.message.content  # Utilisez += pour concaténer les chaînes de caractères
        
    return reponse

def reperer_bonne_pratique(texte):
    # Vérifier si le texte est supérieur à 2000 caractères
    if len(texte) > 2000:
        # Prend seulement les 2000 premiers caractères
        texte = texte[:2000]
    
    # Construire le message de conseil
    message_bonne_pratique = "Voici le texte à analyser : " + texte
    # Appel à la fonction fictive communicationConseil (à remplacer par la fonction réelle que vous utilisez)
    return communicationBonnePratique(message_bonne_pratique)

## Remarques sur le texte
convRemarque = []
roleRemarque = f"Ton role est de faire des remarques sur le texte. Tu dois faire des remarques sur le texte de niveau universitaire. Ton reponse est un court paragraphe de 2-3 phrases)"
convRemarque.append({"role": "system", "content": f"{roleRemarque}"})

def communicationRemarque(messageF):
    reponse = ""

    # Utilisez append au lieu de push
    convRemarque.append({"role": "user", "content": f"{messageF}"})

    # Appel à l'API
    chat_completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=convRemarque
    )

    # Imprimez la structure complète de la réponse pour comprendre sa structure
    for choice in chat_completion.choices:
        if choice.message.role == "assistant":
            reponse += choice.message.content  # Utilisez += pour concaténer les chaînes de caractères
        
    return reponse

def remarque_texte(texte):
    # Vérifier si le texte est supérieur à 2000 caractères
    if len(texte) > 2000:
        # Prend seulement les 2000 premiers caractères
        texte = texte[:2000]
    
    # Construire le message de conseil
    message_remarque = "Voici le texte à analyser : " + texte
    # Appel à la fonction fictive communicationConseil (à remplacer par la fonction réelle que vous utilisez)
    return communicationRemarque(message_remarque)

##  ----- Fonctions non liees a l'API OpenAI

def texte_en_phrases(texte: str) -> List[str]:
    # Découpe le texte en phrases en utilisant les points, points d'exclamation et points d'interrogation comme séparateurs.
    # Note : Cela peut ne pas être parfait pour tous les usages de la langue.
    phrases = re.split(r'(?<=[.!?]) +', texte)
    return phrases

def verifier_phrases(tableau_phrases, verifier_phrase):
    # Initialisation d'un tableau pour stocker les résultats booléens
    resultats = []
    # Itération sur chaque phrase dans le tableau
    for phrase in tableau_phrases:
        # Appel de la fonction de vérification sur la phrase
        resultat = verifier_phrase(phrase)
        # Ajout du résultat booléen dans le tableau des résultats
        resultats.append(resultat)
    return resultats

def verifier_faute(texte):
    if '1' in texte:
        return "Grammaire"
    elif '2' in texte:
        return "Orthographe"
    elif '3' in texte:
        return "Conjugaison"
    elif '4' in texte:
        return "syntaxe"
    else:
        return "Globale"

def concateneListeDict(liste1, liste2):
    # Assure que les deux listes ont la même longueur
    if len(liste1) != len(liste2):
        return "Les listes ne sont pas de la même longueur."
    
    # Crée et concatène les éléments des deux listes dans des instances de la classe Erreur
    resultat = [Erreur(elem1, elem2) for elem1, elem2 in zip(liste1, liste2)]
    return resultat


def creerPhraseObj(phrase): 
    try: 
        objPhrase = []
        objPhrase.append(phrase)
        listeDescriptionFautes = ast.literal_eval(detecter_phrase(phrase))
        listeTypeFautes = []
        for faute in listeDescriptionFautes:
            fauteVerif = verifier_faute(classer_phrase(faute))
            listeTypeFautes.append(fauteVerif)
        objPhrase.append(listeDescriptionFautes)
        objPhrase.append(listeTypeFautes)
        listeErreurs = concateneListeDict(listeTypeFautes,listeDescriptionFautes)
        return listeErreurs
        pass
    except Exception as e:
        return []

def creerPhrase(contenu: str) -> Phrase:
    fautes = creerPhraseObj(contenu)  # Trouve les fautes dans la phrase.
    return Phrase(contenu=contenu, fautes=fautes)


## FONCTION PRINCIPALE DU BACKEND
## Cette fonction prend une liste de phrases et retourne une liste de phrases avec les fautes detectees, classees et expliquees.
def creerPhrases(liste_phrases: List[str]) -> List[Phrase]:
    return [creerPhrase(contenu) for contenu in liste_phrases]
    


## ---------------------------------------------------------------- ##
## -----------------  FONCTIONS LIEES AU FRONTEND ----------------- ##
## ---------------------------------------------------------------- ##

# Utilisation de la fonction avec la liste phrases_exemple
def calculer_penalites(phrases, penalite_orthographe, penalite_conjugaison, penalite_grammaire):
    nb_total_fautes = 0
    total_penalite_orthographe = 0
    total_penalite_conjugaison = 0
    total_penalite_grammaire = 0

    for phrase in phrases:
        for erreur in phrase.fautes:
            nb_total_fautes += 1
            if erreur.typeErreur == "Orthographe":
                total_penalite_orthographe += penalite_orthographe
            elif erreur.typeErreur == "Conjugaison":
                total_penalite_conjugaison += penalite_conjugaison
            elif erreur.typeErreur == "Grammaire":
                total_penalite_grammaire += penalite_grammaire

    penalite_totale = round(total_penalite_orthographe + total_penalite_conjugaison + total_penalite_grammaire, 2)
    return nb_total_fautes, total_penalite_orthographe, total_penalite_conjugaison, total_penalite_grammaire, penalite_totale


@app.route('/update_penalties', methods=['POST'])
def update_penalties():
    # Supposons que phrases_exemple est déjà rempli avec les phrases et erreurs initiales
    global phrases_exemple

    penalite_orthographe = float(request.form.get('orthographe_penalité', 1))
    penalite_conjugaison = float(request.form.get('conjugaison_penalité', 1))
    penalite_grammaire = float(request.form.get('grammaire_penalité', 1))

    nb_total_fautes, penalite_orthographe_total, penalite_conjugaison_total, penalite_grammaire_total, penalite_totale = calculer_penalites(
        phrases_exemple, penalite_orthographe, penalite_conjugaison, penalite_grammaire)

    # Retournez les données mises à jour pour être utilisées dans la page actuelle sans recharger
    return jsonify(
        penalite_orthographe_total=penalite_orthographe_total,
        penalite_conjugaison_total=penalite_conjugaison_total,
        penalite_grammaire_total=penalite_grammaire_total,
        penalite_totale=penalite_totale
    )


@app.route('/corrector', methods=['POST'])
def corrector():
    # texte = request.form['text_content']  # Récupérez le texte
    texte = request.form.get('text_content', '')

    print("texte récupéré =", texte)
    # Simulation
    # texte = "L'enfant jouait tranquillement dans le jardin, mais ils n'ont pas vu le temps passer et il a commencer à pleuvoir fort."
    global phrases_exemple
    aAmeliorer = conseiller_texte(texte)
    bonnePratique = reperer_bonne_pratique(texte)
    remarque =  remarque_texte(texte)
    phrasesEntree = texte_en_phrases(texte)
    phrases_exemple = creerPhrases(phrasesEntree)
    liste_commentaire = [bonnePratique, aAmeliorer, remarque]
    # print("PHRASE ENTREEEEEES ET IA CORRECTION")
    # # print(phrases_exemple)
    # print("OOOOOOOOOOOOOOO")

    # phrases_exemple = [
    #     Phrase("Ceci est une phrase sans faute.", []),
    #     Phrase("Elle a acheter un nouveau livre.",
    #            [Erreur("Conjugaison", "'acheter' doit être remplacé par 'acheté'")]),
    #     Phrase("Les livres est sur la table.", [Erreur("Grammaire", "'est' doit être remplacé par 'sont'")]),
    # ]
    # # print(phrases_exemple)
    # phrases_exemple.append(
    #     Phrase("Ce livre et très interessant.", [
    #         Erreur("Orthographe", "'et' doit être remplacé par 'est'"),
    #         Erreur("Orthographe", "'interessant' doit être remplacé par 'intéressant'"), ]))

    # print(phrases_exemple)

    # Appliquez la correction ici sur le texte soumis

    nb_erreurs_conjugaison, nb_erreurs_orthographe, nb_erreurs_grammaire = compter_erreurs_par_type(phrases_exemple)
    total_erreurs = nb_erreurs_conjugaison + nb_erreurs_orthographe + nb_erreurs_grammaire
    if (total_erreurs == 0):
        resultat_sans_faute = "Il n'y a pas d'erreur dans ce texte"
    else:
        resultat_sans_faute = ""
    ratio_orthographe = round(nb_erreurs_orthographe / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    ratio_conjugaison = round(nb_erreurs_conjugaison / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    ratio_grammaire = round(nb_erreurs_grammaire / total_erreurs * 100, 2) if total_erreurs > 0 else 0

    penalite_orthographe = float(request.form.get('orthographe_penalité', 1))
    penalite_conjugaison = float(request.form.get('conjugaison_penalité', 1))
    penalite_grammaire = float(request.form.get('grammaire_penalité', 1))
    print("penalité_conjugaison=", penalite_conjugaison)

    # Vous pouvez maintenant appeler la fonction calculer_penalites avec les pénalités ajustées
    nb_total_fautes, penalite_orthographe_total, penalite_conjugaison_total, penalite_grammaire_total, penalite_totale = calculer_penalites(
        phrases_exemple, penalite_orthographe, penalite_conjugaison, penalite_grammaire)

    return render_template('correction.html',
                           phrases=phrases_exemple,
                           nb_erreurs_conjugaison=nb_erreurs_conjugaison,
                           nb_erreurs_orthographe=nb_erreurs_orthographe,
                           nb_erreurs_grammaire=nb_erreurs_grammaire,
                           ratio_conjugaison=ratio_conjugaison,
                           ratio_orthographe=ratio_orthographe,
                           ratio_grammaire=ratio_grammaire,
                           penalite_orthographe=penalite_orthographe_total,
                           penalite_conjugaison=penalite_conjugaison_total,
                           penalite_grammaire=penalite_grammaire_total,
                           penalite_totale=penalite_totale,
                           resultat_sans_faute=resultat_sans_faute,
                           liste_commentaire=liste_commentaire)

    def nombre_erreurs_par_phrase(phrase):
        return len(phrase.fautes) if phrase.fautes else 0

    nb_erreurs_par_phrase = [nombre_erreurs_par_phrase(phrase) for phrase in phrases_exemple]

    variables_json = {
        'nb_erreurs_grammaire': nb_erreurs_grammaire,
        'nb_erreurs_conjugaison': nb_erreurs_conjugaison,
        'nb_erreurs_orthographe': nb_erreurs_orthographe,
        'ratio_orthographe': ratio_orthographe,
        'ratio_conjugaison': ratio_conjugaison,
        'ratio_grammaire': ratio_grammaire,
        'nb_erreurs_par_phrase': nb_erreurs_par_phrase,
    }

    print(phrases_exemple)
    return render_template('correction.html', texte=texte, phrases=phrases_exemple,
                           nb_erreurs_conjugaison=nb_erreurs_conjugaison, nb_erreurs_orthographe=nb_erreurs_orthographe,
                           nb_erreurs_grammaire=nb_erreurs_grammaire, ratio_orthographe=ratio_orthographe,
                           ratio_conjugaison=ratio_conjugaison, ratio_grammaire=ratio_grammaire,
                           nb_total_fautes=nb_total_fautes, penalite_orthographe=penalite_orthographe,
                           penalite_conjugaison=penalite_conjugaison, penalite_grammaire=penalite_grammaire,
                           penalite_totale=penalite_totale, resultat_sans_faute=resultat_sans_faute,
                           nb_erreurs_par_phrase=nb_erreurs_par_phrase)


@app.route('/update_variables', methods=['DELETE'])
def update_variables():
    data = request.json
    numeroPhrase = data.get('indexPhrase')
    numeroFaute = data.get('indexFaute')

    if 0 <= numeroPhrase < len(phrases_exemple) and 0 <= numeroFaute < len(phrases_exemple[numeroPhrase].fautes):
        print("numeroPhrase", numeroPhrase)
        print(phrases_exemple[numeroPhrase].fautes[numeroFaute])
        print("OOOOOOOOOOOOOOOOOOO")
        del phrases_exemple[numeroPhrase].fautes[numeroFaute]
        print(phrases_exemple[numeroPhrase].fautes)
        print("IIIIIIIIIIIIIIIIIIIIII")
        # phrases_exemple[numeroPhrase].fautes_ignores = all(erreur.faute_ignoree for erreur in phrases_exemple[numeroPhrase].fautes)
        print("UUUUUUUUUUUUUUUUUUUU ")
    else:
        print("Error: Index out of range.")

    # correctorBis()
    # Retournez les nouvelles valeurs au format JSON
    nb_erreurs_conjugaison, nb_erreurs_orthographe, nb_erreurs_grammaire = compter_erreurs_par_type(phrases_exemple)
    total_erreurs = nb_erreurs_conjugaison + nb_erreurs_orthographe + nb_erreurs_grammaire
    if (total_erreurs == 0):
        resultat_sans_faute = "Il n'y a pas d'erreur dans ce texte"
    else:
        resultat_sans_faute = ""

    penalite_orthographe = float(request.form.get('orthographe_penalité', 1))
    penalite_conjugaison = float(request.form.get('conjugaison_penalité', 1))
    penalite_grammaire = float(request.form.get('grammaire_penalité', 1))

    ratio_orthographe = round(nb_erreurs_orthographe / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    ratio_conjugaison = round(nb_erreurs_conjugaison / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    ratio_grammaire = round(nb_erreurs_grammaire / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    nb_total_fautes, penalite_orthographe, penalite_conjugaison, penalite_grammaire, penalite_totale = calculer_penalites(
        phrases_exemple, penalite_orthographe, penalite_conjugaison, penalite_grammaire)

    return jsonify(nb_erreurs_orthographe=nb_erreurs_orthographe, nb_erreurs_conjugaison=nb_erreurs_conjugaison,
                   nb_erreurs_grammaire=nb_erreurs_grammaire, ratio_conjugaison=ratio_conjugaison,
                   ratio_grammaire=ratio_grammaire, ratio_orthographe=ratio_orthographe,
                   nb_total_fautes=nb_total_fautes, penalite_orthographe=penalite_orthographe,
                   penalite_conjugaison=penalite_conjugaison, penalite_grammaire=penalite_grammaire,
                   penalite_totale=penalite_totale)


def compter_erreurs_par_type(phrases):
    # Initialisation des compteurs
    nb_erreurs_conjugaison = 0
    nb_erreurs_orthographe = 0
    nb_erreurs_grammaire = 0


    # Parcourir chaque phrase
    for phrase in phrases:
        # Parcourir chaque erreur dans la phrase
        for erreur in phrase.fautes:
            print(phrase.fautes)
            # Incrémenter le compteur approprié en fonction du type d'erreur
            if erreur.typeErreur == "Conjugaison":
                nb_erreurs_conjugaison += 1
            elif erreur.typeErreur == "Orthographe":
                nb_erreurs_orthographe += 1
            elif erreur.typeErreur == "Grammaire":
                nb_erreurs_grammaire += 1
    
    return nb_erreurs_conjugaison, nb_erreurs_orthographe, nb_erreurs_grammaire

def generate_pdf(penalite_totale, penalite_grammaire, penalite_orthographe, penalite_conjugaison, nb_erreurs_orthographe, nb_erreurs_grammaire, nb_erreurs_conjugaison, phrases, filename='correction.pdf'):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Récapitulatif des fautes")

    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "Le texte comportait :")
    c.drawString(100, 700, f"{float(nb_erreurs_orthographe)} faute{'s' if float(nb_erreurs_orthographe) > 1 else ''} d'orthographe, soit {penalite_orthographe} de pénalité{'s' if float(penalite_orthographe) > 1 else ''}")
    c.drawString(100, 680, f"{float(nb_erreurs_grammaire)} faute{'s' if float(nb_erreurs_grammaire) > 1 else ''} de grammaire, soit {penalite_grammaire} de pénalité{'s' if float(penalite_grammaire) > 1 else ''}")
    c.drawString(100, 660, f"{float(nb_erreurs_conjugaison)} faute{'s' if float(nb_erreurs_conjugaison) > 1 else ''} de conjugaison, soit {penalite_conjugaison} de pénalité{'s' if float(penalite_conjugaison) > 1 else ''}")
    c.drawString(100, 640, f"Donc un total de pénalités de {penalite_totale}")
    y_position = 610  # Position Y initiale pour le texte

    for phrase in phrases.split('\n'):
        wrapped_lines = textwrap.wrap(phrase, width=70)  # 70 caractères par ligne
        for line in wrapped_lines:
            c.drawString(100, y_position, line)
            y_position -= 20  # Décalage pour la prochaine ligne

    c.save()
    buffer.seek(0)
    return buffer, filename


@app.route('/download-correction', methods=['POST'])
def download_correction():
    
    nb_erreurs_orthographe = request.form['nb_erreurs_orthographe']
    nb_erreurs_grammaire = request.form['nb_erreurs_grammaire']
    nb_erreurs_conjugaison = request.form['nb_erreurs_conjugaison']
    penalite_orthographe = request.form['penalite_orthographe']
    penalite_conjugaison = request.form['penalite_conjugaison']
    penalite_grammaire = request.form['penalite_grammaire']
    penalite_totale = request.form['penalite_totale']
    phrases = request.form['phrases']

    buffer, filename = generate_pdf(penalite_totale, penalite_grammaire, penalite_orthographe, penalite_conjugaison, nb_erreurs_orthographe, nb_erreurs_grammaire, nb_erreurs_conjugaison, phrases)
    return send_file(buffer, as_attachment=True, download_name=filename)




if __name__ == '__main__':
    app.run(debug=True)



