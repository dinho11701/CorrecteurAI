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
from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
from flask import send_file
from flask import request
from werkzeug.utils import secure_filename


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
        model="gpt-4",
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
        model="gpt-4",
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
roleClasseur = f"Ton role est de recevoir des message contenant une description de faute de francais, Tu dois juger a quel type de faute correspond le mieux la description de la faute.Reponds 1 si c'est une faute de grammaire, 2 si c'est une faute d'orthographe, 3 si c'est une faute de conjugaison, 4 si c'est une faute de syntaxe. Repond seulement le chiffre correspondant"
convClasseur.append({"role": "system", "content": f"{roleClasseur}"})

def communicationClasseur(messageF):
    reponse = ""

    # Utilisez append au lieu de push
    convClasseur.append({"role": "user", "content": f"{messageF}"})

    # Appel à l'API
    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=convClasseur
    )

    # Imprimez la structure complète de la réponse pour comprendre sa structure
    for choice in chat_completion.choices:
        if choice.message.role == "assistant":
            reponse += choice.message.content  # Utilisez += pour concaténer les chaînes de caractères
        
    return reponse

def classer_phrase(phrase):
    return communicationClasseur(phrase)

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
def calculer_penalites(phrases):
    nb_total_fautes = 0
    penalite_orthographe = 0
    penalite_conjugaison = 0
    penalite_grammaire = 0


    for phrase in phrases:
        for erreur in phrase.fautes:
            nb_total_fautes += 1
            if erreur.typeErreur == "Orthographe":
                penalite_orthographe += 2
            elif erreur.typeErreur == "Conjugaison":
                penalite_conjugaison += 1
            elif erreur.typeErreur == "Grammaire":
                penalite_grammaire += 1

    penalite_totale = penalite_orthographe + penalite_conjugaison + penalite_grammaire
    return nb_total_fautes, penalite_orthographe, penalite_conjugaison, penalite_grammaire, penalite_totale

