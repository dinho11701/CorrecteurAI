/* script.js */


document.addEventListener('DOMContentLoaded', function() {

document.getElementById('transferTextButton').addEventListener('click', function (event) {
    event.preventDefault(); // Empêche le comportement par défaut du formulaire

    var fileInput = document.getElementById('fileUpload');
    var editableTextarea = document.getElementById('editable-textarea');
    var file = fileInput.files[0]; // Obtenez le fichier sélectionné

    if (file) {
        var reader = new FileReader();

        reader.onload = function (e) {
            var fileContent = e.target.result;
            // Injectez le contenu du fichier dans la zone de texte
            editableTextarea.textContent = fileContent;
        };

        reader.readAsText(file);
    }
});
})

function decrementationFaute (targetElement) {
    console.log ("Tu fonctionnes nouvelle fonction ?");
    var endPopUp = document.getElementById('errorPopup');
  var nbErreurParPhrase = parseInt(targetElement.getAttribute('data-nb-erreurs'));
  if (nbErreurParPhrase > 0) {
      nbErreurParPhrase--;
      targetElement.setAttribute('data-nb-erreurs', nbErreurParPhrase);
      if (nbErreurParPhrase === 0) {
          targetElement.classList.remove('error');
          endPopUp.classList.add('faute-ignoree');
      }
  }
    }

function afficherPopup(indexPhrase,event) {
  var popup = document.getElementById('errorPopup');
  var popupText = document.getElementById('errorContent');
    
  // Vérifie si les attributs de données existent avant de continuer
  if (!event.target.dataset.description || !event.target.dataset.typeerreur) {
      console.error('Données de l\'erreur manquantes.');
      return; // Sortie anticipée de la fonction si les données nécessaires sont absentes
  }
  
  var descriptionsErreur = event.target.dataset.description.split("|");
  console.log("----Descriptions Erreur----");
  console.log(descriptionsErreur);
  console.log(event.target.dataset.description);
  var typesErreur = event.target.dataset.typeerreur.split("|");
  console.log(event.target.dataset.typeerreur)


    popupText.innerHTML = ""; // Clear previous content
    descriptionsErreur.forEach((description, index) => {
      var errorText = document.createElement("p");
  
      var colorPastille = document.createElement("div");
  
      choseColor(colorPastille, typesErreur[index]);
  
      errorText.appendChild(colorPastille);
  
      errorText.innerHTML += "<span class='important-line faute-titre'> Erreur " + typesErreur[index] + "</span><br>" + description;
  
      popupText.appendChild(errorText);
  
      var ignoreButton = document.createElement("button");
      ignoreButton.textContent = "Ignorer faute";
      ignoreButton.classList.add('btn', 'btn-primary', 'btn-popup');
      let indexFaute = index;
      ignoreButton.onclick = function() { ignorerFaute(indexPhrase, indexFaute, event.target);};
      popupText.appendChild(ignoreButton);
    });
  popup.style.left = (event.clientX + 10) + 'px'; // Positionner la popup près de la souris
  popup.style.top = (event.clientY + 10) + 'px';
  popup.style.display = 'block';
  // Position popup based on event details or use fixed positioning.


function choseColor(element, typeErreur) {
    if (typeErreur === 'Conjugaison') {
      element.classList.add('little-blue-cube');
    } else if (typeErreur === 'Orthographe') {
      element.classList.add('little-red-cube');
    } else {
      element.classList.add('little-green-cube');
    }
  }
}


// function ignorerFaute(numeroPhrase, numeroErreur, targetElement) {
//     const donnees = { indexPhrase: numeroPhrase, indexFaute: numeroErreur };

