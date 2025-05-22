# Network Device Configuration Tool

## Opis projektu

Network Device Configuration Tool to zaawansowana aplikacja desktopowa napisana w Python z wykorzystaniem PySide6, przeznaczona do konfiguracji urządzeń sieciowych Cisco (routery i przełączniki). Aplikacja umożliwia tworzenie, edycję i generowanie konfiguracji IOS/IOS-XE w intuicyjnym interfejsie graficznym.

## Główne funkcje

### 🔧 Obsługiwane urządzenia
- **Routery Cisco**: 1841, 1941, 2811, 2911, 4321
- **Przełączniki L2**: Cisco 2960, 3560, 3650, 3850
- **Przełączniki L3**: Z pełną obsługą funkcji routingu

### 📋 Szablony konfiguracji
- **Szablony urządzeń**: Podstawowa konfiguracja routera/przełącznika
- **Szablony portów dostępowych (Access)**: Kompletna konfiguracja portów końcowych
- **Szablony portów magistralnych (Trunk)**: Konfiguracja połączeń między przełącznikami
- **Szablony L3**: Zaawansowane funkcje routingu dla przełączników warstwy 3

### 🎨 Interfejs użytkownika
- Intuicyjny interfejs z zakładkami tematycznymi
- Kolorowe oznaczenia szablonów dla łatwej identyfikacji
- Dynamiczne przypisywanie interfejsów do szablonów
- Podgląd na żywo generowanej konfiguracji

## Struktura projektu

```
├── src/
│   ├── data/                    # Dane konfiguracyjne urządzeń
│   ├── forms/                   # Formularze GUI
│   │   ├── AccessTemplateForm.py
│   │   ├── TrunkTemplateForm.py
│   │   ├── RouterTemplateForm.py
│   │   ├── SwitchL2TemplateForm.py
│   │   └── SwitchL3TemplateForm.py
│   ├── models/                  # Modele danych
│   │   └── templates/
│   │       ├── AccessTemplate.py
│   │       ├── TrunkTemplate.py
│   │       ├── RouterTemplate.py
│   │       ├── SwitchL2Template.py
│   │       └── SwitchL3Template.py
│   ├── utils/                   # Narzędzia pomocnicze
│   ├── views/                   # Widoki głównej aplikacji
│   │   ├── ConfigPageAdd/       # Strona konfiguracji
│   │   ├── MainWindow.py
│   │   └── StartPage.py
│   └── widgets/                 # Komponenty UI
│       └── ColorPicker.py
└── app.py                       # Punkt wejścia aplikacji
```

## Funkcje konfiguracyjne

### Szablony Access Port
- **Podstawowe ustawienia**: VLAN, opis, prędkość, duplex
- **Bezpieczeństwo portów**: Ograniczenia MAC, akcje naruszenia
- **Spanning Tree**: PortFast, BPDU Guard, Loop Guard
- **QoS**: Trust states, policing, shaping
- **Uwierzytelnianie**: 802.1X, MAC Authentication Bypass, Web Auth
- **PoE**: Zarządzanie zasilaniem przez Ethernet
- **Storm Control**: Kontrola broadcastu, multicastu, unknown unicast
- **DHCP/ARP Security**: DHCP Snooping, ARP Inspection
- **Voice VLAN**: Obsługa telefonów IP

### Szablony Trunk Port
- **VLAN**: Allowed VLANs, Native VLAN, pruning
- **Enkapsulacja**: dot1q, ISL
- **DTP**: Dynamic Trunking Protocol
- **EtherChannel**: LACP, PAgP
- **Bezpieczeństwo**: DHCP Snooping Trust, ARP Inspection Trust
- **QoS**: Trust states, priority queues

### Szablony Router/Switch
- **Konfiguracja podstawowa**: Hostname, domeny, zarządzanie
- **VLANs**: Tworzenie i zarządzanie VLAN-ami
- **Spanning Tree**: Tryby, priorytety, timery
- **Monitoring**: Logging, SNMP, SPAN
- **AAA**: Uwierzytelnianie, autoryzacja, accounting

