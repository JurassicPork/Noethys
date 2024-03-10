Noethys
==================
Logiciel de gestion libre et gratuit de gestion multi-activités pour 
les accueils de loisirs, crèches, garderies périscolaires, cantines, 
TAP ou NAP, clubs sportifs et culturels...

Plus d'infos sur www.noethys.com


Installation sur Windows
------------------

Allez dans la rubrique Téléchargements du site www.noethys.com pour télécharger la version compilée pour Windows.


Installation sur Ubuntu 22.04 pour du python 3.10
------------------

Lancez dans votre console Linux les commandes suivantes :
```
sudo apt-get install git curl libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0 python3-pip python3-pyscard python3-dev default-libmysqlclient-dev build-essential
pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04 wxPython
git clone https://github.com/JurassicPork/Noethys
pip3 install -r Noethys/requirements.txt
python3 Noethys/noethys/Noethys.py
```



Installation depuis les sources
------------------
Si vous rencontrez les difficultés d'installation ou souhaitez installer Noethys depuis les sources,
consultez les documents dédiés ici : https://github.com/Noethys/Noethys/tree/master/noethys/Doc

