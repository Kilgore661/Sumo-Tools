# JSA & Grand Sumo (Ōzumō) Official Document Directory

This reference guide maps out the structural organization of official Japan Sumo Association (JSA) documents, static web assets, regulatory frameworks, and statistical data sources for future research.

## 1. Primary JSA Server Directory Paths

The JSA hosts static files on `www.sumo.or.jp` across structured subdirectories. While direct folder indexing is hidden, files are accessible via standard path formats:

### `https://www.sumo.or.jp/pdf/kyokai/` (Governance & Corporate Operations)

* **`寄附行為` (*Kifukōi* / Articles of Incorporation):** Administrative rules governing JSA directors, stable masters (*oyakata*), and official business operations.

* **`2013nyumonhen.pdf` (Introductory Guide to Sumo):** Official educational document detailing division progressions, training standards, and promotion flows (including *Ōzeki* and *Yokozuna* advancement).

* **`price_list.pdf`:** Ticket pricing, arena tiering rules, and venue seating classifications across tournament locations.

### `https://www.sumo.or.jp/pdf/honbasho/` (Tournament Operations & Match Data)

* **`betsuhyoYYYYMMen.pdf`:** Match brackets, schedules, and daily division operational layouts (e.g., `betsuhyo201607en.pdf`).

* **`kansen/`:** Venue-specific arena maps, seating layouts, and operational rules for Tokyo (*Kokugikan*), Osaka, Nagoya, and Fukuoka arenas.

* **`YYYY_jul_history.pdf`:** Historical overview sheets and traditional ring ceremony guides (*Dohyō Sahō*).

### `https://www.sumo.or.jp/pdf/en/` (English Public Documentation)

* **`sumo_introduction.pdf`:** Concise summary covering ranking divisions, hair/attire rules, ring rituals, and basic match procedures.

* **`sumo_ticket_fee.pdf`:** English pricing structures and box seat (*masu-seki*) classification documents.

## 2. Core Operational & Rule Frameworks

Grand Sumo governance relies on three primary categories of rules, bylaws, and precedents:

### A. Rank Movement & Promotion Guidelines

* **Banzuke Creation Guidelines (*Banzuke Hensei Yōryō* / 番付編成要領):** Internal Judging Committee (*Shimpan-bu*) guidelines used after each tournament to draft the new rankings sheet based on net win/loss margins (*Kachi-koshi* vs. *Make-koshi*).

* **Ōzeki Promotion Benchmark & Protocol (*Ōzeki Jōshō* / 大関昇進):**
  * **Informal Benchmark:** Achieving **33 wins over 3 consecutive tournaments** while positioned in *Sanyaku* (*Sekiwake* or *Komusubi*).
  * **Formal Process:** Unlike lower ranks (which move automatically based on score), *Ōzeki* promotion requires a meeting of the **Ranking Committee (*Banzuke Hensei Kaigi*)**, approval by the **JSA Board of Directors (*Rijikai*)**, and an official envoy delivery ceremony (*Shōshin Dentatsushiki*).
  * **Official JSA Path:** JSA news releases announce these under `IrohaKyokaiInformation/detail?id=...` (e.g., "新大関誕生" / "New Ōzeki Announcement").

* **Yokozuna Deliberation Council Internal Regulations (*Yokozuna Shingi Iinkai Naiki* / 横綱審議委員会内規):** Codified rules established in 1950 setting promotion criteria to *Yokozuna* (historically requiring two consecutive *Makuuchi* championships or equivalent performance).

* **Special Re-promotion Rule (*Tokurei Fukki* / 特例復帰):** Automatic re-promotion rule for a demoted *Ōzeki* who achieves 10+ wins in their immediate subsequent tournament as *Sekiwake*.

### B. Match Mechanics & Prohibitions

* **Recognized Winning Techniques (*Kimarite* / 決まり手):** The 82 official techniques and 5 non-technique winning outcomes recognized by the JSA.

* **Prohibited Actions (*Kinjite* / 禁じ手):** Illegal moves (hair pulling, eye gouging, striking with a closed fist, kicking in the chest/stomach) leading to immediate disqualification (*Hansoku*).

* **Bout Restart Triggers (*Torinaoshi* / 取り直し):** Official referee/judging protocols for handling simultaneous ringouts or dead-heats (*Dōtai*).

## 3. Official Tournament Records & Statistics

| Source Type | Japanese Term | URL Structure / Path | Description |
| ----- | ----- | ----- | ----- |
| **Official Ranking Sheet** | 番付表 (*Banzuke*) | `/ResultBanzuke/table/` | Bimonthly ranking list of all active wrestlers, referees, and ring announcers. |
| **Daily Score Sheet** | 星取表 (*Hoshitori-hyō*) | JSA Match Results Portal | Daily record of bouts, win/loss markers (white/black circles), and winning techniques used. |
| **Sponsorship Breakdown** | 懸賞金 (*Kenshōkin*) | Tournament Program Guides | Lists of corporate match sponsorship banners and cash prize assignments for top-tier bouts. |

## 4. Key Search Terms for Manual Server Discovery

When attempting to locate specific Japanese-language PDFs or administrative announcements on the JSA server, combine targeted terms with standard date suffixes (`YYYYMM` format):

```
site:sumo.or.jp/pdf/ "大関昇進"       (Ōzeki promotion references)
site:sumo.or.jp/pdf/ "番付編成要領"   (Banzuke creation guidelines)
site:sumo.or.jp/pdf/ "寄附行為"       (JSA constitution/governance)
site:sumo.or.jp/pdf/ "決まり手"       (Winning techniques guide)
site:sumo.or.jp/pdf/ "禁じ手"         (Illegal actions/fouls)
site:sumo.or.jp/pdf/ "横綱審議"       (Yokozuna Deliberation Council docs)
```
