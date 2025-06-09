//google cooolab//

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
