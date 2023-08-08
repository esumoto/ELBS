# https://qiita.com/fujino-fpu/items/99ce52950f4554fbc17d
import cv2

capture = cv2.VideoCapture(0)
capture.set(3,640)# 320 320 640 720
capture.set(4,360)#180 240  360 405

# NOTE: cv2の場所を絶対パスで指定
face_cascade = cv2.CascadeClassifier(r'C:\Users\tesum\AppData\Local\Programs\Python\Python39\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier(r'C:\Users\tesum\AppData\Local\Programs\Python\Python39\Lib\site-packages\cv2\data\haarcascade_smile.xml')

while True:
        ret, img = capture.read()
        img = cv2.flip(img,1)#鏡表示にするため．
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        for (x,y,w,h) in faces:
                cv2.circle(img,(int(x+w/2),int(y+h/2)),int(w/2),(255, 0, 0),2) # blue

                roi_gray = gray[y:y+h, x:x+w] #Gray画像から，顔領域を切り出す．
                smiles= smile_cascade.detectMultiScale(roi_gray,scaleFactor= 1.2, minNeighbors=10, minSize=(30, 30))#笑顔識別
                if len(smiles) >0 :
                        for(sx,sy,sw,sh) in smiles:
                                cv2.circle(img,(int(x+sx+sw/2),int(y+sy+sh/2)),int(sw/2),(0, 0, 255),2)#red

        cv2.imshow('img',img)
        # key Operation
        key = cv2.waitKey(5) 
        if key ==27 or key ==ord('q'): #escまたはeキーで終了
                break
capture.release()
cv2.destroyAllWindows()
print("Exit")    
