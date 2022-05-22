Layout
GPIO2 - I2C_SDA
GPIO3 - I2C_CLK
GPIO4 - 1WIRE dla czujnika temperatury


1) na RPi:
sudo raspi-config
-> Interface option -> wlaczyc i2c i 1-wire

2) sciagnac repo

#Przed odpaleniem skryptu nalezy wpisac w konsoli otwartej w glownych pliku repo:
3)sudo chmod u+x install_lib.sh
# wystartowac skrypt
4)sudo ./install_lib.sh

in progress.... :)


Bug list(TODO):
- Poprawic uklad dla grafu, uzyc vp by miescil sie w swoim divie dla kazdej rozdzielczosci,
- Poprawic init funkcje dla uzupelnienia dcc.Input elementow, zeby czytaly z gen wartosc ustawiona.
- Dla headera repr status pomiaru dodac funkcje init, ktora bedzie sprawdzac jak ustawic wartosc na starcie