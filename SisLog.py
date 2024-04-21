import winreg
import subprocess
import platform
import psutil
import os.path
import time
import winreg
from colorama import Fore, Style

# Este es un programa que permite crear archiviosde Log del sistema en ficehros txt.
# el codigo puede ser modificado a gusto propio para adaptarlo a su arquitectura o distribución, por defecto
# es windows pero facilmente puede pasar a linux o mac dependiento el uso apra esta herramienta,
# no soy responsable de el uso malintencionado que pueda ocasionar su uso, solo proporciono la herramienta forense para analisis
# informaticos. aún asi, tampoco es que sea una super herramienta.
# @author: Rawier


# Función para ver los programas instalados.

def get_installed_programs():
    installed_programs = []
    uninstall_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    for i in range(0, winreg.QueryInfoKey(uninstall_key)[0]):
        try:
            keyname = winreg.EnumKey(uninstall_key, i)
            subkey = winreg.OpenKey(uninstall_key, keyname)
            value = winreg.QueryValueEx(subkey, "DisplayName")[0]  # Corrección aquí
            installed_programs.append(value)
            winreg.CloseKey(subkey)
        except WindowsError:
            pass
    winreg.CloseKey(uninstall_key)
    return installed_programs


# Función para ver los procesos ejecutandose al momento.
def get_running_processes():
    processes_info = ""
    for process in psutil.process_iter():
        try:
            process_name = process.name()
            processes_info += process_name + "\n"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes_info


# Función para ver los servicios ejecutandose en el momento.
def get_running_services():
    services_info = ""
    for service in psutil.win_service_iter():
        try:
            if service.status() == "running":
                services_info += service.name() + "\n"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return services_info


# Función para mostrar la cache dns.
def get_dns_cache():
    dns_cache = subprocess.check_output(["ipconfig", "/displaydns"]).decode("ISO-8859-1")
    return dns_cache


# Función para mostrar información del sistema.
def get_system_info():
    system_info = f"Sistema operativo: {platform.system()} {platform.release()} {platform.version()}\n"
    system_info += f"Arquitectura: {platform.machine()}\n"
    system_info += f"Procesador: {platform.processor()}\n"
    system_info += f"Memoria RAM disponible: {psutil.virtual_memory().available / (1024 ** 3):.2f} GB\n"
    system_info += f"Uso de CPU: {psutil.cpu_percent()}%\n"
    system_info += f"Arquitectura: {platform.architecture()}%\n"
    return system_info


# Función para mostrar archivo Host.
def get_host_content():
    try:
        host_content = subprocess.check_output(["findstr", "/V", "#", r"C:\Windows\System32\drivers\etc\hosts"]).decode()
    except FileNotFoundError:
        print("El archivo hosts no se encontró.")
        host_content = ""
    except subprocess.CalledProcessError as e:
        print("Error al obtener el contenido del archivo hosts:", e)
        host_content = ""
    return host_content


# Función para mostrar conexiones NetBios activas.
def get_netbios_established():
    connections = psutil.net_connections(kind="udp")
    netbios_established = [conn for conn in connections if conn.status == "ESTABLISHED" and "netbios" in conn.laddr]
    netbios_established_str = "\n".join([f"{conn.laddr[0]}:{conn.laddr[1]} -> {conn.raddr[0]}:{conn.raddr[1]}" for conn in netbios_established])
    return netbios_established_str


# Función para mostrar cache ARP.
def get_arp_cache():
    arp_cache = subprocess.check_output(["arp", "-a"], encoding="latin-1")
    return arp_cache


# 𝕽♛
# Función para mostrar procesos activos.
def get_scheduled_tasks():
    scheduled_tasks = subprocess.check_output(["schtasks.exe", "/query", "/fo", "LIST"], encoding="cp1252")
    return scheduled_tasks


# Función para mostrar conexiones activas.
def get_active_connections():
    active_connections = subprocess.check_output(["netstat", "-ano"]).decode("latin-1")
    return active_connections


# Función para mostrar uso del disco C:
def get_disk_info():
    disk_path = os.path.abspath("C:\\")
    created_time = time.ctime(os.path.getctime(disk_path))
    modified_time = time.ctime(os.path.getmtime(disk_path))
    accessed_time = time.ctime(os.path.getatime(disk_path))
    return f"Fecha de creación del disco: {created_time}\nFecha de modificación del disco: {modified_time}\nÚltimo acceso al disco: {accessed_time}"


