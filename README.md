# SubDomain Recon Suite

A comprehensive subdomain enumeration and reconnaissance tool that automates discovery, validation, and screenshot capture processes.

## Features

- **Subdomain Enumeration**: Combines results from multiple tools
- **DNS Validation**: Filters out dead subdomains
- **HTTP Analysis**: Identifies live web services
- **Visual Recon**: Captures screenshots of web interfaces
- **Smart Output**: Organized results with clean reporting

## Prerequisites

- Go 1.20+ (`go version`)
- Python 3.10+ (`python3 --version`)
- Firefox ESR (`firefox-esr --version`)

## Tools Used

| [subfinder](https://github.com/projectdiscovery/subfinder) | v2.6.4 | Subdomain discovery |
| [findomain](https://github.com/Findomain/Findomain) | v9.0.4 | Certificate transparency parsing |
| [assetfinder](https://github.com/tomnomnom/assetfinder) | v0.1.1 | Domain association discovery |
| [dnsx](https://github.com/projectdiscovery/dnsx) | v1.1.6 | DNS record validation |
| [httpx](https://github.com/projectdiscovery/httpx) | v1.3.8 | HTTP service analysis |
| [EyeWitness](https://github.com/FortyNorthSecurity/EyeWitness) | v3.1.0 | Screenshot capture & header analysis |

# Install Go tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/findomain/findomain@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

## Usage 

python3 subenum.py -d example.com

## Output Structure

SR/
├── example_com_raw.txt
├── example_com_dns_validated.txt
├── example_com_web_active.txt
├── example_com_web_clean.txt
└── EyeWitness_Report/
    ├── screenshots/
    ├── report.html
    └── headers.csv


