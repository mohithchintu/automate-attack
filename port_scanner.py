import nmap

# Initialize the Nmap scanner
scanner = nmap.PortScanner()

# Define the target website and ports to scan
target = 'cbit.ac.in'
ports = '80,443'  # Common web ports (HTTP and HTTPS)

# Perform the scan
scanner.scan(target, ports)

# Display scan results
for host in scanner.all_hosts():
    print(f"Host : {host} ({scanner[host].hostname()})")
    print(f"State : {scanner[host].state()}")
    for protocol in scanner[host].all_protocols():
        print(f"Protocol : {protocol}")
        ports = scanner[host][protocol].keys()
        for port in ports:
            print(f"Port : {port}\tState : {scanner[host][protocol][port]['state']}")
