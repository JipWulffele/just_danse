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

        # Liste des pronoms

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
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #Option 2: Use matplotlib (uncomment if preferred)
    # Affichage avec matplotlib (convertir BGR -> RGB)
