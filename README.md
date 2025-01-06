guide détaillé pour installer Flask et lancer votre jeu sur le terminal en utilisant Flas : 

Étape 1 : Installer Python
Assurez-vous que Python est installé sur votre système :
Téléchargez Python à partir du site officiel : Python.org.
Installez Python en cochant l'option "Add Python to PATH" pendant l'installation.
Pour vérifier, ouvrez le terminal (ou l’invite de commandes) et tapez :\\[0.5cm]
python --version  ou  python3 --version
Étape 2 : Créer un Environnement Virtuel
Un environnement virtuel permet d’isoler vos dépendances :
Créez un environnement virtuel
python -m venv env
Activez l'environnement virtuel
 Windows :
 env\Scripts\activate
macOS/Linux :
source env/bin/activate
Étape 3 : Installer Flask
Une fois dans votre environnement virtuel, installez Flask :
pip install flask
Pour vérifier l’installation, tapez :
pip show flask
Étape 4 : Installer les Autres Dépendances
Si votre projet a d'autres dépendances (comme Flask-Cors pour gérer les requêtes CORS), installez-les via pip. Par exemple :
pip install flask-cors
Étape 5 : Structure du Projet
Attention, il faut créer un dossier. Par exemple, le nom de dossier est "SharkGame". Ensuite, il faut créer des dossiers Backend et Frontend.
Dans le Backend, il faut qu'il contienne app.py et dans Frontend tous les autres fichiers.
Étape 6 : Lancer le Serveur Flask
Ouvrez votre terminal et naviguez jusqu’au répertoire du projet :
cd chemin/vers/votre/projet exemple : cd home/user/Desktop/SharkGame/Backend
Lancer l’application Flask :
python app.py
Par défaut, Flask s’exécute sur http://127.0.0.1:5000. Vous verrez des logs comme ceci :
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)











