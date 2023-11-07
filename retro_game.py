import serial
import time

class retroGame():
    '''# retroGame

        レトロゲームと通信するクラス

    Attrs:
        port      , String  , レトロゲームのポート名\n
        baud_rate , int     , レトロゲームとのシリアル通信ボーレート\n

    '''

    def __init__(self, port, baud_rate = 115200, timeout = 1, debug_mode = False):
        self.port       = port
        self.baud_rate  = baud_rate
        self.timeout    = timeout
        self.debug_mode = debug_mode
        self.retry_num  = 3

    def connect(self):
        '''# connect
        
            指定のポートを開くメソッド
        '''
        if self.debug_mode:
            print('debug_mode: ' +str(self.port) + ' connected!')
        else:
            try:
                self.target = serial.Serial(self.port, self.baud_rate, timeout = self.timeout)
                print(str(self.port) + ' connected!')
            except Exception as e:
                print(e)
                raise

    def disconnect(self):
        '''# disconnect

            指定のポートを閉じるメソッド

        '''
        if self.debug_mode:
            print('debug_mode: ' +str(self.port) + ' disconnected!')
        else:
            try:
                self.target.close()
                print(str(self.port) + ' disconnected!')
            except Exception as e:
                print(e)
                raise

    def reset_buffer(self):
        '''# reset_buffer
           
            シリアルバッファを消去するメソッド
        
        '''
        if self.debug_mode:
            print('debug_mode: ' +str(self.port) + ' reset input buffer')
        else:
            try:
                self.target.reset_input_buffer()
                self.target.flush()
                print(str(self.port) + ' reset input buffer')
            except Exception as e:
                print(e)
                # raise


    def send_8bit_data(self, data_8bit):
        '''# send_bpm

            レトロゲームへ8ビットデータを送信する関数

        Args:
            data_8bit, int   , 送信するデータ\n
        '''
        data_tobe_send = [data_8bit & 0xff]
        if self.debug_mode:
            print('debug mode: write -> ' + str(data_tobe_send))
        else:
            try:
                self.target.write(data_tobe_send)
                # print('send_8bit_data', format(data_tobe_send[0], 'x'))
            except:
                pass

if __name__ == '__main__':

    port = "COM5"
    myDevice = retroGame(port)
    myDevice.connect()

    myDevice.send_8bit_data(0x31)

    time.sleep(5)

    myDevice.send_8bit_data(0x32)

    time.sleep(5)

    myDevice.disconnect()