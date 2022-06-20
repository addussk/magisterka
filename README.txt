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
- (DONE) Refactoring callbacka aktualizujacego graf- na starcie wyswietla ostatni pomiar oraz podczas pomiaru aktualny.
- (DONE) Wystylizowanie diag boxow zawierajacych formularz - poprawione
- (DONE) Rozwiazanie problemu z handlowaniem freq i pwr dla fix moda. Czy w formularzu powinna byc opcja ustawienia? - po zaktualizowaniu wartosci w glownym widoku, dane widoczne w formualrzu.
- Poprawic uklad dla grafu, uzyc vp by miescil sie w swoim divie dla kazdej rozdzielczosci,
- Poprawic init funkcje dla uzupelnienia dcc.Input elementow, zeby czytaly z gen wartosc ustawiona.
- Dla headera repr status pomiaru dodac funkcje init, ktora bedzie sprawdzac jak ustawic wartosc na starcie
- Dodanie ograniczenia przy ustawianiu mocy i czestotliwosci
- Dodanie koloru zielonego dla status headera gdy odbywa sie pomiar
- Dodanie warning boxow
- Poprawa legendy grafu
- Mozliwosc wprowadzenia nazwy pomiarow

Rzeczy do poprawy(Spotkanie 2.06.2022):
1) Dodac access do repositorum - (DONE)
2) dodac blank space miedzy wartosc pomiaru a jednostke. (DONE)
3) Kwestia klawiatury, standardowa lub custom
4) p-tracking usunac freq step,  power zamienic power min max. (DONE)
5) pf przekopiowac dialog window z dodaniem pwr min max. (DONE)
6) maxksymalny czas grzania dla wszystkich trybow
7) Aktualizacja wartosci czestotliwosci po zaakceptowaniu ustawien danego trybu (DONE)
8) Stworzenie blokad dla kontrolek podczas dzialania jednego trybu i reprezentowanie tego w odpowiedni sposob(wyszarzyc).
9) Manage result button w miejsce 
10) jak czesto zapisuja sie elemenety do pamieci na raspberry pi
11) Przeniesienie btn start na jeden panel z stop btn (DONE)
12) Dodanie podswietlenia stp btn po jego wcisnieciu (DONE)
13) Zmiana kolorow na neutralne (DONE)
14) Problem z przekazaniem cfg dla p i pf trybu pracy. (DONE)