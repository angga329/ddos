#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                     DRGXEL FILE UNLOCKER v1.0                             ║
║                         Professional Edition                              ║
║                                                                           ║
║                          Created by: Axel                                 ║
║                    From: Dexel Scripter Team                              ║
║                                                                           ║
║                    [ FILE DECRYPTION TOOL ]                               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

CUSTOMER TOOL - File Unlock System with Usage Tracking
"""

import os
import sys
import json
import hashlib
import uuid
import platform
from base64 import b64decode
from datetime import datetime


class ColorCode:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


class DrgXelUnlocker:
    """File Unlocker with Usage Limit Tracking"""
    
    def __init__(self):
        self.version = "1.0"
        self.show_banner()
    
    def show_banner(self):
        banner = f"""
{ColorCode.CYAN}╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  ██████╗ ██████╗  ██████╗ ██╗  ██╗███████╗██╗                            ║
║  ██╔══██╗██╔══██╗██╔════╝ ██║ ██╔╝██╔════╝██║                            ║
║  ██║  ██║██████╔╝██║  ███╗█████╔╝ █████╗  ██║                            ║
║  ██║  ██║██╔══██╗██║   ██║██╔═██╗ ██╔══╝  ██║                            ║
║  ██████╔╝██║  ██║╚██████╔╝██║  ██╗███████╗███████╗                       ║
║  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝                       ║
║                                                                           ║
║                        ═══ FILE UNLOCKER v1.0 ═══                        ║
║                                                                           ║
║                          {ColorCode.GREEN}Created by: Axel{ColorCode.CYAN}                              ║
║                        {ColorCode.GREEN}Team: Dexel Scripter Team{ColorCode.CYAN}                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝{ColorCode.END}
"""
        print(banner)
    
    def get_hardware_id(self):
        """Get Hardware ID"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
            system = platform.system()
            machine = platform.machine()
            hw_string = f"{mac}|{system}|{machine}"
            hw_id = hashlib.sha256(hw_string.encode()).hexdigest()[:16].upper()
            return hw_id
        except:
            return "GENERIC-HARDWARE"
    
    def multi_layer_decrypt(self, data, key):
        if isinstance(key, str):
            key = key.encode()
        
        # Reverse Layer 5: Un-shuffle
        layer4 = bytearray(data)
        key_sum = sum(key) % 256
        indices = list(range(len(layer4) - 1))[::-1]
        for i in indices:
            j = (i + key_sum) % len(layer4)
            layer4[i], layer4[j] = layer4[j], layer4[i]
        layer4 = bytes(layer4)
        
        # Reverse Layer 4
        rotated_key = key[len(key)//2:] + key[:len(key)//2]
        expanded_key2 = (rotated_key * (len(layer4) // len(rotated_key) + 1))[:len(layer4)]
        layer3 = bytes([d ^ k for d, k in zip(layer4, expanded_key2)])
        
        # Reverse Layer 3
        layer2 = layer3[::-1]
        
        # Reverse Layer 2
        layer1 = bytes([(b - 137) % 256 for b in layer2])
        
        # Reverse Layer 1
        expanded_key = (key * (len(layer1) // len(key) + 1))[:len(layer1)]
        original = bytes([d ^ k for d, k in zip(layer1, expanded_key)])
        
        return original
    
    def generate_master_key(self, license_key, salt, iterations=20000):
        key = (license_key + salt).encode()
        
        for i in range(iterations):
            if i % 2 == 0:
                key = hashlib.sha512(key + str(i).encode() + salt.encode()).digest()
            else:
                key = hashlib.sha256(key + str(i).encode() + salt.encode()).digest()
        
        return key
    
    def unlock_file(self, protected_file, license_key):
        print(f"\n{ColorCode.CYAN}{'═'*75}")
        print(f"  UNLOCKING FILE: {protected_file}")
        print(f"{'═'*75}{ColorCode.END}\n")
        
        if not os.path.exists(protected_file):
            print(f"{ColorCode.RED}[✗]{ColorCode.END} File tidak ditemukan!")
            return False
        
        print(f"{ColorCode.CYAN}[•]{ColorCode.END} Loading protected package...")
        
        try:
            with open(protected_file, 'r') as f:
                package = json.load(f)
        except:
            print(f"{ColorCode.RED}[✗]{ColorCode.END} Invalid file format!")
            return False
        
        license_data = package['license']
        
        # Verify license key
        print(f"{ColorCode.CYAN}[•]{ColorCode.END} Verifying license key...")
        
        if license_key.upper() != license_data['license_key'].upper():
            print(f"{ColorCode.RED}[✗]{ColorCode.END} INVALID LICENSE KEY!")
            return False
        
        print(f"{ColorCode.GREEN}[✓]{ColorCode.END} License key valid!")
        
        # Check hardware binding
        if license_data.get('hardware_bound'):
            current_hw = self.get_hardware_id()
            if current_hw != license_data['hardware_bound']:
                print(f"{ColorCode.RED}[✗]{ColorCode.END} HARDWARE MISMATCH!")
                print(f"{ColorCode.RED}[✗]{ColorCode.END} License terikat dengan hardware lain!")
                return False
            print(f"{ColorCode.GREEN}[✓]{ColorCode.END} Hardware verified!")
        
        # Check expiry
        print(f"{ColorCode.CYAN}[•]{ColorCode.END} Checking license expiry...")
        expiry = datetime.strptime(license_data['expiry'], '%Y-%m-%d %H:%M:%S')
        days_remaining = (expiry - datetime.now()).days
        
        if datetime.now() > expiry:
            print(f"{ColorCode.RED}[✗]{ColorCode.END} LICENSE EXPIRED!")
            return False
        
        print(f"{ColorCode.GREEN}[✓]{ColorCode.END} License aktif ({days_remaining} hari tersisa)")
        
        # Check usage limit
        usage_limit = license_data.get('usage_limit', 0)
        usage_count = license_data.get('usage_count', 0)
        
        if usage_limit > 0:
            if usage_count >= usage_limit:
                print(f"{ColorCode.RED}[✗]{ColorCode.END} USAGE LIMIT EXCEEDED!")
                print(f"{ColorCode.RED}[✗]{ColorCode.END} License sudah digunakan {usage_count}/{usage_limit} kali")
                return False
            print(f"{ColorCode.YELLOW}[!]{ColorCode.END} Usage: {usage_count + 1}/{usage_limit}")
        else:
            print(f"{ColorCode.GREEN}[✓]{ColorCode.END} Unlimited usage")
        
        # Decrypt
        print(f"{ColorCode.CYAN}[•]{ColorCode.END} Generating decryption key...")
        salt = license_data['salt']
        master_key = self.generate_master_key(license_key, salt)
        
        print(f"{ColorCode.CYAN}[•]{ColorCode.END} Decrypting file...")
        encrypted_b64 = package['encrypted_data']
        encrypted_data = b64decode(encrypted_b64)
        
        decrypted_data = self.multi_layer_decrypt(encrypted_data, master_key)
        
        output_file = package['metadata']['original_name']
        
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)
        
        # Update usage count
        if usage_limit > 0:
            license_data['usage_count'] = usage_count + 1
            package['license'] = license_data
            with open(protected_file, 'w') as f:
                json.dump(package, f, indent=2)
            print(f"{ColorCode.GREEN}[✓]{ColorCode.END} Usage updated: {usage_count + 1}/{usage_limit}")
        
        print(f"{ColorCode.GREEN}[✓]{ColorCode.END} File unlocked: {ColorCode.YELLOW}{output_file}{ColorCode.END}")
        
        original_size = package['metadata']['file_size']
        decrypted_size = len(decrypted_data)
        
        print(f"\n{ColorCode.GREEN}{'═'*75}")
        print(f"{ColorCode.BOLD}  FILE UNLOCKED SUCCESSFULLY!{ColorCode.END}{ColorCode.GREEN}")
        print(f"{'═'*75}{ColorCode.END}\n")
        
        return True


def main():
    unlocker = DrgXelUnlocker()
    
    protected_file = "DrgxDDoS.drgxel"
    
    if not os.path.exists(protected_file):
        print(f"{ColorCode.RED}[✗]{ColorCode.END} File tidak ditemukan")
        sys.exit(1)
    
    print(f"\n{ColorCode.CYAN}{'─'*75}{ColorCode.END}")
    print(f"{ColorCode.BOLD}  Masukkan License Key Anda{ColorCode.END}")
    print(f"{ColorCode.CYAN}{'─'*75}{ColorCode.END}\n")
    
    license_key = input(f"{ColorCode.YELLOW}License Key:{ColorCode.END} ").strip().upper()
    
    if not license_key:
        print(f"\n{ColorCode.RED}[✗]{ColorCode.END} License key tidak boleh kosong!")
        sys.exit(1)
    
    success = unlocker.unlock_file(protected_file, license_key)
    
    if success:
        print(f"{ColorCode.GREEN}[✓]{ColorCode.END} File siap digunakan!\n")
    else:
        print(f"\n{ColorCode.RED}[✗]{ColorCode.END} Gagal unlock file!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{ColorCode.YELLOW}[!]{ColorCode.END} Program dihentikan\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{ColorCode.RED}[✗]{ColorCode.END} Error: {e}\n")
        sys.exit(1)
