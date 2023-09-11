'''#elbs.py

    # 笑顔をコントローラとした対戦ゲーム

    TODO:
    - ゲーム作り
        - 笑顔インターフェース入力
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
PLAYER     = 1

LOWER_THRESH_MULTIPLI_VAL = 1.5
UPPER_THRESH_MULTIPLI_VAL = 0.8


start_flag = False
game_time  = 10
calib_time = 5

face_cascade_dest  = r'C:\Users\tesum\AppData\Local\Programs\Python\Python311\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'
smile_cascade_dest = r'C:\Users\tesum\AppData\Local\Programs\Python\Python311\Lib\site-packages\cv2\data\haarcascade_smile.xml'

# インスタンス化と初期化
smile_recg = smile_recognition.smileRecognition(camera_num = CAMERA_NUM, player = PLAYER)
smile_recg.set_face_and_smile_cascade(face_cascade_dest, smile_cascade_dest)
smile_recg.camera_init()

def main_routine():
    '''main_routine
    
        ゲームのメイン関数, threadingで呼び出す
    '''
    global start_flag

    while True:
        if start_flag:
            # ---------------------------------------------------------------------------------------------------------------
            #         キャリブレーションを実行する
            # ---------------------------------------------------------------------------------------------------------------

            # 下限値のキャリブレーションを行う
            print('下限値のキャリブレーションを行います')
            time.sleep(2)
            smile_time_data, best_score_data, best_img_data = get_time_dependent_smile_data(PLAYER, calib_time)

            if PLAYER == 1:
                lower_thresh = round(sum(smile_time_data[1]) / len(smile_time_data[1]) * LOWER_THRESH_MULTIPLI_VAL)
                print('lower_thresh = ', lower_thresh)
            elif PLAYER == 2:
                lower_thresh_left  = round(sum(smile_time_data[1]) / len(smile_time_data[1]) * LOWER_THRESH_MULTIPLI_VAL)
                lower_thresh_right = round(sum(smile_time_data[2]) / len(smile_time_data[2]) * LOWER_THRESH_MULTIPLI_VAL)

            # 上限値のキャリブレーションを行う
            print('上限値のキャリブレーションを行います')
            time.sleep(2)
            smile_time_data, best_score_data, best_img_data = get_time_dependent_smile_data(PLAYER, calib_time)

            if PLAYER == 1:
                upper_thresh = round(sum(smile_time_data[1]) / len(smile_time_data[1]) * UPPER_THRESH_MULTIPLI_VAL)
                print('upper_thresh = ', upper_thresh)
            elif PLAYER == 2:
                upper_thresh_left  = round(sum(smile_time_data[1]) / len(smile_time_data[1]) * UPPER_THRESH_MULTIPLI_VAL)
                upper_thresh_right = round(sum(smile_time_data[1]) / len(smile_time_data[1]) * UPPER_THRESH_MULTIPLI_VAL)
            
            # ---------------------------------------------------------------------------------------------------------------
            #         ゲームを実行する
            # ---------------------------------------------------------------------------------------------------------------
            print('ゲームを開始します')
            time.sleep(2)

            # 判定下限値の結合
            if PLAYER == 1:
                lower_thresh_in = [lower_thresh, None]
            elif PLAYER == 2:
                lower_thresh_in = [lower_thresh_left, lower_thresh_right]
            # 判定上限値の結合
            if PLAYER == 1:
                upper_thresh_in = [upper_thresh, None]
            elif PLAYER == 2:
                upper_thresh_in = [upper_thresh_left, upper_thresh_right]

            start_time = time.time()
            smile_time_data, best_score_data, best_img_data = get_time_dependent_smile_data(PLAYER, game_time, game_mode = True, lower_thresh = lower_thresh_in, upper_thresh = upper_thresh_in)
            
            # データの保存
            dt = datetime.datetime.fromtimestamp(start_time)
            csvname = 'data/' + dt.strftime('%Y%m%d_%H%M%S') + '.csv'
            with open(csvname, 'w', newline='') as file:
                writer = csv.writer(file)
                if PLAYER == 1:
                        writer.writerow(['time[sec]', 'smile_score'])
                elif PLAYER == 2:
                    writer.writerow(['time[sec]', 'smile_score_left', 'smile_score_right'])
                for i in range(len(smile_time_data[0])):
                    if PLAYER == 1:
                        writer.writerow([smile_time_data[0][i], smile_time_data[1][i]])
                    elif PLAYER == 2:
                        writer.writerow([smile_time_data[0][i], smile_time_data[1][i], smile_time_data[2][i]])

            # 最高の笑顔画像の保存
            if PLAYER == 1:
                if best_score_data[0] != 0:
                # print('best_score', best_score)
                    imgname = 'data/' + dt.strftime('%Y%m%d_%H%M%S') + '_best.jpg'
                    cv2.imwrite(imgname, best_img_data[0])
            elif PLAYER == 2:
                if best_score_data[0] != 0:
                    imgname = 'data/' + dt.strftime('%Y%m%d_%H%M%S') + '_best_left.jpg'
                    cv2.imwrite(imgname, best_img_data[0])
                if best_score_data[1] != 0:
                    imgname = 'data/' + dt.strftime('%Y%m%d_%H%M%S') + '_best_right.jpg'
                    cv2.imwrite(imgname, best_img_data[1])
            
            start_flag = False
            print('finish')
            sys.exit()

        time.sleep(0.5)


def get_time_dependent_smile_data(player, smile_time, game_mode = False, lower_thresh = None, upper_thresh = None):
    '''get_time_dependent_smile_data
    
        時間に対する笑顔度のデータを収集する関数

    Args:
        player          , int          , 対戦人数. 1 or 2人
        smile_time      , int          , プレイ時間
        game_mode       , bool         , 対戦モードにする
        lower_thresh    , int          , 対戦モードのときの笑顔判定下限値
        upper_thresh    , int          , 対戦モードのときの笑顔判定上限値
        
    Returns:
        smile_time_data , list of list , [時間データリスト 笑顔値データリスト, 笑顔値データリスト2(2人プレイのとき)]
        best_score_data , list of int  , [最高の笑顔値1, 最高の笑顔値2(2人プレイのとき)]
        best_img_data   , list of img  , [最高の笑顔値1の画像, 最高の笑顔値2の画像(2人プレイのとき)]

    TODO: 笑顔インターフェースによる入力機能を実装
    '''
    if game_mode:
        if lower_thresh == None:
            print('lower_threshを設定してください')
            raise
        if upper_thresh == None:
            print('upper_threshを設定してください')
            raise

    # 笑顔値を初期化する
    if player == 1:
        smile_score = []
        best_score  = 0
        best_img    = None
    elif player == 2:
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
    while elapsed_time < smile_time:
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

        if player == 1:
            if smile_scores_current[0] == None:
                smile_score.append(smile_scores_prev[0])
            else:
                smile_score.append(smile_scores_current[0])
                smile_scores_prev[0] = smile_scores_current[0]
                # 最高の笑顔値と最高の笑顔画像のキャッシュ
                if best_score < smile_scores_current[0]:
                    best_img = img_raw
                    best_score = smile_scores_current[0]
        elif player == 2:
            if smile_scores_current[0] == None:
                smile_score_left.append(smile_scores_prev[0])
            # プレイヤー1の最高の笑顔値と最高の笑顔画像のキャッシュ
            else:
                smile_score_left.append(smile_scores_current[0])
                smile_scores_prev[0] = smile_scores_current[0]
                if best_score_left < smile_scores_current[0]:
                    best_img_left = img_raw[0 : smile_recg.y_res, 0 : round(smile_recg.x_res/2)]
                    best_score_left = smile_scores_current[0]
            if smile_scores_current[1] == None:
                smile_score_right.append(smile_scores_prev[1])
            # プレイヤー2の最高の笑顔値と最高の笑顔画像のキャッシュ
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

    # 返すデータを作る
    if player == 1:
        smile_time_data = [time_data, smile_score, None]
        best_score_data = [best_score, None]
        best_img_data   = [best_img, None]
    elif player == 2:
        smile_time_data = [time_data, smile_score_left, smile_score_right]
        best_score_data = [best_score_left, best_score_right]
        best_img_data   = [best_img_left, best_img_right]
    else:
        raise

    return smile_time_data, best_score_data, best_img_data

def start_calc_smile_routine_thread():
    thread = threading.Thread(target = main_routine)
    thread.daemon = True
    thread.start()



if __name__ == '__main__':
    start_flag = True
    main_routine()
