import numpy as np
import cv2
import matplotlib.pyplot as plt
import time

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
    
    def show_ecran(self, video, reference, start_screen_frame, duration):
        start_time = time.time()
        while time.time() - start_time < duration:  # show for 2 seconds
            video.show(start_screen_frame)
            if video.should_quit('q'):
                video.release()
                reference.release()
                return
            cv2.waitKey(1) 
     
    def get_ecran_chute(self, size=(1080, 720)):
        
        width, height = size

        # Create a white background image
        frame_chute = np.ones((height, width, 3), dtype=np.uint8) * 255   
        titre = "Alerte : Chute"
        cv2.putText(frame_chute, titre, (400,100), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=1, 
                        color=(0, 0, 255), 
                        thickness=3) 
        
        #  image de chute
        
        image_path3 = "./assets/img_jamila/Image3.png"  
        img3 = cv2.imread(image_path3, cv2.IMREAD_UNCHANGED)
        if img3 is not None:
            if img3.shape[2] == 4:
                # Supprimer la transparence et remplacer par un fond blanc
                r, g, b, a = cv2.split(img3)
                white_bg = np.ones_like(a, dtype=np.uint8) * 255
                b = cv2.bitwise_or(b, white_bg, mask=cv2.bitwise_not(a))
                g = cv2.bitwise_or(g, white_bg, mask=cv2.bitwise_not(a))
                r = cv2.bitwise_or(r, white_bg, mask=cv2.bitwise_not(a))
                img3 = cv2.merge((r, g, b))

            # Redimensionner l’image
            img3 = cv2.resize(img3, (200, 200))

            

            # Positionner au centre de frame_chute
            h, w = frame_chute.shape[:2]
            y_offset = h // 2 - 100  # 200/2
            x_offset = w // 2 - 100

            # Coller l'image centrée
            frame_chute[y_offset:y_offset+200, x_offset:x_offset+200] = img3
        else:
            print(f"⚠️ Troisième image non trouvée à : {image_path3}")


    def get_ecran_chute2(self, size=(1080, 720)):

        width, height = size

        # Create a white background image
        frame_chute = np.ones((height, width, 3), dtype=np.uint8) * 255   
        titre = "Alerte : Chute"
        cv2.putText(frame_chute, titre, (400,100), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=1, 
                        color=(0, 0, 255), 
                        thickness=3) 
        
        # image de chute
        image_path3 = "./assets/img_jamila/Image3.png"  
        img3 = cv2.imread(image_path3, cv2.IMREAD_UNCHANGED)

        if img3 is not None:
            # Resize
            img3 = cv2.resize(img3, (200, 200))

            # Get center position
            h, w = frame_chute.shape[:2]
            y_offset = h // 2 - 100
            x_offset = w // 2 - 100

            # If the image has alpha channel (4th channel)
            if img3.shape[2] == 4:
                # Split channels
                b, g, r, a = cv2.split(img3)

                # Create 3-channel image and alpha mask
                img_rgb = cv2.merge((b, g, r))
                mask = cv2.merge((a, a, a)) / 255.0  # Normalize alpha to [0,1]

                # Get ROI from background
                roi = frame_chute[y_offset:y_offset+200, x_offset:x_offset+200].astype(float)

                # Blend the image with ROI using alpha mask
                blended = (img_rgb * mask + roi * (1 - mask)).astype(np.uint8)

                # Replace region in frame_chute
                frame_chute[y_offset:y_offset+200, x_offset:x_offset+200] = blended
            else:
                # No alpha channel, just paste the image directly
                frame_chute[y_offset:y_offset+200, x_offset:x_offset+200] = img3
        else:
            print(f"⚠️ Troisième image non trouvée à : {image_path3}")


        # img3 = cv2.imread(image_path3, cv2.IMREAD_UNCHANGED)

        # if img3 is not None:
        #     if img3.shape[2] == 4:
        #         r, g, b, a = cv2.split(img3)
        #         white_bg = np.ones_like(a, dtype=np.uint8) * 255
        #         b = cv2.bitwise_or(b, white_bg, mask=cv2.bitwise_not(a))
        #         g = cv2.bitwise_or(g, white_bg, mask=cv2.bitwise_not(a))
        #         r = cv2.bitwise_or(r, white_bg, mask=cv2.bitwise_not(a))
        #         img3 = cv2.merge((r, g, b))

        #     img3 = cv2.resize(img3, (200, 200))
        #     hsv3 = cv2.cvtColor(img3, cv2.COLOR_BGR2HSV)
        #     lower = np.array([0, 0, 0])
        #     upper = np.array([150, 255, 100])
        #     mask3 = cv2.inRange(hsv3, lower, upper)
        #     img3[mask3 > 0] = [0, 0, 255]  # rouge

        #     # Coller l'image en bas à droite
        #     frame_chute[-200:, -200:] = img3
        # else:
        #     print(f"⚠️ Deuxième image non trouvée à : {image_path3}")
        return frame_chute   
        
if __name__ == "__main__":
    ecran = Ecran()
    #frame = ecran.get_ecran_start()
    frame = ecran.get_ecran_chute2()

    # imshow frame


    # Option 1: Use OpenCV to display
    #cv2.namedWindow("Just Danse", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("Noms sur écran", width, height)
    cv2.namedWindow("Alerte : Chute", cv2.WINDOW_NORMAL)
    #cv2.imshow("Just Danse", frame)
    cv2.imshow("Alerte : Chute", frame)
    #cv2.imshow("image3")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #Option 2: Use matplotlib (uncomment if preferred)
    # Affichage avec matplotlib (convertir BGR -> RGB)
