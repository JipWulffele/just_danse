# 💃 Just_Danse
## 🤖 Cours de danse gamifié avec MediaPipe & OpenCV

Ce projet utilise **MediaPipe** et **OpenCV** pour détecter les poses du corps en temps réel à partir d'une webcam et les comparer à une **vidéo de référence de danse**.  
La logique de scoring est **basée sur la distance entre les poses** du participant et celles de la vidéo de référence.

---

## ✨ Fonctionnalités

- 🎥 Détection et suivi du corps en temps réel avec la webcam.
- 💃 Affichage de la vidéo de référence en grand et du flux webcam en PiP (Picture-in-Picture).
- 🧩 Overlay d’icônes pour indiquer les mouvements à réaliser.
- 🧠 Scoring en direct basé sur la similarité entre la pose du participant et la référence.
- ⏱ Countdown avant le début de la danse.
- 🔄 Possibilité de **relancer la session** ou quitter à la fin de la vidéo de référence.

---

## ⚙️ Installation

### 1. Cloner le projet
```bash
git clone git@github.com:JipWulffele/just_danse.git
cd just_danse
```
### 2. Créer un environnement
```bash
conda env create -f envirornment.yml
conda activate tf-env
```
### 3. Exécuter le programme
```bash
python main.py
```

---

## 📝 Auteurs

- 👤 Jip Wulffelé
- 👤 Diletta Ciardo
- 👤 Jamila Obeid

🎓 Réalisé dans le cadre du module ACV au sein du Campus Numérique dans les Alpes