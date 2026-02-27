"""
RP2040 Connect Modbus RTU 온도 센서 읽기

RP2040 Connect의 Input Register 2개를 1초 주기로 읽어 출력합니다.
  - Register 0: 온도 x 100 (signed, 예: 2500 = 25.00°C)
  - Register 1: 온도 정수부 (signed, 예: 25)

사용법:
  uv run main.py              # 자동으로 COM 포트 검색
  uv run main.py --port COM5  # COM 포트 직접 지정
"""

import argparse
import ctypes
import time

from pymodbus.client import ModbusSerialClient
from serial.tools import list_ports


SLAVE_ID = 1
BAUD_RATE = 9600
REGISTER_ADDRESS = 0
REGISTER_COUNT = 2
POLL_INTERVAL = 1.0  # seconds


def to_signed16(value: int) -> int:
    """uint16 값을 signed int16으로 변환"""
    return ctypes.c_int16(value).value


def find_rp2040_port() -> str | None:
    """연결된 COM 포트 목록을 보여주고 RP2040을 자동 검색"""
    ports = list(list_ports.comports())
    if not ports:
        return None

    print("검색된 시리얼 포트:", flush=True)
    for p in ports:
        print(f"  {p.device}: {p.description}", flush=True)

    # RP2040 관련 키워드로 자동 검색
    for p in ports:
        desc = (p.description or "").lower()
        if "rp2040" in desc or "raspberry pi" in desc:
            return p.device

    # 자동 검색 실패 시 첫 번째 포트 반환
    return ports[0].device


def main():
    parser = argparse.ArgumentParser(description="RP2040 Modbus RTU 온도 읽기")
    parser.add_argument("--port", help="COM 포트 (예: COM5)")
    args = parser.parse_args()

    port = args.port or find_rp2040_port()
    if not port:
        print("시리얼 포트를 찾을 수 없습니다. --port 옵션으로 지정해주세요.")
        return

    client = ModbusSerialClient(
        port=port,
        baudrate=BAUD_RATE,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=2,
    )

    if not client.connect():
        print(f"포트 {port} 연결 실패")
        return

    print(f"연결됨: {port} (Slave ID={SLAVE_ID}, {BAUD_RATE}bps)", flush=True)
    print("Ctrl+C로 종료\n", flush=True)

    try:
        while True:
            result = client.read_input_registers(
                address=REGISTER_ADDRESS,
                count=REGISTER_COUNT,
                device_id=SLAVE_ID,
            )

            if result.isError():
                print(f"읽기 오류: {result}", flush=True)
            else:
                temp_x100 = to_signed16(result.registers[0])
                temp_int = to_signed16(result.registers[1])
                print(f"온도: {temp_x100 / 100:.2f}°C  (raw: {temp_x100}, 정수부: {temp_int})", flush=True)

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
