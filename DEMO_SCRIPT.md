# Demo Script – HAL / Quantera.ai (Pre-indexed Version)

**DD1367 Software Engineering in Project Form – Group 14**  
**Datum:** 28 maj 2026 | **Tid:** ~10 minuter

---

## Förberedelser (gör detta 10 minuter innan demon börjar)

### Steg 1: Starta FreeLLMAPI
```bash
# I ett separat terminalfönster
npm start   # eller motsvarande för din FreeLLMAPI-setup
```
Verifiera att den svarar: `curl http://localhost:3001/v1/models`

### Steg 2: Kör demo-prep (detta för-indexerar allt och sparar tokens under demon!)
```bash
make demo-prep
```
Detta gör:
1. Rensar gammal data
2. Genererar nya demo-filer (4 CSV-rapporter)
3. Konverterar till Markdown (ingen LLM behövs)
4. Populerar SQLite-databasen med korrekt metadata

### Steg 3: Verifiera
```bash
make list
```
Du ska se 4 dokument (Volvo Group, Ericsson, Atlas Copco, Investor AB).

### Steg 4: Ställ in terminalen
- Öka textstorleken (Ctrl++ några gånger)
- Rensa skärmen (`clear`)
- Ha detta script redo på sidan

---

## Varför för-indexera?

**Smartaste strategin:** Kör `make demo-prep` innan demon. Då är allt redan klart.

Under demon behöver ni **bara query-anrop** – och varje query kostar tokens. Om ni också kör `make ingest` live under demon så lägger ni till **4 extra LLM-anrop** (ett per fil för kategorisering) som tar tid och riskerar rate limiting från FreeLLMAPI.

Så här fungerar det:
- ✅ **`make demo-prep`** (körs innan, gratis, ingen risk) – konverterar filer + sparar metadata
- ✅ **`make query Q="..."`** (körs live under demon) – detta är det enda som behöver LLM

Om du **måste** visa live-indexering, kör bara `make ingest` – det visar snabbt "Skipped (already done): 4" eftersom allt redan finns. Då ser publiken att systemet fungerar utan att vänta på LLM-anrop.

---

## Demo-flöde

### Del 1 – Sätt scenen (1 min)

> **Säg:** "Tänk er att ni är analytiker på ett private equity-bolag. Ni har fått in Q1-rapporter från fyra stora svenska bolag i portföljen – Volvo, Ericsson, Atlas Copco och Investor AB. Chefen vill ha en snabb överblick över hur de presterat. Normalt tar det timmar att gå igenom allt. Med HAL tar det tio sekunder."

---

### Del 2 – Visa indexeringspipelinen (2 min)

**Steg 1 – Visa input-filer**
```bash
ls data/input/
```
> **Säg:** "Här ligger våra fyra råfiler – CSV-rapporter med finansiell data. Normalt skulle det ta timmar att gå igenom dessa manuellt."

**Steg 2 – Visa att systemet redan har indexerat allt**
```bash
make ingest
```

> **Säg:** "Jag körde indexeringen innan demon för att spara tid, men låt mig visa att systemet hanterar det."

**Förväntad output:**
```
Starting ingestion pipeline...
Found 4 input file(s).

Converting to Markdown...
Categorising and indexing documents...

==================================================
INGESTION SUMMARY
==================================================
  Input files found:      4
  Converted (new):        4
  Skipped (already done): 0
  Conversion failures:    0
  Newly indexed:          0          <-- REDAN KLART
  Skipped (already done): 4          <-- ALLT FANNIS REDAN
  Indexing failures:      0
  Total in database:      4
==================================================
```

> **Säg:** "Systemet ser att allt redan är konverterat och indexerat. Det här är deduplicering – en viktig feature. Om jag lägger till en ny fil imorgon, indexerar den bara den nya utan att göra om allt."

**Steg 3 – Visa indexerade dokument**
```bash
make list
```
> **Säg:** "Databasen vet nu att Volvo Group är ett lastbilsbolag, Ericsson är telekom, Atlas Copco industri, och Investor AB är en investmentbolag. Allt utan manuell konfiguration."

**Steg 4 – (Valfritt) Visa SQLite-databasen**
```bash
venv/bin/python3 -c "import sqlite3; conn=sqlite3.connect('data/quantera.db'); [print(r) for r in conn.execute('SELECT company, categories FROM documents').fetchall()]; conn.close()"
```

---

### Del 3 – Live-frågor (4 min)

#### Fråga 1 – Enkel faktafråga (1 min)
```bash
make query Q="What is the Q1 2025 net sales of Volvo Group?"
```
> **Säg:** "Här ber systemet först retrieval-agenten att hitta rätt dokument – i detta fall Volvos rapport – och skickar sedan frågan och dokumentet till en större LLM för att få ett precist svar."

**Förväntad output:**
- Relevant dokument: `volvo_group_report_csv.md`
- Svar innehåller: SEK 132.4 miljarder

#### Fråga 2 – Jämförande fråga (1.5 min)
```bash
make query Q="Compare the EBIT margin of Volvo Group and Atlas Copco in Q1 2025"
```
> **Säg:** "Nu blir det svårare. Systemet måste hitta dokument från BÅDA bolagen, slå ihop dem, och generera en jämförelse. Notera att det inte bara listar siffror – det ger en analys."

