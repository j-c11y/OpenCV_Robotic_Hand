#include <Adafruit_PWMServoDriver.h>

#define PCA9685_I2C_ADDR 0x40

#define THUMB_SERVO_MIN 240 // Closed - 70 deg
#define THUMB_SERVO_MAX 490 // Open   - 180 deg

int currentThumb = 100;  // Current thumb angle
int targetThumb  = 100;  // Target thumb angle

const int step = 1;

Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver(PCA9685_I2C_ADDR);

void setup() {
  Serial.begin(9600);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);

  pwm1.begin();
  pwm1.setPWMFreq(50); // 50Hz

  pwm1.setPWM(0, 0, THUMB_SERVO_MAX);
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');

    int angles[5];
    int i = 0;
    char *token = strtok((char *)data.c_str(), ",");

    while (token != NULL && i < 5) {
      angles[i] = constrain(atoi(token), 0, 180); // clamp to servo limits
      token = strtok(NULL, ",");
      i++;
    }

    targetThumb = angles[0];

    if (currentThumb < targetThumb) currentThumb += step;
    else if (currentThumb > targetThumb) currentThumb -= step;

    if (i == 5) {
      int pulse = map(currentThumb, 100, 180, THUMB_SERVO_MIN, THUMB_SERVO_MAX);
      pwm1.setPWM(0, 0, pulse);
    }
  }
}
