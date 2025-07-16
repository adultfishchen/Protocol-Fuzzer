from boofuzz import *
#from boofuzz.connections import TCPSocketConnection
import time
import datetime

def fuzz_protocol(protocol):
    ip = "Your_IP" 
    ports = {
        'rtsp': 554,
        'tls': 443,
        'http': 8080
    }
    
    if protocol not in ports:
        print("Unsupported protocol")
        return
        
    # Create unique timestamp for database filename
    unique_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    db_filename = f"./boofuzz-results/{protocol}_{unique_timestamp}.db"
    
    connection = SocketConnection(ip, ports[protocol], proto='tcp')
    #connection = TCPSocketConnection(ip, ports[protocol])

    
    session = Session(
        target=Target(
            connection=connection
        ),
        db_filename=db_filename,  # 正確設置 db_filename
        sleep_time=0.288,  # 控制测试用例之间的间隔
    )  



    max_duration = 8 * 60 * 60  # 8 hours in seconds
    start_time = time.time()

    for i in range(100000):  # Generate 100,000 test cases
        if time.time() - start_time > max_duration:
            print("Reached the maximum allowed duration for fuzzing.")
            break
        
        s_initialize(f"{protocol}_Request_{i}")

        if protocol == 'tls':
            with s_block("Handshake"):
                s_string("\x16", name='HandshakeType-ClientHello', fuzzable=False)
                s_group("TLS_Version", values=["0301", "0302", "0303", "0304"])
                s_random(value='', min_length=32, max_length=32, name='Random')
                s_group("Cipher_Suite", values=["1301", "1302", "1303", "c02b", "c02f", "cca9", "cca8", "009c", "009d", "002f", "0035", "c013", "c014"])
                s_byte(value=1, name="Compression_Method", fuzzable=True)

        elif protocol == 'rtsp':
            with s_block("Request-Line"):
                s_string('DESCRIBE', name='Method')
                s_delim(" ", name='space-1')
                s_string("rtsp://ACCOUNT:PASSWORD@YOUR_IP_ADDRESS/live/profile.0", name='Request-URI')
                s_delim(" ", name='space-2')
                s_string('RTSP/1.0', name='RTSP-Version')
                s_static("\r\n", name="Request-Line-CRLF")
            s_static("\r\n", "Request-CRLF")
            
        elif protocol == 'http':
            with s_block("Request-Line"):
                s_string("GET", name="Method")
                s_delim(" ", name="space-1")
                s_string("/index.html", name="Request-URI")
                s_delim(" ", name="space-2")
                s_string("HTTP/1.1", name="HTTP-Version")
                s_static("\r\n", name="Request-Line-CRLF")
                s_string("Host:", name="Host Header")
                s_delim(" ", name="space-3")
                s_string("YOUR_IP_ADDRESS", name="Host IP")
                s_static("\r\n\r\n", name="End Headers")
                
        session.connect(s_get(f"{protocol}_Request_{i}"))
        session.fuzz()

def main():
    print("Please select the protocol type for fuzz testing:")
    protocols = ['rtsp', 'tls','http']
    for idx, protocol in enumerate(protocols, 1):
        print(f"{idx}. {protocol}")

    choice = input("Enter the number of the protocol type you want to test:")
    protocol = protocols[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(protocols) else None
    if protocol:
        fuzz_protocol(protocol)
    else:
        print("Invalid selection")

if __name__ == "__main__":
    main()

