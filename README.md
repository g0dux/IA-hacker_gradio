# 🧠 IA Hacker - Google Colab Offensive Toolkit

**IA Hacker** is a portable, ready-to-use environment that integrates classic *ethical hacking* tools directly into Google Colab. Built with Python, Gradio, and a suite of security utilities, this project acts as a remote and accessible testing lab for penetration testers, cybersecurity students, and researchers.

> ⚠️ **Legal Disclaimer:** This project is strictly for educational purposes. Misuse of these tools to access unauthorized systems is illegal and unethical.

---

## 🚀 Included Tools

This environment automatically installs and integrates the following utilities:

| Tool         | Description |
|--------------|-------------|
| **Nmap**     | Network and port scanner used for infrastructure reconnaissance. |
| **Wpscan**   | Vulnerability scanner tailored for WordPress sites. |
| **Nikto**    | Web server vulnerability scanner focusing on misconfigurations and dangerous files. |
| **Amass**    | Subdomain enumeration and DNS mapping tool. |
| **WafW00f**  | Web Application Firewall (WAF) detector. |
| **Ffuf**     | Fast web fuzzer for content discovery and parameter testing. |
| **IA-Hacker (Gradio)** | Gradio-based web UI for managing tools and automation. |

---

## 📦 Automatic Installation (Google Colab)

Open a notebook on Google Colab and run the following commands:

```python
!apt-get install nmap -y
!gem install wpscan
!apt-get install nikto -y
!snap install amass
!pip install wafw00f
!apt-get install golang -y
!go install github.com/ffuf/ffuf/v2@latest
%cd /content
!git clone https://github.com/g0dux/IA-hacker_gradio.git
%cd /content/IA-hacker_gradio
!pip install -r requirements.txt
!python main.py
