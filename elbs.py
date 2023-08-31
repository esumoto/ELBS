'''#elbs.py

    # 笑顔をコントローラとした対戦ゲーム

    NOTE:
        - 笑顔の数値化機能を実装
        - プレイヤー数2人に対応
    TODO:
        - 笑顔の閾値(笑顔判定機能)
        - 笑顔の最大値の画像の保存機能
        - CSV出力機能
        - ゲーム作り
            - キャリブレーションステップ
            - 一定時間の対戦ステップ
            - 対戦後の結果出力
            - GUI
'''

import threading

import smile_recognition


CAMERA_NUM = 1
PLAYER     = 2

def main_routine():
    '''main_routine
    
        笑顔値を計算するメイン関数\n
        threadingで呼び出す
    '''
    smile_recg = smile_recognition.smileRecognition(camera_num = CAMERA_NUM, player = PLAYER)
    smile_recg.camera_init()

    while True:
        # カメラ画像から顔を検出する
        faces, img = smile_recg.get_faces_from_camera()
        
        # 顔が検出されたとき
        if len(faces) > 0:
            # プレーヤーの数によって, 検出した顔をフィルターする
            filt_faces = smile_recg.filter_faces(faces)

            # 笑顔値を得る, &認識部分を画像に付与する
            img, smile_scores = smile_recg.get_smile_score(filt_faces, img)

            print(smile_scores)

        # 画像を表示する
        key = smile_recg.show_image(img)
        if key ==27 or key ==ord('q'): #escまたはeキーで終了
            break


if __name__ == '__main__':
    main_routine()