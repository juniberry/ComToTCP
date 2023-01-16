# ComToTCP.py
#
# An uncomplicated, reliable, multithreaded Serial Comm port to TCP server script with error handling.
# digitaljackalope@github
# Nov-2022

import serial
import socket
import threading
import time
import sys
import signal

# Serial port settings
COM_PORT = '/dev/ttyUSB0'
#COM_PORT = 'COM1'
BAUD_RATE = 115200
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS
STOP_BITS = serial.STOPBITS_ONE
FLOW_CONTROL_HW = False
FLOW_CONTROL_XONOFF = False

# TCP bind address and port
BIND_ADDRESS = '0.0.0.0'
BIND_PORT = 6969
# nice

# Handle ctrl+c and other signals
def signal_handler(signum, frame):
    print('Exiting...')
    sys.exit(0)

# Handle incoming data from serial port
def serial_to_tcp(tcp_client):
    while True:
        data = ser.read(1)
        if not data:
            break
        tcp_client.sendall(data)

# Handle incoming data from TCP connection
def tcp_to_serial(tcp_client):
    while True:
        data = tcp_client.recv(1)
        if not data:
            break
        ser.write(data)

# Handle new TCP connections
def handle_tcp_client(tcp_client, client_address):
    print('New connection from {}'.format(client_address[0]))
    try:
        # Start separate threads to handle data in both directions
        serial_to_tcp_thread = threading.Thread(target=serial_to_tcp, args=(tcp_client,))
        serial_to_tcp_thread.start()
        tcp_to_serial_thread = threading.Thread(target=tcp_to_serial, args=(tcp_client,))
        tcp_to_serial_thread.start()
    except Exception as e:
        print('Exception: {}'.format(e))
    finally:
        # Clean up threads and TCP connection when client disconnects
        serial_to_tcp_thread.join()
        tcp_to_serial_thread.join()
        tcp_client.close()
        print('Connection from {} closed'.format(client_address[0]))

# Goodies go here..
def main():
    # Print settings to console
    print('COM port: {}'.format(COM_PORT))
    print('Baud rate: {}'.format(BAUD_RATE))
    print('Byte Size: {}'.format(BYTE_SIZE))
    print('Parity: {}'.format(PARITY))
    print('Stop Bits: {}'.format(STOP_BITS))
    print('Flow control Hardware: {}'.format(FLOW_CONTROL_HW))
    print('Flow control XON/XOFF: {}'.format(FLOW_CONTROL_XONOFF))
    print('Bind address: {}'.format(BIND_ADDRESS))
    print('Bind port: {}'.format(BIND_PORT))

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Open serial port
    try:
        global ser
        ser = serial.Serial(COM_PORT, BAUD_RATE, bytesize=BYTE_SIZE, parity=PARITY, stopbits=STOP_BITS, xonxoff=FLOW_CONTROL_XONOFF, rtscts=FLOW_CONTROL_HW)
    except Exception as e:
        print('Error opening serial port: {}'.format(e))
        sys.exit(1)

    # Create TCP socket
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.bind((BIND_ADDRESS, BIND_PORT))
        tcp_socket.listen()
    except Exception as e:
        print('Error creating TCP socket: {}'.format(e))
        sys.exit(1)

    # Handle connections
    try:
        while True:
            # Accept new TCP connections
            tcp_client, client_address = tcp_socket.accept()
            handle_tcp_client_thread = threading.Thread(target=handle_tcp_client, args=(tcp_client, client_address))
            handle_tcp_client_thread.start()
    except KeyboardInterrupt:
        print('Exiting...')
    except Exception as e:
        print('Exception: {}'.format(e))
    finally:
        # Close serial port and TCP socket
        ser.close()
        tcp_socket.close()

if __name__ == '__main__':
    main()
