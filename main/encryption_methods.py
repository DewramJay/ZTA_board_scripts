import pyshark

# Define encryption scores and mappings
encryption_scores = {
    'AES-256': 1.0,  # 10/10
    'AES-128': 0.9,  # 9/10
    'ChaCha20': 0.9, # 9/10
    '3DES': 0.5,     # 5/10
    'RC4': 0.2,      # 2/10
    'DES': 0.1,      # 1/10
    'MD5': 0.1,      # 1/10
    'SHA-1': 0.3,    # 3/10
    'SHA-256': 0.9,  # 9/10
    'SHA-3': 1.0     # 10/10
}

# Map common TLS cipher suite hex codes to encryption mechanisms
cipher_suite_mapping = {
    '0x1301': 'AES-256',  # TLS_AES_256_GCM_SHA384
    '0x1302': 'AES-128',  # TLS_AES_128_GCM_SHA256
    '0x1303': 'ChaCha20', # TLS_CHACHA20_POLY1305_SHA256
    '0xc02c': 'AES-256',  # TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
    '0xc02b': 'AES-128',  # TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
    '0xc00a': '3DES',     # TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA
    '0xcca8': 'ChaCha20', # TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
    '0x009c': 'AES-256',  # TLS_RSA_WITH_AES_256_GCM_SHA384
    '0x009d': 'AES-128',  # TLS_RSA_WITH_AES_128_GCM_SHA256
    # Add more mappings as needed
}

# Initialize dictionary to count occurrences of each encryption mechanism
encryption_counts = {
    'AES-256': 0,
    'AES-128': 0,
    'ChaCha20': 0,
    '3DES': 0,
    'Other/Unrecognized': 0
}

def get_encryption_mechanism(cipher_suite_hex):
    """ Get the encryption mechanism based on the cipher suite hex code. """
    return cipher_suite_mapping.get(cipher_suite_hex, 'Other/Unrecognized')

def analyze_pcap():
    pcap_file = 'packet_capture.pcap'
    """ Analyze a PCAP file for encryption mechanisms and count occurrences. """
    cap = pyshark.FileCapture(pcap_file)
    
    for pkt in cap:
        if 'tls' in pkt:
            # Analyze TLS handshake and cipher suites
            if hasattr(pkt.tls, 'handshake_ciphersuite'):
                cipher_suite = pkt.tls.handshake_ciphersuite
                encryption_mechanism = get_encryption_mechanism(cipher_suite)
                encryption_counts[encryption_mechanism] += 1

    # Print summary of encryption mechanisms
    print("\nEncryption Mechanism Summary:")
    for mechanism, count in encryption_counts.items():
        print(f"{mechanism}: {count} packets")

# Example: Analyze a captured PCAP file
# pcap_file = 'Desktop/project/eval/ZTA_main_2/main/packet_capture.pcap'  # Provide the path to your PCAP file
# analyze_pcap(pcap_file)