@app.route('/corrector', methods=['POST'])
def corrector():
    global phrases_exemple

    #texte = request.form['text_content']  # Récupérez le texte
    #print("Voici le texte : " + texte)
    #Simulation
    texte = "L'enfant jouait tranquillement dans le jardin, mais ils n'ont pas vu le temps passer et il a commencer à pleuvoir fort.Il était une foa, un petit garson qui s'apelait Tom. Il habitait dans une grande maisson avec sa famillie, mais il se sentait toujours seul car il n'avait pas d'amis. Un jour, il décida de partir à l'aventure dans la forêt deriere chez lui, malgré les avertissemments de ses parents qui lui disaient que c'était dangeureux."
    # texte += "  Sans prendre garde aux consseils de ses parents, il pris son sac à dos et y mis un bouteille d'eau, quelques biscuites et une lampe torche. Il partit en direction de la forêt, tout excité à l'idée de decouvrir ce que cachait cette grande étendue verte."
    # texte += "  Arrivé à la lisière de la forêt, Tom s'arreta un moment, regardant les arbres qui se balançaient doucement au vent. Il se sentit un peu effrayé mais sa curiosité était plus forte. Il fit donc ses premiers pas dans la forêt, écoutant les bruits étranges et les cris d'animaux sauvages."
    # texte += "  Il marcha pendant des heures, s'aventurant de plus en plus profondément dans la forêt, jusqu'à ce qu'il réalise qu'il s'était perdu. La panique commença à monter en lui. Il essaiya de retrouver son chemin mais toutes les directions lui semblaient identiques. La nuit commença à tomber, et Tom compris qu'il devait trouver un abri pour passer la nuit."
    # texte += "  Il trouva une petite cavité sous un arbre et décida de s'y installer pour la nuit. Il sorti sa lampe torche et ses biscuits et essaya de se rassurer en se disant que tout irait bien le lendemain. Mais il eut beaucoup de mal à s'endormir, écoutant les sons effrayants de la forêt nocturne."
    # texte += "  Le lendemain matin, après une nuit peuplée de cauchemards, Tom se réveilla, déterminé à trouver son chemin de retour. Il marcha toute la journée, fatigué, affamé, mais ne perdant jamais espoir. Finalement, alors que le soleil commençait à se coucher une fois de plus, il aperçut la lumière qui provenait de sa maison au loin. Il couru le reste du chemin, éclatant de joie lorsqu'il retrouva enfin sa famille qui était très inquiète mais heureuse de le revoir."
    # texte += "  La morale de cette histoire, c'est qu'il ne faut jamais ignorer les conseils des parents et qu'il est important de toujours être prudent, surtout dans les endroits inconnus."
    # texte += "  J'espère que ce texte répond à votre demande !"
    # texte += "L'enfant jouait tranquillement dans le jardin, mais ils n'ont pas vu le temps passer et il a commencer à pleuvoir fort.Il était une foa, un petit garson qui s'apelait Tom. Il habitait dans une grande maisson avec sa famillie, mais il se sentait toujours seul car il n'avait pas d'amis. Un jour, il décida de partir à l'aventure dans la forêt deriere chez lui, malgré les avertissemments de ses parents qui lui disaient que c'était dangeureux."
    # texte += "  Sans prendre garde aux consseils de ses parents, il pris son sac à dos et y mis un bouteille d'eau, quelques biscuites et une lampe torche. Il partit en direction de la forêt, tout excité à l'idée de decouvrir ce que cachait cette grande étendue verte."
    # texte += "  Arrivé à la lisière de la forêt, Tom s'arreta un moment, regardant les arbres qui se balançaient doucement au vent. Il se sentit un peu effrayé mais sa curiosité était plus forte. Il fit donc ses premiers pas dans la forêt, écoutant les bruits étranges et les cris d'animaux sauvages."
    # texte += "  Il marcha pendant des heures, s'aventurant de plus en plus profondément dans la forêt, jusqu'à ce qu'il réalise qu'il s'était perdu. La panique commença à monter en lui. Il essaiya de retrouver son chemin mais toutes les directions lui semblaient identiques. La nuit commença à tomber, et Tom compris qu'il devait trouver un abri pour passer la nuit."
    # texte += "  Il trouva une petite cavité sous un arbre et décida de s'y installer pour la nuit. Il sorti sa lampe torche et ses biscuits et essaya de se rassurer en se disant que tout irait bien le lendemain. Mais il eut beaucoup de mal à s'endormir, écoutant les sons effrayants de la forêt nocturne."

    phrasesEntree = texte_en_phrases(texte)
    phrases_exemple = creerPhrases(phrasesEntree)
    
    # phrases_exemple = [
    #     Phrase("Ceci est une phrase sans faute.", []),
    #     Phrase("Elle a acheter un nouveau livre.", [Erreur("Conjugaison", "'acheter' doit être remplacé par 'acheté'")]),
    #     Phrase("Les livres est sur la table.", [Erreur("Grammaire", "'est' doit être remplacé par 'sont'")]),
    # ]

    # # print(phrases_exemple)
    # phrases_exemple.append(
    # Phrase("Ce livre et très interessant.", [
    #     Erreur("Orthographe", "'et' doit être remplacé par 'est'"),
    #     Erreur("Orthographe", "'interessant' doit être remplacé par 'intéressant'"),]))
    # Appliquez la correction ici sur le texte soumis
    nb_erreurs_conjugaison, nb_erreurs_orthographe, nb_erreurs_grammaire = compter_erreurs_par_type(phrases_exemple)
    total_erreurs = nb_erreurs_conjugaison + nb_erreurs_orthographe + nb_erreurs_grammaire
    if (total_erreurs == 0):
        resultat_sans_faute = "Il n'y a pas d'erreur dans ce texte"
    else:
        resultat_sans_faute = ""
    ratio_orthographe = round(nb_erreurs_orthographe / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    ratio_conjugaison = round(nb_erreurs_conjugaison / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    ratio_grammaire = round(nb_erreurs_grammaire / total_erreurs* 100, 2) if total_erreurs > 0 else 0

    nb_total_fautes, penalite_orthographe, penalite_conjugaison, penalite_grammaire, penalite_totale = calculer_penalites(phrases_exemple)
    
    variables_json = {
    'nb_erreurs_grammaire': nb_erreurs_grammaire,
    'nb_erreurs_conjugaison': nb_erreurs_conjugaison,
    'nb_erreurs_orthographe': nb_erreurs_orthographe,
    'ratio_orthographe': ratio_orthographe,
    'ratio_conjugaison': ratio_conjugaison,
    'ratio_grammaire': ratio_grammaire,
    }
    return render_template('correction.html', texte=texte, phrases=phrases_exemple, nb_erreurs_conjugaison=nb_erreurs_conjugaison, nb_erreurs_orthographe=nb_erreurs_orthographe, nb_erreurs_grammaire=nb_erreurs_grammaire, ratio_orthographe=ratio_orthographe, ratio_conjugaison=ratio_conjugaison, ratio_grammaire=ratio_grammaire, nb_total_fautes=nb_total_fautes, penalite_orthographe=penalite_orthographe, penalite_conjugaison=penalite_conjugaison, penalite_grammaire=penalite_grammaire, penalite_totale=penalite_totale, resultat_sans_faute=resultat_sans_faute)

# @app.route('/correctorBis', methods=['POST'])
# def correctorBis():
#     texte = request.form['text_content']  # Récupérez le texte

#     #Simulation
#     # texte = "L'enfant jouait tranquillement dans le jardin, mais ils n'ont pas vu le temps passer et il a commencer à pleuvoir fort."
#     # phrasesEntree = texte_en_phrases(texte)
#     # phrases_exemple = creerPhrases(phrasesEntree)
    
    
    
#     # Appliquez la correction ici sur le texte soumis
#     nb_erreurs_conjugaison, nb_erreurs_orthographe, nb_erreurs_grammaire = compter_erreurs_par_type(phrases_exemple)
#     print("nb_erreurs_conjugaison",nb_erreurs_conjugaison,"nb_erreurs_orthographe",nb_erreurs_orthographe,"nb_erreurs_grammaire",nb_erreurs_grammaire)
#     print
#     total_erreurs = nb_erreurs_conjugaison + nb_erreurs_orthographe + nb_erreurs_grammaire
#     if (total_erreurs == 0):
#         resultat_sans_faute = "Il n'y a pas d'erreur dans ce texte"
#     else:
#         resultat_sans_faute = ""
#     ratio_orthographe = round(nb_erreurs_orthographe / total_erreurs * 100, 2) if total_erreurs > 0 else 0
#     ratio_conjugaison = round(nb_erreurs_conjugaison / total_erreurs * 100, 2) if total_erreurs > 0 else 0
#     ratio_grammaire = round(nb_erreurs_grammaire / total_erreurs* 100, 2) if total_erreurs > 0 else 0
#     print(ratio_orthographe)

#     nb_total_fautes, penalite_orthographe, penalite_conjugaison, penalite_grammaire, penalite_totale = calculer_penalites(phrases_exemple)
#     print(penalite_totale)

#     variables_json = {
#     'nb_erreurs_grammaire': nb_erreurs_grammaire,
#     'nb_erreurs_conjugaison': nb_erreurs_conjugaison,
#     'nb_erreurs_orthographe': nb_erreurs_orthographe,
#     'ratio_orthographe': ratio_orthographe,
#     'ratio_conjugaison': ratio_conjugaison,
#     'ratio_grammaire': ratio_grammaire,
#     }

#     return render_template('correction.html', texte=texte, phrases=phrases_exemple, nb_erreurs_conjugaison=nb_erreurs_conjugaison, nb_erreurs_orthographe=nb_erreurs_orthographe, nb_erreurs_grammaire=nb_erreurs_grammaire, ratio_orthographe=ratio_orthographe, ratio_conjugaison=ratio_conjugaison, ratio_grammaire=ratio_grammaire, nb_total_fautes=nb_total_fautes, penalite_orthographe=penalite_orthographe, penalite_conjugaison=penalite_conjugaison, penalite_grammaire=penalite_grammaire, penalite_totale=penalite_totale, resultat_sans_faute=resultat_sans_faute)


@app.route('/update_variables', methods=['DELETE'])
def update_variables():
    data = request.json
    numeroPhrase = data.get('indexPhrase')
    numeroFaute = data.get('indexFaute')

    if 0 <= numeroPhrase < len(phrases_exemple) and 0 <= numeroFaute < len(phrases_exemple[numeroPhrase].fautes):
        del phrases_exemple[numeroPhrase].fautes[numeroFaute] 
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
    ratio_orthographe = round(nb_erreurs_orthographe / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    ratio_conjugaison = round(nb_erreurs_conjugaison / total_erreurs * 100, 2) if total_erreurs > 0 else 0
    ratio_grammaire = round(nb_erreurs_grammaire / total_erreurs* 100, 2) if total_erreurs > 0 else 0
    nb_total_fautes, penalite_orthographe, penalite_conjugaison, penalite_grammaire, penalite_totale = calculer_penalites(phrases_exemple)

    return jsonify(nb_erreurs_orthographe =nb_erreurs_orthographe,nb_erreurs_conjugaison=nb_erreurs_conjugaison,nb_erreurs_grammaire=nb_erreurs_grammaire, ratio_conjugaison=ratio_conjugaison,ratio_grammaire=ratio_grammaire,ratio_orthographe=ratio_orthographe,nb_total_fautes=nb_total_fautes, penalite_orthographe=penalite_orthographe, penalite_conjugaison=penalite_conjugaison, penalite_grammaire=penalite_grammaire, penalite_totale=penalite_totale)




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

def generate_pdf(texte, filename='correction.pdf'):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Écrire le texte corrigé dans le PDF
    c.drawString(100, 750, "Texte corrigé :Ceci est une phrase sans faute.Il mange une pomme.Le chien court vite dans le jardin.Elle a acheté un nouveau livre. Les livres sont sur la table. Il mange une pomme.")
    c.drawString(100, 730, texte)

    c.save()
    buffer.seek(0)
    return buffer, filename


@app.route('/download-correction', methods=['POST'])
def download_correction():
    if 'texte_corrigé' not in request.form:
        # Gérer l'erreur ici, par exemple, rediriger vers une autre page avec un message d'erreur
        return redirect(url_for('index'))

    buffer, filename = generate_pdf(request.form['texte_corrigé'])
    return send_file(buffer, as_attachment=True, download_name=filename)


if __name__ == '__main__':
    app.run(debug=True)



