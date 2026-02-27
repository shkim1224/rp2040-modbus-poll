/*
 * RP2040 Connect - Modbus RTU Slave (온도센서)
 *
 * LSM6DSOX IMU의 온도센서 값을 Modbus RTU로 제공합니다.
 * Windows의 Modbus Poll 프로그램에서 USB COM 포트로 읽을 수 있습니다.
 *
 * ===== 필요 라이브러리 (Arduino Library Manager에서 설치) =====
 *   1. ModbusRTUSlave  (by CMB27)
 *   2. Arduino_LSM6DSOX
 *
 * ===== Modbus Poll 설정 =====
 *   Connection Setup (F3):
 *     - Connection : Serial Port
 *     - Port       : COMx (장치관리자에서 확인)
 *     - Baud Rate  : 9600
 *     - Data Bits  : 8
 *     - Stop Bits  : 1
 *     - Parity     : None
 *     - Mode       : RTU
 *
 *   Read/Write Definition (F8):
 *     - Slave ID   : 1
 *     - Function   : 04 Read Input Registers
 *     - Address    : 0
 *     - Quantity   : 2
 *     - Scan Rate  : 1000 ms
 *
 * ===== 레지스터 맵 =====
 *   Input Register 0 : 온도 x 100 (예: 2543 = 25.43°C)  [signed]
 *   Input Register 1 : 온도 정수부 (예: 25)               [signed]
 */

#include <ModbusRTUSlave.h>
#include <Arduino_LSM6DSOX.h>

// ----- 설정값 -----
const uint8_t  SLAVE_ID            = 1;
const uint32_t BAUD_RATE           = 9600;
const uint32_t TEMP_READ_INTERVAL  = 1000;  // 온도 읽기 주기 (ms)

// ----- Modbus 레지스터 -----
const uint8_t NUM_INPUT_REGS = 2;
uint16_t inputRegisters[NUM_INPUT_REGS];

ModbusRTUSlave modbus(Serial);

unsigned long lastTempRead = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  // USB Serial 연결 대기 (최대 3초)
  Serial.begin(BAUD_RATE);
  unsigned long waitStart = millis();
  while (!Serial && (millis() - waitStart < 3000)) {
    delay(10);
  }

  // IMU 초기화
  if (!IMU.begin()) {
    // IMU 초기화 실패 시 LED 깜빡임으로 알림
    while (1) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(200);
      digitalWrite(LED_BUILTIN, LOW);
      delay(200);
    }
  }

  // Modbus Input Register 설정 (읽기 전용)
  modbus.configureInputRegisters(inputRegisters, NUM_INPUT_REGS);

  // Modbus 시작 (Slave ID, Baud Rate, 8N1)
  modbus.begin(SLAVE_ID, BAUD_RATE, SERIAL_8N1);

  // 초기 온도 읽기
  int temperature = 0;
  IMU.readTemperature(temperature);
  inputRegisters[0] = (uint16_t)((int16_t)(temperature * 100));
  inputRegisters[1] = (uint16_t)((int16_t)temperature);
}

void loop() {
  // 주기적으로 온도 갱신
  unsigned long now = millis();
  if (now - lastTempRead >= TEMP_READ_INTERVAL) {
    lastTempRead = now;

    int temperature = 0;
    if (IMU.temperatureAvailable()) {
      IMU.readTemperature(temperature);
      // Register 0: 온도 x 100 (정수값이므로 예: 25 -> 2500)
      inputRegisters[0] = (uint16_t)((int16_t)(temperature * 100));
      // Register 1: 온도 정수값 (예: 25)
      inputRegisters[1] = (uint16_t)((int16_t)temperature);
    }
  }

  // Modbus 요청 처리
  modbus.poll();
}
