'''# smile_recognition

   カメラ画像から笑顔を認識し, 笑顔度に変換するモジュールプログラム\n

'''

import cv2

class smileRecognition():
    '''smileRecognition

        カメラ画像から笑顔を認識し, 笑顔度に変換するクラス\n
        
    '''
    face_cascade_dest  = r'C:\Users\tesum\AppData\Local\Programs\Python\Python39\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'
    smile_cascade_dest = r'C:\Users\tesum\AppData\Local\Programs\Python\Python39\Lib\site-packages\cv2\data\haarcascade_smile.xml'
    face_size_px = 80

    def __init__(self, camera_num = 0, player = 2, x_res = 640, y_res = 480):
        '''__init__

            コンストラクタ\n

        Args:
            camera_num  ,  int  , カメラ番号  0 -> PCカメラ, 1 -> USBカメラ\n
            player      ,  int  , 対戦人数  2人 or 1人
            x_res       ,  int  , カメラ画像のx軸解像度\n
            y_res       ,  int  , カメラ画像のy軸解像度

        Return:
            None
        '''
        
        self.camera_num = camera_num
        self.player = player
        self.x_res = x_res
        self.y_res = y_res

    def set_face_and_smile_cascade(self, face_cascade_dest, smile_cascade_dest):
        '''set_face_and_smile_cascade
        
            顔検出器, 笑顔検出器のパスのsetter\n
            cameta_initメソッドの前に実行する\n

        Args:
            face_cascade_dest , string  , haarcascade_frontalface_default.xmlの絶対パス\n
            smile_cascade_dest, string  , haarcascade_smile.xmlの絶対パス

        Return:
            None
        '''
        self.face_cascade_dest = face_cascade_dest
        self.smile_cascade_dest = smile_cascade_dest

    def camera_init(self):
        '''camera_init

            カメラ画像をキャプチャできるようにする\n
            顔, 笑顔検出器をインスタンス化する

        Arg: 
            None
        Return:
            None
        '''
        self.capture = cv2.VideoCapture(self.camera_num)
        self.capture.set(3, self.x_res)
        self.capture.set(4, self.y_res)
        self.face_cascade = cv2.CascadeClassifier(self.face_cascade_dest)
        self.smile_cascade = cv2.CascadeClassifier(self.smile_cascade_dest)

    def get_faces_from_camera(self):
        '''get_faces_from_camera
        
            カメラ画像を一枚撮像し, その画像から顔を検出する\n
        
        Arg: 
            None
        Returns:
            faces          , list of ? , 顔が検出された画像リスト
            img            , image     , 1枚のカメラ画像
        '''
        ret, img = self.capture.read()
        img = cv2.flip(img,1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100,100))

        return faces, img
    
    def show_image(self, img):
        '''show_image
        
            カメラ画像を表示する
        '''
        if self.player == 2:
            cv2.line(img, (round(self.x_res/2), 0), (round(self.x_res/2), self.y_res), (0, 255, 0), thickness=8)

        cv2.imshow('img',img)
        # key Operation
        key = cv2.waitKey(5) 
        
        return key

    def filter_faces(self, faces):
        '''filter_faces
        
            検出した顔のリストをフィルタする

        Args:
            faces      , list of [x,y,w,h] , 検出された顔のx,y,w,hのリスト
        Returns
            filt_faces , tuple of (x,y,w,h), フィルタ後の顔のx,y,w,hのリスト
        '''
        # 2人対戦の時
        if self.player == 2:
            left_w_max  = 0
            left_h_max  = 0
            left_x_max  = 0
            left_y_max  = 0
            right_w_max = 0
            right_h_max = 0
            right_x_max = 0
            right_y_max = 0

            for (x,y,w,h) in faces:
                # 画像の半分より左側の顔について
                if x < (self.x_res/2):
                    # 顔の大きさが一定以上, かつ最大の大きさの顔を登録する
                    if w > self.face_size_px and w > left_w_max and h > self.face_size_px and h > left_h_max:
                        left_x_max = x
                        left_y_max = y
                        left_w_max = w
                        left_h_max = h
                # 画像の半分より右側の顔について
                else:
                    # 顔の大きさが一定以上, かつ最大の大きさの顔を登録する
                    if w > self.face_size_px and w > right_w_max and h > self.face_size_px and h > right_h_max:
                        right_x_max = x
                        right_y_max = y
                        right_w_max = w
                        right_h_max = h
                
            # 画像中央より左側と右側のそれぞれ最大の顔を返す
            filt_faces = [(left_x_max, left_y_max, left_w_max, left_h_max), (right_x_max, right_y_max, right_w_max, right_h_max)]
        
        # 1人の時
        else:
            w_max  = 0
            h_max  = 0
            x_max  = 0
            y_max  = 0

            for (x,y,w,h) in faces:
                # 顔の大きさが一定以上, かつ最大の大きさの顔を登録する
                if w > self.face_size_px and w > w_max and h > self.face_size_px and h > h_max:
                    x_max = x
                    y_max = y
                    w_max = w
                    h_max = h
            
            # 画像中の最大の顔を返す
            filt_faces = [(x_max, y_max, w_max, h_max)]

        return filt_faces
            

    def get_smile_score(self, faces, img, check_mid_image = False, normalize_brightness = True):
        '''get_smile_score
        
            入力した顔検出画像リストから, 顔の笑顔スコアを算出する\n
        
        Arg: 
            faces          , list of ?   , 顔が検出された画像リスト
            img            , image       , 1枚のカメラ画像
            check_mid_image, boolean     , Trueにすると検出し規格化された顔画像を表示する
        Returns:
            img            , ?           , 検出した顔のrectangleが付加されたカメラ画像
            smile_scores   , list of int , 
        '''
        smile_scores = [None, None]

        for i, (x,y,w,h) in enumerate(faces):
            if x == 0:
                continue
            # ------------------------------------------------------------------------------------------------------
            #                 顔領域の切り出しと規格化
            # ------------------------------------------------------------------------------------------------------
            # 検出した顔の領域のrectangleを作る 
            cv2.rectangle(img, (x,y), (x + w,y + h), (255, 0, 0) , 2) # blue
            #Gray画像から，顔領域を切り出す．
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            roi_gray = gray[y : y + h, x : x + w] 

            # 切り出した顔領域を100 x 100に規格化
            roi_gray = cv2.resize(roi_gray,(100,100))

            # 顔領域の輝度を規格化
            if normalize_brightness:
                lmin = roi_gray.min()
                lmax = roi_gray.max()
                for index1, item1 in enumerate(roi_gray):
                    for index2, item2 in enumerate(item1) :
                        roi_gray[index1][index2] = int((item2 - lmin)/(lmax-lmin) * item2)


            #確認のため輝度を正規化した画像を表示
            if check_mid_image:
                cv2.imshow("roi_gray2", roi_gray)

            # --------------------------------------------------------------------------------------------------------
            #                     顔領域の切り出しと規格化
            # --------------------------------------------------------------------------------------------------------
            #笑顔識別
            smiles= self.smile_cascade.detectMultiScale(roi_gray, scaleFactor= 1.1, minNeighbors=0, minSize=(20, 20))

            # 笑顔が検出された場合
            if len(smiles) > 0:
                # smile_neighbors が笑顔度に相当する
                smile_neighbors = len(smiles)

                # 検出した笑顔の場所を, 画像上で赤サークルで示す
                LV = 2/100
                intensityZeroOne = smile_neighbors  * LV 
                if intensityZeroOne > 1.0: intensityZeroOne = 1.0 
                for(sx,sy,sw,sh) in smiles:
                    cv2.circle(img,(int(x+(sx+sw/2)*w/100),int(y+(sy+sh/2)*h/100)),int(sw/2*w/100), (255*(1.0-intensityZeroOne), 0, 255*intensityZeroOne),2)

                smile_scores[i] = smile_neighbors

        return img, smile_scores

        