//     fetch('/update_variables', {
//         method: 'DELETE',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(donnees),
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         return response.json();
//     })
//     .then(data => {
//         // Update error counts and progress bars
//         updateErrorCounts(data);
//         document.getElementById('errorPopup').style.display = 'none';
//         var endPopUp = document.getElementById('errorPopup');
//         var nbErreurParPhrase = parseInt(targetElement.getAttribute('data-nb-erreurs'));
//         if (nbErreurParPhrase > 0) {
//             nbErreurParPhrase--;
//             targetElement.setAttribute('data-nb-erreurs', nbErreurParPhrase);
//             if (nbErreurParPhrase === 0) {
//                 targetElement.classList.remove('error');
//                 endPopUp.classList.add('faute-ignoree');
//             }
//         }
//         // Recharge la page pour afficher les modifications
//        // location.reload(); // Ajoutez cette ligne pour recharger la page
//        updatePhraseAfterIgnoring(targetElement, indexFaute);
//         document.getElementById('errorPopup').style.display = 'none'; // Fermer le popup
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     })
// }
function ignorerFaute(indexPhrase, indexFaute, targetElement) {
    // Construire les données à envoyer
    const data = { indexPhrase: indexPhrase, indexFaute: indexFaute };

    // Envoyer les données au serveur pour mettre à jour l'état
    fetch('/update_variables', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Ici, vous pouvez mettre à jour le DOM en fonction de la réponse
        // Par exemple, supprimer la faute du data-description et data-typeErreur
        updateErrorCounts(data);

        updatePhraseAfterIgnoring(targetElement, indexFaute);
        document.getElementById('errorPopup').style.display = 'none'; // Fermer le popup
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
function updatePhraseAfterIgnoring(targetElement, indexFaute) {
    let descriptions = targetElement.dataset.description.split('|');
    let types = targetElement.dataset.typeerreur.split('|');

    // Supprimer la faute ignorée
    descriptions.splice(indexFaute, 1);
    types.splice(indexFaute, 1);

    // Mettre à jour le dataset
    targetElement.dataset.description = descriptions.join('|');
    targetElement.dataset.typeerreur = types.join('|');

    // Si toutes les fautes ont été ignorées, changer le style ou cacher l'indicateur d'erreur
    if (descriptions.length === 0) {
        targetElement.classList.remove('error'); // Supposer que 'error' est la classe utilisée pour indiquer une faute
    }
}


function updateErrorCounts(data) {
    document.getElementById('nb_erreurs_grammaire').textContent = data.nb_erreurs_grammaire;
    document.getElementById("nb_erreurs_conjugaison").innerHTML = data.nb_erreurs_conjugaison;
    document.getElementById('nb_erreurs_orthographe').textContent = data.nb_erreurs_orthographe;
    document.getElementById('penalite_orthographe').textContent = data.penalite_orthographe;
    document.getElementById("penalite_conjugaison").textContent = data.penalite_conjugaison;
    document.getElementById("penalite_grammaire").textContent = data.penalite_grammaire;
    document.getElementById("penalite_totale").textContent = data.penalite_totale;
    console.log(penalite_orthographe)
    
    // Update progress bars
    updateProgressBar('progress_bar_grammaire', data.ratio_grammaire);
    updateProgressBar('progress_bar_conjugaison', data.ratio_conjugaison);
    updateProgressBar('progress_bar_orthographe', data.ratio_orthographe);
}

function updateProgressBar(barId, ratio) {
    $('#' + barId).css('width', ratio + '%')
                 .attr('aria-valuenow', ratio)
                 .text(ratio + '%');
}



// Ajouter des gestionnaires pour fermer le popup en cliquant à l'extérieur
window.onclick = function (event) {
    var popup = document.getElementById('errorPopup');
    if (event.target == popup) {
        fermerPopup();
    }
};


function fermerPopup() {
    var popup = document.getElementById('errorPopup');
    popup.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {

const invisiblebutton = document.getElementById('invisiblebutton');
const banniere = document.getElementById('banniere');

invisiblebutton.addEventListener("click", () => {
    if (banniere.style.display == 'none') {
        banniere.style.display = "block";
    } else {
        banniere.style.display = "none";
    }
    });
})

function updateDisplay() {
    // Supposons que cette fonction est appelée après une suppression réussie
    $.ajax({
        url: '/update_variables',  // L'URL de votre endpoint Flask
        method: 'DELETE',  // ou 'DELETE', si vous passez des données pour la suppression
        success: function(data) {
            // Mettre à jour les éléments du DOM en fonction des données reçues
            $('#nb_erreurs_grammaire').text(data.nb_erreurs_grammaire);
            // Répéter pour les autres données reçues
        },
        error: function(error) {
            console.log("Erreur lors de la mise à jour des données : ", error);
        }
    });
}