# Función para mostrar información de red y WIFI.
def get_network_info():
    network_info = ""
    # Obtener información de red
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        network_info += f"Interfaz: {interface_name}\n"
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                network_info += f"  Dirección IPv4: {address.address}\n"
                network_info += f"  Máscara de red IPv4: {address.netmask}\n"
            elif str(address.family) == 'AddressFamily.AF_INET6':
                network_info += f"  Dirección IPv6: {address.address}\n"
                network_info += f"  Máscara de red IPv6: {address.netmask}\n"

    # Obtener información de wifi
    wifi_info = psutil.net_io_counters(pernic=True)
    if 'Wi-Fi' in wifi_info:
        network_info += "Información de Wi-Fi:\n"
        network_info += f"  Bytes recibidos: {wifi_info['Wi-Fi'].bytes_recv}\n"
        network_info += f"  Bytes enviados: {wifi_info['Wi-Fi'].bytes_sent}\n"
    return network_info


# Función para mostrar unidades mapeadas.
def ver_unidades():
    unidades = os.popen("wmic logicaldisk get caption").read()
    print(unidades)
    with open("unidades.txt", "w") as f:
        f.write(unidades)
    print("Archivo exportado como 'unidades.txt'")
    return unidades  # Devolver la cadena 'unidades'


# Función para crear todos los ficheros txt en uno solo.
def crear_all_scan():
    processes = get_running_processes()
    disk_info = get_disk_info()
    network_info = get_network_info()
    installed_programs = get_installed_programs()
    services = get_running_services()
    cache_dns = get_dns_cache()
    info_system = get_system_info()
    host = get_host_content()
    netbios_establish = get_netbios_established()
    arp = get_arp_cache()
    prg_task = get_scheduled_tasks()
    scan_cap = get_active_connections()
    unidades = ver_unidades()  # Llamar a la función y almacenar su resultado

    # Escribir la información en un archivo all_scan.txt
    with open("all_scan.txt", "w") as f:
        f.write("INFORMACIÓN DE PROCESOS:\n\n" + processes)
        f.write("INFORMACIÓN DE PROGRAMAS INSTALADOS:\n\n")
        for program in installed_programs:
            f.write(program + "\n")
        f.write("INFORMACIÓN DEL DISCO:\n\n" + disk_info)
        f.write("INFORMACIÓN DE RED Y WIFI:\n\n" + network_info)
        f.write("INFORMACIÓN DE SERVICIOS:\n\n" + services)
        f.write("INFORMACIÓN DE CACHE DNS:\n\n" + cache_dns)
        f.write("INFORMACIÓN DEL SISTEMA:\n\n" + info_system)
        f.write("INFORMACIÓN DEL HOST:\n\n" + host)
        f.write("INFORMACIÓN DE CONEXIONES NETBIOS ESTABLECIDAS:\n\n" + netbios_establish)
        f.write("INFORMACIÓN DEL CACHE ARP:\n\n" + arp)
        f.write("INFORMACIÓN DE TAREAS PROGRAMADAS:\n\n" + prg_task)
        f.write("INFORMACIÓN DE CONEXIONES ACTIVAS O PUERTOS ABIERTOS:\n\n" + scan_cap)
        f.write("INFORMACIÓN DE UNIDADES CONECTADAS O MAPEADAS:\n\n" + unidades)

    print("Archivo exportado como 'all_scan.txt'")

