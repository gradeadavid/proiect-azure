# Corpus fictiv — VelaBank, produse de tip card

Toate documentele din acest folder sunt **fictive**, create pentru Assignment 3.
Banca ("VelaBank"), produsele, sumele și numerele de telefon sunt inventate — nu au
legătură cu vreun angajator sau bancă reală.

## Documente și cazul(urile) pe care le acoperă

| Document | Caz acoperit |
|---|---|
| `card-tipuri-si-eligibilitate.md` | Trebuie combinat cu documentele de taxe / asigurare pentru un răspuns complet |
| `card-taxe-2025.md` | Tabel · aproape-duplicat cu 2026 |
| `card-taxe-2026.md` | Tabel · aproape-duplicat cu 2025 (valori diferite) |
| `card-blocare-deblocare.md` | Procedură lungă, pas cu pas · număr precis (3 încercări PIN, 24h) |
| `card-inlocuire-pierdut-furat.md` | Procedură lungă, pas cu pas · trebuie combinat cu documentul de contestare |
| `card-limita-retragere-atm-v1-2025.md` | Contradicție între versiuni (pereche cu v2) |
| `card-limita-retragere-atm-v2-2026.md` | Contradicție între versiuni — limita a crescut de la 2.000/5.000 la 3.000/6.000 lei |
| `card-dobanda-comisioane-credit.md` | Numere precise (DAE 21,5%, comision 4% min 15 lei) |
| `card-tranzactii-contestare.md` | Procedură lungă, pas cu pas · trebuie combinat cu documentul de card pierdut/furat |
| `card-securitate-3dsecure-notificari.md` | Numere precise (3 minute confirmare, 0,10 lei/SMS) |
| `card-produse-neofertate.md` | Ceva absent intenționat — VelaBank nu oferă BNPL, carduri cripto, prepaid anonime |
| `card-asigurare-si-beneficii.md` | Trebuie combinat cu `card-tipuri-si-eligibilitate.md` pentru condițiile de eligibilitate Platinum · numere precise (30.000 EUR, 5.000 lei) |

## Acoperirea celor 7 cazuri din enunț

| Caz | Documente |
|---|---|
| Un număr precis | `card-blocare-deblocare.md`, `card-dobanda-comisioane-credit.md`, `card-securitate-3dsecure-notificari.md`, `card-asigurare-si-beneficii.md` |
| Două documente combinate | `card-tipuri-si-eligibilitate.md` + `card-taxe-2026.md` (cost per tip de card); `card-tipuri-si-eligibilitate.md` + `card-asigurare-si-beneficii.md` (cine are dreptul la beneficii Platinum); `card-inlocuire-pierdut-furat.md` + `card-tranzactii-contestare.md` (ce faci după furt) |
| Aproape-duplicate care diferă | `card-taxe-2025.md` vs `card-taxe-2026.md` |
| Procedură lungă, pas cu pas | `card-blocare-deblocare.md`, `card-inlocuire-pierdut-furat.md`, `card-tranzactii-contestare.md` |
| Un tabel | `card-taxe-2025.md`, `card-taxe-2026.md` |
| Contradicție între versiuni | `card-limita-retragere-atm-v1-2025.md` vs `card-limita-retragere-atm-v2-2026.md` |
| Ceva absent intenționat | `card-produse-neofertate.md` |

