import struct
import socket
import time
import select

def checksum(bits):
    '''Checksum function to help create packet header'''
    x = sum(x << 8 if i % 2 else x for i, x in enumerate(bits)) & 0xFFFFFFFF
    x = (x >> 16) + (x & 0xFFFF)
    x = (x >> 16) + (x & 0xFFFF)
    return struct.pack('<H', ~x & 0xFFFF)

def ping(address):
        '''Pings given address one time, returns time between sending icmp packet and recieving response if response recieved'''
        package = b'' #data to send in ping packet
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) #create socket
        message = struct.pack('!HH', 77, 3) + package

        my_socket.connect((address, 42))
        my_socket.sendall(b'\x08\0' + checksum(b'\x08\0\0\0' + message) + message) #type set to 8, code set to 0, send icmp packet
        start = time.time() #start timer

        while select.select([my_socket], [], [], max(0, 1 + start - time.time()))[0]: #wait 1 sec for response
            package = my_socket.recv(1024) #recieve response
            return time.time() - start #end timer, return ping time

def pings(target, count):
    '''executes count number of pings to target address about 1 sec apart, prints ping and package loss stats'''
    #execute pings
    total_pings = count
    fails = 0
    total_time = 0
    high_ping = -.1
    low_ping = 1.1
    for x in range(total_pings):
        ping_time = ping(target)
        if not ping_time:
            fails += 1
        else:
            total_time += ping_time
            if ping_time < low_ping:
                low_ping = ping_time
            if ping_time > high_ping:
                high_ping = ping_time
        time.sleep(.9) #to send pings ~1 sec apart

    #display ping and package loss statistics
    print()
    print(str(total_pings) + " ping attempts to "+target+":")
    print(str(fails) + " out of " + str(total_pings) + " packets were lost.")
    if ((total_pings - fails) != 0):
        average_time = total_time / (total_pings - fails)
        print("Average ping took " + str(average_time*1000) + " milliseconds.")
        print("Longest ping took " + str(high_ping*1000) + " milliseconds.")
        print("Shortest ping took " + str(low_ping*1000) + " milliseconds.")
    else:
        print("No statistical summary because no pings were successful.")

def user_input():
    '''allows terminal user to choose address to ping and number of pings'''
    address = input("Enter address to ping: ")
    while True:
        num_pings = input("Enter number of pings to send: ")
        if num_pings.isdigit(): #make sure number of pings is a positive integer
            if num_pings != "0":
                break
        print("Invalid input, please try again.")
    pings(address, int(num_pings)) #execute pings based on user input

if __name__ == '__main__':
    user_input()
