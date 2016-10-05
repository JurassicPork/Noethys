Noethys
==================
Logiciel de gestion libre et gratuit de gestion multi-activit�s pour 
les accueils de loisirs, cr�ches, garderies p�riscolaires, cantines, 
TAP ou NAP, clubs sportifs et culturels...

Plus d'infos sur www.noethys.com


Proc�dure d'installation
------------------

Si vous souhaitez installer manuellement Noethys sur
Windows, Mac OS ou Linux, il vous suffit de copier
l'int�gralit� du r�pertoire sur votre disque dur et
d'installer toutes les d�pendances list�es ci-dessous.


D�pendances pour Windows
------------------
Sur Windows, vous devez aller sur les sites des auteurs pour 
rechercher et installer les biblioth�ques suivantes.

- Python 2.7 (http://www.python.org/)
- wxPython 3.0 - version unicode (http://www.wxpython.org/)
- dateutil (http://pypi.python.org/pypi/python-dateutil)
- MySQLdb (http://sourceforge.net/projects/mysql-python/)
- NumPy (http://new.scipy.org/download.html)
- PIL (http://www.pythonware.com/products/pil/)
- PyCrypto (https://www.dlitz.net/software/pycrypto/)
- PyCrypt (https://sites.google.com/site/reachmeweb/pycrypt)
- ReportLab (http://www.reportlab.com/software/opensource/rl-toolkit/download/)
- MatPlotLib (http://matplotlib.sourceforge.net/)
- ObjectListView (http://objectlistview.sourceforge.net/python/)
- pyExcelerator (http://sourceforge.net/projects/pyexcelerator/)
- videoCapture (http://videocapture.sourceforge.net/)
- Pyttsx (http://pypi.python.org/pypi/pyttsx)
- Appdirs (https://pypi.python.org/pypi/appdirs)
- Psutil (https://pypi.python.org/pypi/psutil)
- Paramiko (https://pypi.python.org/pypi/paramiko)


D�pendances pour Linux
------------------


- python 2.7 (Install� en principe par d�faut sous ubuntu)
- python-wxgtk3.0 (Biblioth�que graphique wxPython)
- python-mysqldb (Pour l'utilisation en mode r�seau)
- python-dateutil (Manipulation des dates)
- python-numpy (Calculs avanc�s)
- python-imaging (Traitement des photos)
- python-reportlab (Cr�ation des PDF)
- python-matplotlib (Cr�ation de graphes)
- python-xlrd (Traitement de fichiers Excel)
- python-crypto (pour crypter les sauvegardes)
- python-excelerator (pour les exports format excel)
- python-pyscard (pour pouvoir configurer les proc�dures de badgeage)
- python-opencv (pour la d�tection automatique des visages)
- python-pip (qui permet d'installer pyttsx et icalendar)
- python-appdirs (pour rechercher les r�pertoires de stockage des donn�es)
- python-psutil (infos syst�me)
- python-paramiko (Prise en charge SSH)

Ils s'installent depuis le terminal tout simplement avec la commande (**� ex�cuter si besoin avec sudo**):

```
apt-get install python-mysqldb python-dateutil python-numpy python-imaging python-reportlab python-matplotlib 
python-xlrd python-excelerator python-pip python-pyscard python-opencv python-crypto python-appdirs
python-wxgtk3.0 python-sqlalchemy libcanberra-gtk-module python-psutil python-paramiko
```

Et pour pyttsx et icalendar il faut avoir install� python-pip (ce qui a �t fait dans l'�tape pr�c�dente) et les installer par:
```
pip install pyttsx
pip install icalendar
```
Puis:
```
apt-get install python-wxgtk3.0
```
Si cette commande se termine correctement, vous avez fini.


Pour lancer Noethys, lancez le terminal de Linux, placez-vous dans le r�pertoire d'installation de Noethys, puis saisissez la commande "python Noethys.py"



Dans le cas contraire, o� votre version de debian ou d'ubuntu ne proposerait pas python-wxgtk3.0 (ce qui est le cas pour ubuntu LTS 14.04 et toute distribution bas�e sur cette version), la commande pr�c�dente retourne une erreur.

Ex�cutez alors la commande suivante:
```
apt-get install python-wxgtk2.8 libjpeg62 libwxgtk3.0-0
```

Puis t�l�chargez les paquets de la biblioth�que graphique correspondant � votre architecture (32 ou 64 bits), wxpython et wxwidgets, ainsi que libtiff4.

Vous trouverez ces fichiers sur le site de Noethys : **Menu Assistance > Ressources communautaires > Liste des ressources > Divers**.

Puis ex�cutez la commande suivante:
```
dpkg -i dossier/wxwidget*****.deb dossier/wxpython*****.deb dossier/libtiff4*****.deb
```

**dossier**: le dossier dans lequel vous avez t�l�charg� la biblioth�que
**wxwidget\*****.deb, wxpython\*****.deb et libtiff4\*****.deb** sont les fichiers correspondant � votre architecture que vous avez t�l�charg�s.

**V�rifiez que vous avez choisi la version correspondant � votre architecture (32 ou 64 bits).**



