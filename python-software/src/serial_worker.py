def serial_worker(port, baud, q):
    import serial
    try:
        ser = serial.Serial(port, baud, timeout=1)
        import time
        time.sleep(0.15)  # allow Arduino to reset
    except Exception as e:
        print("Failed to open serial:", e)
        return

    while True:
        packet = q.get()  # wait for next packet
        if packet == "QUIT":
            break
        try:
            ser.write((packet + "\n").encode())
            time.sleep(0.002)  # tiny delay
        except Exception as e:
            print("Serial write error:", e)

    ser.close()