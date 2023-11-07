#include <M5Stack.h>


// globals
unsigned long score_left = 0;
unsigned long score_right = 0;

// timer
hw_timer_t *timer0 = NULL;  

//prototypes
void IRAM_ATTR callback1s();
void setup_M5Stack();
void setup_display();
void disp_score(unsigned long left, unsigned long right);


void setup() {
  // put your setup code here, to run once:
  setup_M5Stack();
  setup_display();
  disp_score(score_left, score_right);

  Serial.begin(115200);

  timer0 = timerBegin(0, 80, true); //timer=1us
  timerAttachInterrupt(timer0, &callback1s, true);
  timerAlarmWrite(timer0, 1000000, true); // 1000000us = 1s
  timerAlarmEnable(timer0);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0){
    unsigned short incoming_byte = Serial.read();

    Serial.print("I received: "); // 受信データを送りかえす
		Serial.println(incoming_byte);

    switch(incoming_byte){
      case 0x30:
        score_left  = 0;
        score_right = 0;
        break;

      case 0x31:
        score_left += 1;
        break;

      case 0x32:
        score_right += 1;
        break;

      default:
        break;
    }
  }

  // delay(1000);
  // score_left  += 1;
  // score_right += 1;
  // disp_score(score_left, score_right);

}

//timer callback
void IRAM_ATTR callback1s() {
  disp_score(score_left, score_right);
}

void setup_M5Stack()
{
    // M5Stack オブジェクトの初期化
    M5.begin();

}

void setup_display()
{
  M5.Lcd.setRotation(1);      // 画面向き設定（0～3で設定、4～7は反転)※初期値は1
  M5.Lcd.setTextWrap(false);  // 画面端での改行の有無（true:有り[初期値], false:無し）※print関数のみ有効

  M5.Lcd.fillScreen(BLACK);           // 画面背景(指定色で画面全体を塗りつぶす。表示を更新する場合にも使用)
  M5.Lcd.setTextColor(WHITE, BLACK); // テキスト色(文字色, 文字背景)
  M5.Lcd.setTextFont(2);              // フォント(フォント番号：0,2,4,6,7,8の中から指定)
  M5.Lcd.setCursor(0, 0);             // テキスト表示座標(x座標, y座標)
  M5.Lcd.setTextSize(4);              // テキストサイズ倍率(整数で指定)
}

void disp_score(unsigned long left, unsigned long right)
{
  M5.Lcd.clear(BLACK);
  M5.Lcd.setCursor(0, 0);             // テキスト表示座標(x座標, y座標)
  M5.Lcd.printf("Left vs Right\n\n %d - %d", score_left, score_right);
}