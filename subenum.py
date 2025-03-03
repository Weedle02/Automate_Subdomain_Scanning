#!/usr/bin/env python3
import subprocess
import argparse
import os
import glob
import re  

TOOLS = {
    "subfinder": "/home/user/go/bin/subfinder",
    "findomain": "/usr/bin/findomain",
    "assetfinder": "/home/user/go/bin/assetfinder",
    "dnsx": "/home/user/go/bin/dnsx",
    "httpx": "/home/user/go/bin/httpx",
    "eyewitness": "/home/user/go/bin/EyeWitness/Python/EyeWitness.py"
}

def sanitize_domain(domain):
    return domain.replace('.', '_')

def clean_web_active_file(input_path, output_path):
    """Clean ANSI codes and non-URL content from web_active file"""
    cleaned_urls = []
    try:
        with open(input_path, 'r') as f:
            for line in f:
                clean_line = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', line)
                url = clean_line.split()[0].strip()
                if url.startswith(('http://', 'https://')):
                    cleaned_urls.append(url)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(cleaned_urls))
            
    except Exception as e:
        print(f"[-] Error cleaning web active file: {str(e)}")
        exit(1)

def run_command(command, stdin_input=None):
    try:
        result = subprocess.run(
            command,
            input=stdin_input,
            check=True,
            text=True,
            capture_output=True,
            shell=False,
            timeout=600
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Command failed: {' '.join(command)}")
        print(f"Error output:\n{e.stderr}")
        exit(1)

def clear_output_files():
    output_dir = "SR"
    if os.path.exists(output_dir):
        deleted = 0
        for filename in glob.glob(os.path.join(output_dir, "*.txt")):
            try:
                os.remove(filename)
                deleted += 1
            except Exception as e:
                print(f"Error deleting {filename}: {str(e)}")
        print(f"[+] Removed {deleted} files from {output_dir}")
    else:
        print(f"[-] Directory {output_dir} does not exist")

def run_dns_checks(subs):
    proc = subprocess.Popen(
        [TOOLS["dnsx"], "-silent", "-a", "-aaaa", "-cname"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    proc.stdin.write("\n".join(sorted(subs)))
    proc.stdin.close()
    
    resolved_subs = set()
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        resolved_subs.add(line.strip().split()[0])
    
    proc.wait()
    return sorted(resolved_subs)

def run_http_checks(subs):
    proc = subprocess.Popen(
        [TOOLS["httpx"], "-silent", "-status-code", "-title"],  
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    proc.stdin.write("\n".join(subs))
    proc.stdin.close()
    
    web_subs = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        web_subs.append(line.strip())
    
    proc.wait()
    return web_subs

def run_eyewitness(input_file, output_dir):
    print("\n[+] Starting EyeWitness analysis...")
    eyewitness_dir = os.path.join(output_dir, "EyeWitness_Report")
    os.makedirs(eyewitness_dir, exist_ok=True)
    
    command = [
        "xvfb-run",
        "python3", 
        TOOLS["eyewitness"],
        "--web",
        "-f", input_file,
        "-d", eyewitness_dir,
        "--no-prompt",
        "--timeout", "30",  
        "--threads", "3",  
        "--max-retries", "2",
        "--resolve",
        "--width", "1920",
        "--height", "1080"
    ]
    
    run_command(command)
    
    print(f"[+] EyeWitness report saved to {eyewitness_dir}")

def main(domain, enable_screenshots):
    output_dir = "SR"
    safe_domain = sanitize_domain(domain)
    
    raw_path = os.path.join(output_dir, f"{safe_domain}_raw.txt")
    dns_path = os.path.join(output_dir, f"{safe_domain}_dns_validated.txt")
    web_path = os.path.join(output_dir, f"{safe_domain}_web_active.txt")
    clean_web_path = os.path.join(output_dir, f"{safe_domain}_web_clean.txt")

    os.makedirs(output_dir, exist_ok=True)

    print(f"\n[+] Starting subdomain enumeration for: {domain}")

    # Subdomain enumeration
    print("\n[1/3] Running Subfinder...")
    subfinder = run_command([TOOLS["subfinder"], "-d", domain, "-silent"])
    
    print("[2/3] Running Findomain...")
    findomain = run_command([TOOLS["findomain"], "-t", domain, "--quiet"])
    
    print("[3/3] Running Assetfinder...")
    assetfinder = run_command([TOOLS["assetfinder"], domain])

    # Combine results
    all_subs = set()
    all_subs.update(subfinder.splitlines())
    all_subs.update(findomain.splitlines())
    all_subs.update(assetfinder.splitlines())

    if not all_subs:
        print("[-] No subdomains found!")
        exit(0)

    # Save raw results
    with open(raw_path, "w") as f:
        f.write("\n".join(sorted(all_subs)))
    print(f"\n[+] Raw subdomains saved to {raw_path} ({len(all_subs)} found)")

    # DNS validation
    dns_valid = run_dns_checks(all_subs)
    if not dns_valid:
        print("[-] No DNS-resolvable subdomains found")
        exit(0)
    
    with open(dns_path, "w") as f:
        f.write("\n".join(dns_valid))
    print(f"[+] DNS-validated subdomains saved to {dns_path} ({len(dns_valid)} found)")

    # HTTP checks
    web_active = run_http_checks(dns_valid)
    if not web_active:
        print("[-] No web-accessible subdomains found")
        exit(0)
    
    with open(web_path, "w") as f:
        f.write("\n".join(web_active))
    print(f"[+] Web-active subdomains saved to {web_path} ({len(web_active)} found)")

    # Clean file for EyeWitness
    clean_web_active_file(web_path, clean_web_path)
    print(f"[+] Cleaned URLs for EyeWitness saved to {clean_web_path}")

    # Optional EyeWitness
    if enable_screenshots:
        run_eyewitness(clean_web_path, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain Enumeration with Optional Screenshots")
    parser.add_argument("-d", "--domain", help="Target domain name")
    parser.add_argument("--clear", action="store_true", help="Clear all results files")
    parser.add_argument("--screenshots", action="store_true", 
                      help="Capture screenshots and generate EyeWitness report")
    args = parser.parse_args()
    
    if args.clear:
        clear_output_files()
    elif args.domain:
        main(args.domain, args.screenshots)
    else:
        parser.print_help()
