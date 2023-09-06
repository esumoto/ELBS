'''#elbs.py

    # 笑顔をコントローラとした対戦ゲーム

    NOTE:
        - 笑顔の数値化機能を実装
        - プレイヤー数2人に対応
        - 笑顔の最大値の画像の保存機能
        - CSV出力機能
    TODO:
        - 笑顔の閾値(笑顔判定機能)

        - ゲーム作り
            - キャリブレーションステップ
            - 一定時間の対戦ステップ
            - 対戦後の結果出力
            - GUI
'''
import time, datetime
import threading
import csv
import sys
import cv2

import smile_recognition


CAMERA_NUM = 0 # 0 -> on board , 1 -> external USB camera
PLAYER     = 2


start_flag = True
calc_smile_time = 20

face_cascade_dest  = r'C:\Users\tesum\AppData\Local\Programs\Python\Python39\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'
smile_cascade_dest = r'C:\Users\tesum\AppData\Local\Programs\Python\Python39\Lib\site-packages\cv2\data\haarcascade_smile.xml'

def calc_smile_routine():
    '''calc_smile_routine
    
        笑顔値を計算するメイン関数\n
        threadingで呼び出す
    '''
    global start_flag
    smile_recg = smile_recognition.smileRecognition(camera_num = CAMERA_NUM, player = PLAYER)

    smile_recg.set_face_and_smile_cascade(face_cascade_dest, smile_cascade_dest)
    smile_recg.camera_init()

    while True:
        if start_flag:
            print('start')

            # 笑顔値を初期化する
            if PLAYER == 1:
                smile_score = []
                best_score  = 0
                best_img    = None
            elif PLAYER == 2:
                smile_score_left  = []
                smile_score_right = []
                best_score_left   = 0
                best_score_right  = 0
                best_img_left     = None
                best_img_right    = None
            time_data = []
            smile_scores_prev = [0, 0]
            
            # 開始時間を得る
            start_time = time.time()
            elapsed_time = 0
            while elapsed_time < calc_smile_time:
                elapsed_time = time.time() - start_time
                time_data.append(elapsed_time)

                smile_scores_current = [None, None]

                # カメラ画像から顔を検出する
                faces, img = smile_recg.get_faces_from_camera()
                img_raw = img.copy()
                
                # 顔が検出されたとき
                if len(faces) > 0:
                    # プレーヤーの数によって, 検出した顔をフィルターする
                    filt_faces = smile_recg.filter_faces(faces)

                    # 笑顔値を得る, &認識部分を画像に付与する
                    img, smile_scores_current = smile_recg.get_smile_score(filt_faces, img)

                if PLAYER == 1:
                    if smile_scores_current[0] == None:
                        smile_score.append(smile_scores_prev[0])
                    else:
                        smile_score.append(smile_scores_current[0])
                        smile_scores_prev[0] = smile_scores_current[0]
                        if best_score < smile_scores_current[0]:
                            best_img = img_raw
                            best_score = smile_scores_current[0]
                elif PLAYER == 2:
                    if smile_scores_current[0] == None:
                        smile_score_left.append(smile_scores_prev[0])
                    else:
                        smile_score_left.append(smile_scores_current[0])
                        smile_scores_prev[0] = smile_scores_current[0]
                        if best_score_left < smile_scores_current[0]:
                            best_img_left = img_raw[0 : smile_recg.y_res, 0 : round(smile_recg.x_res/2)]
                            best_score_left = smile_scores_current[0]
                    if smile_scores_current[1] == None:
                        smile_score_right.append(smile_scores_prev[1])
                    else:
                        smile_score_right.append(smile_scores_current[1])
                        smile_scores_prev[1] = smile_scores_current[1]
                        if best_score_right < smile_scores_current[1]:
                            best_img_right = img_raw[0 : smile_recg.y_res, round(smile_recg.x_res/2) : smile_recg.x_res]
                            best_score_right = smile_scores_current[1]
                # print(smile_scores)

                # 画像を表示する
                key = smile_recg.show_image(img)
                if key ==27 or key ==ord('q'): #escまたはeキーで終了
                    start_flag = False
                    break
            print('stop')
            
            dt = datetime.datetime.fromtimestamp(start_time)
            csvname = 'data/' + dt.strftime('%Y%m%d_%H%M%S') + '.csv'
            with open(csvname, 'w', newline='') as file:
                writer = csv.writer(file)
                if PLAYER == 1:
                        writer.writerow(['time[sec]', 'smile_score'])
                elif PLAYER == 2:
                    writer.writerow(['time[sec]', 'smile_score_left', 'smile_score_right'])
                for i in range(len(time_data)):
                    if PLAYER == 1:
                        writer.writerow([time_data[i], smile_score[i]])
                    elif PLAYER == 2:
                        writer.writerow([time_data[i], smile_score_left[i], smile_score_right[i]])

            if PLAYER == 1:
                if best_score != 0:
                # print('best_score', best_score)
                    imgname = 'data/' + dt.strftime('%Y%m%d_%H%M%S') + '_best.jpg'
                    cv2.imwrite(imgname, best_img)
            elif PLAYER == 2:
                if best_score_left != 0:
                    imgname = 'data/' + dt.strftime('%Y%m%d_%H%M%S') + '_best_left.jpg'
                    cv2.imwrite(imgname, best_img_left)
                if best_score_right != 0:
                    imgname = 'data/' + dt.strftime('%Y%m%d_%H%M%S') + '_best_right.jpg'
                    cv2.imwrite(imgname, best_img_right)
            
            start_flag = False
            print('finish')
            sys.exit()


def start_calc_smile_routine_thread():
    thread = threading.Thread(target = calc_smile_routine)
    thread.daemon = True
    thread.start()



if __name__ == '__main__':
    calc_smile_routine()
