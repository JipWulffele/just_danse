import numpy as np
import cv2
import matplotlib.pyplot as plt
import time
import json

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
            # Convertir en HSV pour mieux détecter اللون
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
    
    def show_ecran(self, video, reference, start_screen_frame, duration):
        start_time = time.time()
        while time.time() - start_time < duration:  # show for 2 seconds
            video.show(start_screen_frame)
            if video.should_quit('q'):
                video.release()
                reference.release()
                return
            cv2.waitKey(1) 

    def choose_song(self, config_path="assets/config/songs.json", size=(1080, 720)):
        with open(config_path, "r") as f:
            data = json.load(f)

        songs = data["songs"]

        # Menu loop
        selected = 0  # Index of the currently highlighted song
        while True:
            # Background
            frame = 255 * np.ones((size[1], size[0], 3), dtype=np.uint8)

            # Title
            cv2.putText(frame, "🎵 Choose Your Song 🎵",
                        (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5)

            # List songs with highlight
            for idx, song in enumerate(songs):
                y = 200 + idx * 80
                if idx == selected:
                    # Draw a highlight rectangle behind the selected song
                    cv2.rectangle(frame,
                                (120, y - 40),
                                (900, y + 10),
                                (200, 200, 255),  # light purple
                                -1)
                    color = (0, 0, 255)  # red text for selected
                else:
                    color = (0, 0, 0)    # black text for others

                cv2.putText(frame, f"{idx+1}. {song['name']}",
                            (150, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 4)

            cv2.imshow("Menu", frame)

            # Handle key input
            key = cv2.waitKey(100)
            if key == 82:       # Up arrow
                selected = (selected - 1) % len(songs)
            elif key == 84:     # Down arrow
                selected = (selected + 1) % len(songs)
            elif key == 13:           # Enter key
                cv2.destroyWindow("Menu")
                return songs[selected]
            elif key == ord('q'):     # Quit
                cv2.destroyWindow("Menu")
                return None

            
        
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