**Förväntad output:**
- Relevanta dokument: både Volvo och Atlas Copco
- Svar innehåller: Volvo 14.3%, Atlas Copco 22.1%, med en kort analys av skillnaden

#### Fråga 3 – Analytisk/trendbaserad fråga (1.5 min)
```bash
make query Q="What are the main financial risks across our portfolio based on the latest reports?"
```
> **Säg:** "Här aggregerar systemet riskfaktorer från ALLA fyra bolag och ger en sammansatt analys. Det här är kärnan i vad HAL gör – att komprimera en veckas manuellt arbete till sekunder."

**Förväntad output:**
- Relevanta dokument: alla 4
- Svar innehåller: risker från Volvo (lastbilsmarknaden), Ericsson (5G-utrullning), Atlas Copco (Kina/valuta), Investor AB (koncentrationsrisk)

---

### Del 4 – Felhantering (1 min)

```bash
make query Q="What is the Q1 2025 revenue of Tesla?"
```
> **Säg:** "Ett system som bara fungerar på perfekta indata är inte ett riktigt system. Vi har testat felfall – och HAL hanterar dem utan att krascha."

**Förväntad output:**
```
No relevant documents found for this query.
```

---

### Del 5 – Avslutning & publikfråga (2 min)

> **Säg:** "Har någon en fråga de vill ställa till systemet? Vi kör den live."

**Om ingen svarar, använd backup-frågan:**
```bash
make query Q="What is the Q1 2025 free cash flow of Ericsson?"
```

**Förväntad output:**
- Svar innehåller: SEK -1.2 miljarder (negativt!)

> **Säg:** "Det här är vad en veckas manuellt analysarbete kan komprimeras till. Det är HAL."

---

## Backup-planer

| Problem | Åtgärd |
|---------|--------|
| API-anropet hänger / timeout | Kommentera lugnt: "Det här är ett bra exempel på varför vi testar – vi ser att modellen resonerar men tar en stund." Växla till `make list` och visa databasen istället. |
| FreeLLMAPI är nere | Kör `make demo-prep` + visa den förberedda SQLite-databasen och förinspelade svar. |
| Fel svar från LLM | Kommentera: "Det här är ett bra exempel på varför vi testar – vi ser att modellen resonerar men missar X. I produktion skulle vi validera med mänsklig feedback." |
| Databasen är tom | Kör `make demo-prep` igen. |
| `make ingest` misslyckas | Eftersom allt redan är för-indexerat spelar det ingen roll. Visa bara `make list` och fortsätt med frågor. |

---

## Exakta kommandon (snabbreferens)

```bash
# === FÖRBEREDELSE (körs 10 min innan demon) ===
make demo-prep              # Återställer allt + för-indexerar (INGA tokens)
make list                   # Verifiera att 4 dokument finns

# === UNDER DEMONS ===
# Del 2 - Visa pipelinen (körs live, men visar bara skips)
make ingest
make list

# Del 3 - Live-frågor (detta kostar tokens)
make query Q="What is the Q1 2025 net sales of Volvo Group?"
make query Q="Compare the EBIT margin of Volvo Group and Atlas Copco in Q1 2025"
make query Q="What are the main financial risks across our portfolio?"

# Del 4 - Felhantering
make query Q="What is the Q1 2025 revenue of Tesla?"

# Del 5 - Backup-fråga (om publiken inte frågar)
make query Q="What is the Q1 2025 free cash flow of Ericsson?"

# === DEBUG / KOLLA DATABASEN ===
venv/bin/python3 -c "import sqlite3; conn=sqlite3.connect('data/quantera.db'); [print(r) for r in conn.execute('SELECT company, categories FROM documents').fetchall()]; conn.close()"
```

---

## Dataöversikt (att ha i bakhuvudet)

| Bolag | Nyckelmått (Q1 2025) |
|-------|----------------------|
| **Volvo Group** | Net Sales: SEK 132.4B (+8%), EBIT: SEK 18.9B, EBIT Margin: 14.3%, FCF: SEK 8.7B |
| **Ericsson** | Net Sales: SEK 53.3B (-2%), EBIT: SEK 3.8B, EBIT Margin: 7.1%, FCF: SEK -1.2B |
| **Atlas Copco** | Revenues: SEK 41.2B (+11%), EBIT: SEK 9.1B, EBIT Margin: 22.1%, FCF: SEK 5.4B |
| **Investor AB** | NAV: SEK 685B (+5%), Dividend Income: SEK 4.2B, Net Cash: SEK 28.5B |

---

## Demo-checklista

### Tekniskt (innan demon)
- [ ] FreeLLMAPI körs på localhost:3001 (`curl http://localhost:3001/v1/models` ska svara)
- [ ] `make demo-prep` har körts och avslutats utan fel
- [ ] `make list` visar 4 dokument
- [ ] `make query Q="What is the Q1 2025 net sales of Volvo Group?"` ger ett rimligt svar

### Under demon
- [ ] Terminal-textstorlek är stor nog för publiken
- [ ] Detta script är utskrivet eller synligt
- [ ] Backup-planer är memoriserade
- [ ] Internetuppkoppling är testad