while True:
    mensaje_ascii = ".s5SSSs.                .s                            \n      SS. s.  .s5SSSs.            .s5SSSs.  .s5SSSs.  \n sS    `:; SS.       SS. sS              SS.       SS. \n SS        S%S sS    `:; SS        sS    S%S sS    `:; \n`:;;;;.   S%S `:;;;;.   SS        SS    S%S SS        \n      ;;. S%S       ;;. SS        SS    S%S SS        \n      `:; `:;       `:; SS        SS    `:; SS   ``:; \n.,;   ;,. ;,. .,;   ;,. SS    ;,. SS    ;,. SS    ;,. \n`:;;;;;:' ;:' `:;;;;;:' `:;;;;;:' `:;;;;;:' `:;;;;;:'"
    print(Fore.LIGHTRED_EX + mensaje_ascii + Style.RESET_ALL)
    print(Fore.LIGHTMAGENTA_EX + "Created by Rawier" + Style.RESET_ALL)
    print("https://github.com/rawierdt/SisLog")
    print(" ")
    print(Fore.LIGHTYELLOW_EX + "Bienvenido, ¿Qué desea hacer?" + Style.RESET_ALL)
    print(" ")
    print("1. Ver programas instalados")
    print("2. Ver procesos en ejecución")
    print("3. Ver servicios en ejecución")
    print("4. Ver la caché DNS")
    print("5. Ver caché ARP")
    print("6. Ver informacion del sistema")
    print("7. Ver archivo Host")
    print("8. Ver conexiones NetBios establecidas")
    print("9. Ver tareas programadas")
    print("10. Ver conexiones activas o puertos abiertos")
    print("11. Ver creacion, modificacioon disco raiz")
    print("12. Ver informacion de red y WIFI")
    print("13. Ver unidades mapeadas")
    print("14. Crear todo")
    print(Fore.RED + "15. Salir" + Style.RESET_ALL)
    choice = input(Fore.LIGHTCYAN_EX + "Ingrese el número de su elección: " + Style.RESET_ALL)

    if choice == "1":
        # Mostrar los programas instalados y guardarlos en un archivo de texto
        programs = get_installed_programs()
        # Escribir los programas en un archivo de texto
        with open("programas.txt", "w") as f:
            for program in programs:
                f.write(program + "\n")

        print(
            f"Se han encontrado {len(programs)} programas instalados. Los nombres de los programas han sido guardados en el archivo programas.txt.")

    elif choice == "2":
        # Mostrar los procesos en ejecución y guardarlos en un archivo de texto
        processes = get_running_processes()
        with open("procesos.txt", "w") as f:
            for process in processes:
                f.write(process + "\n")
        print(f"Se han encontrado {len(processes)} procesos en ejecución. Los nombres de los procesos han sido guardados en el archivo procesos.txt.")

    elif choice == "3":
        # Mostrar los servicios en ejecución y guardarlos en un archivo de texto
        services = get_running_services()
        with open("servicios.txt", "w") as f:
            for service in services:
                f.write(service + "\n")
        print(f"Se han encontrado {len(services)} servicios en ejecución. Los nombres de los servicios han sido guardados en el archivo servicios.txt.")

    elif choice == "4":
        # Mostrar la caché DNS y guardarla en un archivo de texto
        dns_cache = get_dns_cache()
        with open("cache_dns.txt", "w") as f:
            f.write(dns_cache)
        print("La caché DNS ha sido guardada en el archivo cache_dns.txt.")

    elif choice == "5":
        # Mostrar el cache ARP y guardarlo en un archivo de texto
        arp_cache = get_arp_cache()
        with open("arp.txt", "w") as f:
            f.write(arp_cache)
        print("El cache ARP ha sido guardado en el archivo arp.txt.")

    elif choice == "6":
        # Mostrar la información del sistema y guardarla en un archivo de texto
        system_info = get_system_info()
        with open("info_sistema.txt", "w") as f:
            f.write(system_info)
        print("La información del sistema ha sido guardada en el archivo info_sistema.txt.")

    elif choice == "7":
        # Mostrar el contenido del archivo hosts y guardarlo en un archivo de texto
        host_content = get_host_content()
        with open("host.txt", "w") as f:
            f.write(host_content)
        print("El contenido del archivo hosts ha sido guardado en el archivo host.txt.")

    elif choice == "8":
        # Mostrar las conexiones NetBIOS establecidas y guardarlas en un archivo de texto
        netbios_established = get_netbios_established()
        with open("netbios_establish.txt", "w") as f:
            f.write(netbios_established)
        print("Las conexiones NetBIOS establecidas han sido guardadas en el archivo netbios_establish.txt.")

    elif choice == "9":
        # Mostrar las tareas programadas y guardarlas en un archivo de texto
        scheduled_tasks = get_scheduled_tasks()
        with open("tareas_prg.txt", "w") as f:
            f.write(scheduled_tasks)
        print("Las tareas programadas han sido guardadas en el archivo tareas_prg.txt.")

    elif choice == "10":
        # Mostrar las conexiones activas o puertos abiertos y guardarlos en un archivo de texto
        active_connections = get_active_connections()
        with open("scan_cap.txt", "w") as f:
            f.write(active_connections)
        print("Las conexiones activas o puertos abiertos han sido guardados en el archivo scan_cap.txt.")

    elif choice == "11":
        # Mostrar la fecha de creación, modificación y último acceso al disco raíz y guardarla en un archivo de texto
        disk_info = get_disk_info()
        with open("disco.txt", "w") as f:
            f.write(disk_info)
        print("La información del disco raíz ha sido guardada en el archivo disco.txt.")

    elif choice == "12":
        # Mostrar la información de red y wifi y guardarla en un archivo de texto
        network_info = get_network_info()
        with open("red.txt", "w") as f:
            f.write(network_info)
        print("La información de red y wifi ha sido guardada en el archivo red.txt.")

        # Mostrar unidades mapeadas
    elif choice == "13":
        ver_unidades()

        # Crear un solo fichero para.
    elif choice == "14":
        crear_all_scan()

        # Salir
    elif choice == "15":
        # Salir del programa
        break

    else:
        print("Elección no válida. Por favor, ingrese un número válido.")
