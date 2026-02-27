"""
RP2040 Connect Modbus RTU 온도 센서 읽기 + SQLite 저장

RP2040 Connect의 Input Register 2개를 1초 주기로 읽어
SQLite DB(shkimdb.db)의 sensor 테이블에 저장합니다.
  - temp1: 온도 x 100 (signed, 예: 3600 = 36.00°C)
  - temp2: 온도 정수부 (signed, 예: 36)

사용법:
  uv run sqlite-modbus.py              # COM 포트 자동 검색
  uv run sqlite-modbus.py --port COM22 # COM 포트 직접 지정
"""

import argparse
import ctypes
import sqlite3
import time
from datetime import datetime

from pymodbus.client import ModbusSerialClient
from serial.tools import list_ports

SLAVE_ID = 1
BAUD_RATE = 9600
REGISTER_ADDRESS = 0
REGISTER_COUNT = 2
POLL_INTERVAL = 1.0  # seconds
DB_NAME = "shkimdb.db"


def to_signed16(value: int) -> int:
    return ctypes.c_int16(value).value


def find_rp2040_port() -> str | None:
    ports = list(list_ports.comports())
    if not ports:
        return None

    print("검색된 시리얼 포트:", flush=True)
    for p in ports:
        print(f"  {p.device}: {p.description}", flush=True)

    for p in ports:
        desc = (p.description or "").lower()
        if "rp2040" in desc or "raspberry pi" in desc or "usb" in desc:
            return p.device

    return ports[0].device


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temp1 INTEGER NOT NULL,
            temp2 INTEGER NOT NULL
        )
    """)
    conn.commit()
    return conn


def main():
    parser = argparse.ArgumentParser(description="RP2040 Modbus RTU 온도 읽기 + SQLite 저장")
    parser.add_argument("--port", help="COM 포트 (예: COM22)")
    args = parser.parse_args()

    port = args.port or find_rp2040_port()
    if not port:
        print("시리얼 포트를 찾을 수 없습니다. --port 옵션으로 지정해주세요.")
        return

    conn = init_db()
    print(f"DB 준비 완료: {DB_NAME} (sensor 테이블)", flush=True)

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
        conn.close()
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
                temp1 = to_signed16(result.registers[0])
                temp2 = to_signed16(result.registers[1])
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                conn.execute(
                    "INSERT INTO sensor (timestamp, temp1, temp2) VALUES (?, ?, ?)",
                    (now, temp1, temp2),
                )
                conn.commit()

                print(f"[{now}] temp1={temp1}, temp2={temp2}  ({temp1 / 100:.2f}°C)  -> DB 저장", flush=True)

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        client.close()
        conn.close()
        print("DB 및 시리얼 연결 종료")


if __name__ == "__main__":
    main()
