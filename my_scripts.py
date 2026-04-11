import os
import sys

def hibernate():
    os.system("sudo systemctl hibernate -i")
        
def poweroff():
    os.system("sudo systemctl poweroff -i")
  
def restart_system():
    os.system("sudo systemctl reboot -i")
    
def restart_drivers_video():
    os.system("systemctl restart gdm3 -i")

def abrir_pasta(): 
    os.system("xdg-open .")
    
def pegar_caminho_pasta(): 
    print(os.getcwd())

def suspender():
    os.system("systemctl suspend -i ")
    

def menu(): 
    print("=============== MENU ===============")
    print("0 - suspender")
    print("1 - hibernate")
    print("2 - poweroff")
    print("3 - restart_system")
    print("4 - restart_drivers_video")
    print("5 - abrir_pasta")
    print("6 - pegar_caminho_pasta")
    print("====================================")

def manager_simple_scripts():
    try: 
        command = int( sys.argv[2] )
    except:
        menu()
        command = int( input(">> ") )
        
    if command == 0: 
        suspender()
    elif command == 1: 
        hibernate()
    elif command == 2: 
        poweroff()
    elif command == 3: 
        restart_system()
    elif command == 4: 
        restart_drivers_video()
    elif command == 5: 
        abrir_pasta()
    elif command == 6: 
        pegar_caminho_pasta()
        