### Szablony Switch L3 (dodatkowe funkcje)
- **Interfejsy SVI**: Switch Virtual Interfaces
- **Routing**: OSPF, EIGRP, trasy statyczne
- **ACL**: Access Control Lists
- **NAT**: Network Address Translation
- **DHCP Server**: Pule adresów, excluded addresses
- **HSRP/VRRP**: High availability protocols
- **VRF**: Virtual Routing and Forwarding

## Instalacja i uruchomienie

### Wymagania
- Python 3.8+
- PySide6
- Pozostałe zależności w `requirements.txt` (jeśli istnieje)

### Uruchomienie
```bash
python app.py
```

## Sposób użycia

1. **Wybór urządzenia**: Na stronie startowej wybierz typ i model urządzenia
2. **Konfiguracja**: Przejdź do strony konfiguracji
3. **Tworzenie szablonów**: 
   - Użyj przycisku "New Template" aby utworzyć nowy szablon
   - Lub edytuj istniejące szablony (Device, VLAN 1)
4. **Przypisywanie interfejsów**: Kliknij interfejsy aby przypisać je do szablonów
5. **Generowanie konfiguracji**: Użyj przycisku "Zastosuj zmiany" aby wygenerować kod IOS
6. **Export**: Konfiguracja jest automatycznie kopiowana do schowka

## Główne klasy i komponenty

### Modele szablonów
- `AccessTemplate`: Kompletny model portu dostępowego z enum-ami dla działań naruszenia, trybów PoE, stanów QoS
- `TrunkTemplate`: Model portu magistralnego z obsługą enkapsulacji, DTP, EtherChannel
- `SwitchL2Template`: Model przełącznika L2 z obsługą VLAN, STP, QoS, monitoring
- `SwitchL3Template`: Rozszerza SwitchL2Template o funkcje routingu L3

### Formularze GUI
- Organizacja w zakładki tematyczne (Basic, VLANs, Spanning Tree, Security, QoS, etc.)
- Dynamiczne włączanie/wyłączanie pól w zależności od ustawień
- Obsługa kolorów dla wizualnej identyfikacji szablonów
- Walidacja danych wejściowych

### Zarządzanie interfejsami
- `InterfaceAssignmentManager`: Śledzi przypisania interfejsów do szablonów
- Dynamiczne kolorowanie przycisków interfejsów
- Obsługa różnych typów urządzeń (router/switch L2/L3)

## Generowanie konfiguracji

Każdy szablon implementuje metodę `generate_config()` która zwraca listę komend IOS CLI:

- **Kompletne bloki konfiguracyjne**: configure terminal ... end
- **Optymalizacja**: Generowane są tylko aktywnie skonfigurowane funkcje
- **Hierarchia**: Szablony urządzeń mogą zawierać szablony portów jako zagnieżdżone konfiguracje
- **Kompatybilność**: Kod generowany dla IOS/IOS-XE

## Dodatkowe funkcje

- **ColorPicker**: Komponent do wyboru kolorów szablonów z RGB/HEX
- **Dynamiczne tabele**: Dodawanie/usuwanie wierszy w tabelach MAC, ACL, etc.
- **Obsługa enum-ów**: Type-safe wartości dla konfiguracji
- **Cache stron**: Optymalizacja wydajności interfejsu
- **Obsługa błędów**: Graceful handling nieprawidłowych danych

## Status rozwoju

Projekt jest aktywnie rozwijany. Aktualne funkcjonalności obejmują:
- ✅ Podstawowa struktura aplikacji
- ✅ Szablony Access Port (kompletne)
- ✅ Szablony Trunk Port (kompletne)
- ✅ Szablony Switch L2 (kompletne)
- ✅ Szablony Switch L3 (kompletne)
- ✅ Generowanie konfiguracji IOS
- ✅ Kolorowe oznaczenia interfejsów
- ✅ System zarządzania szablonami
- 🔄 Eksport do plików (w trakcie)
- 🔄 Import istniejących konfiguracji (planowane)

## Licencja

[Informacje o licencji do uzupełnienia]

## Kontakt

[Informacje kontaktowe do uzupełnienia]