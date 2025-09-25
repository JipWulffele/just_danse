import numpy as np
import cv2
import matplotlib.pyplot as plt

class Ecran():
    def __init__(self):
        pass

    def get_ecran_start(self, size=(1080, 720)):
        
        width, height = size

        # Create a white background image
        frame_start = np.ones((height, width, 3), dtype=np.uint8) * 255  
        # charger l'image 
        image_path = "./assets/img_jamila/Image collée.png"

        

        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if img is not None:
            # Vérifier si l'image a un canal alpha
            if img.shape[2] == 4:
                # Séparer les canaux
                r, g, b, a = cv2.split(img)
                # Créer un fond blanc
                white_bg = np.ones_like(a, dtype=np.uint8) * 255
                # Appliquer le masque alpha (a) sur chaque canal
                b = cv2.bitwise_or(b, white_bg, mask=cv2.bitwise_not(a))
                g = cv2.bitwise_or(g, white_bg, mask=cv2.bitwise_not(a))
                r = cv2.bitwise_or(r, white_bg, mask=cv2.bitwise_not(a))
                # Fusionner sans alpha
                img = cv2.merge((r, g, b))

            # Redimensionner et coller
            img = cv2.resize(img, (200, 200))
            # Convertir en HSV pour mieux détecter 
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Définir plage de couleur à changer (par exemple teintes sombres/bleues)
            lower = np.array([0, 0, 0])
            upper = np.array([150, 255, 100]) # ajuster selon couleur initiale du vêtement

            mask = cv2.inRange(hsv, lower, upper)

            # Remplacer par rouge
            img[mask > 0] = [0, 0, 255] # BGR → rouge
            frame_start[0:200, 0:200] = img
        else:
            print(f"⚠️ Image non trouvée à : {image_path}")

        # Deuxième image à l'opposé (bas à droite)
        image_path2 = "./assets/img_jamila/Image2.png"  # Mets ici le chemin de la 2e image assets/img_jamila/Image collée (2).png

        img2 = cv2.imread(image_path2, cv2.IMREAD_UNCHANGED)

        if img2 is not None:
            if img2.shape[2] == 4:
                r, g, b, a = cv2.split(img2)
                white_bg = np.ones_like(a, dtype=np.uint8) * 255
                b = cv2.bitwise_or(b, white_bg, mask=cv2.bitwise_not(a))
                g = cv2.bitwise_or(g, white_bg, mask=cv2.bitwise_not(a))
                r = cv2.bitwise_or(r, white_bg, mask=cv2.bitwise_not(a))
                img2 = cv2.merge((r, g, b))

            img2 = cv2.resize(img2, (200, 200))
            hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
            lower = np.array([0, 0, 0])
            upper = np.array([150, 255, 100])
            mask2 = cv2.inRange(hsv2, lower, upper)
            img2[mask2 > 0] = [0, 0, 255]  # rouge

            # Coller l'image en bas à droite
            frame_start[-200:, -200:] = img2
        else:
            print(f"⚠️ Deuxième image non trouvée à : {image_path2}")

        # Liste des pronoms
        titre = "Just dance: ACV special"
        cv2.putText(frame_start, titre, (400,100), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=1, 
                        color=(0, 0, 255), 
                        thickness=3)

        noms = ["Jip Wulffele ", "Diletta Ciardo ", "Jamila Obeid"]
        
    
        # Position de départ pour afficher les noms
        x, y = 400, 200
        espacement = 60  # espace vertical entre les noms

        for i, nom in enumerate(noms):
            position = (x, y + i * espacement)
            cv2.putText(frame_start, nom, position, 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=1, 
                        color=(0, 0, 0), 
                        thickness=3)
        
        return frame_start
        
if __name__ == "__main__":
    ecran = Ecran()
    frame = ecran.get_ecran_start()
    # imshow frame


    # Option 1: Use OpenCV to display
    cv2.namedWindow("Just Danse", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("Noms sur écran", width, height)
    
    cv2.imshow("Just Danse", frame)
   # cv2.imshow("image")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #Option 2: Use matplotlib (uncomment if preferred)
    # Affichage avec matplotlib (convertir BGR -> RGB)
