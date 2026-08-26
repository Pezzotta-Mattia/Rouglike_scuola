import math
import random
import pygame
from classi import STATISTICHE_CLASSI


def linea_di_vista(x0, y0, x1, y1, mappa):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            if (x != x0 or y != y0) and (x != x1 or y != y1):
                if mappa[y][x] == 1:
                    return False
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            if (x != x0 or y != y0) and (x != x1 or y != y1):
                if mappa[y][x] == 1:
                    return False
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy

    return True


def verifica_percorso(mappa, start_x, start_y, punti_da_raggiungere):
    righe = len(mappa)
    colonne = len(mappa[0])

    coda = [(start_x, start_y)]
    visitati = set([(start_x, start_y)])
    direzioni = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    punti_trovati = set()
    if (start_x, start_y) in punti_da_raggiungere:
        punti_trovati.add((start_x, start_y))

    while coda:
        x, y = coda.pop(0)

        for dx, dy in direzioni:
            nx, ny = x + dx, y + dy

            if 0 <= nx < colonne and 0 <= ny < righe:
                if mappa[ny][nx] != 1 and (nx, ny) not in visitati:
                    visitati.add((nx, ny))
                    coda.append((nx, ny))

                    if (nx, ny) in punti_da_raggiungere:
                        punti_trovati.add((nx, ny))

    return len(punti_trovati) == len(punti_da_raggiungere)


def creamappe(righe, colonne):
    stanze = []

    for i in range(6):
        mappa = [[0 for _ in range(colonne)] for _ in range(righe)]

        if i == 4:
            for y in range(righe):
                for x in range(colonne):
                    if y == 0 or y == righe - 1 or x == 0 or x == colonne - 1:
                        mappa[y][x] = 1
            mappa[0][colonne // 2] = 2
            mappa[righe - 1][colonne // 2] = 5
            stanze.append(mappa)
            continue

        elif i == 5:
            for y in range(righe):
                for x in range(colonne):
                    if y == 0 or y == righe - 1 or x == 0 or x == colonne - 1:
                        mappa[y][x] = 1
            mappa[righe - 1][colonne // 2] = 5
            mappa[righe // 2][colonne // 2] = 7
            stanze.append(mappa)
            continue

        while True:
            mappa = [[0 for _ in range(colonne)] for _ in range(righe)]

            for y in range(righe):
                for x in range(colonne):
                    if y == 0 or y == righe - 1 or x == 0 or x == colonne - 1:
                        mappa[y][x] = 1

            pos_porta_avanti = (colonne // 2, 0)
            pos_porta_indietro = (colonne // 2, righe - 1)
            pos_spawn_basso = (colonne // 2, righe - 2)
            pos_spawn_alto = (colonne // 2, 1)

            for y in range(1, righe - 1):
                for x in range(1, colonne - 1):
                    if (x, y) not in (pos_spawn_basso, pos_spawn_alto):
                        if random.random() < 0.15:
                            mappa[y][x] = 1

            mappa[pos_porta_avanti[1]][pos_porta_avanti[0]] = 2

            punti_da_verificare = [pos_porta_avanti]

            if i > 0:
                mappa[pos_porta_indietro[1]][pos_porta_indietro[0]] = 5
                punti_da_verificare.append(pos_porta_indietro)

            if verifica_percorso(
                mappa,
                pos_spawn_basso[0],
                pos_spawn_basso[1],
                punti_da_verificare,
            ):
                stanze.append(mappa)
                break

    return stanze


def genera_nemici_per_stanza(mappa, stanza_idx, player_x, player_y):
    if stanza_idx == 4:
        return [Boss(x=8, y=5)]
    elif stanza_idx == 5:
        return []

    quantita = stanza_idx + 1
    righe = len(mappa)
    colonne = len(mappa[0])
    nemici = []

    caselle_valide = []
    for y in range(1, righe - 1):
        for x in range(1, colonne - 1):
            if mappa[y][x] == 0 and (x, y) != (player_x, player_y):
                caselle_valide.append((x, y))

    posizioni_scelte = random.sample(
        caselle_valide, min(quantita, len(caselle_valide))
    )

    for px, py in posizioni_scelte:
        nemici.append(Nemici(px, py, raggio=5 + stanza_idx * 2))

    return nemici


def disegnamappa(righe, colonne, mappa, dimensione, schermo):
    NERO = (0, 0, 0)
    VERDE = (30, 40, 35)
    GRIGIO = (80, 85, 95)
    ROSSO = (200, 50, 50)
    GIALLO = (255, 215, 0)
    VIOLA = (120, 40, 140)
    AZZURRO = (0, 200, 255)

    for y in range(righe):
        for x in range(colonne):
            pos_x = x * dimensione
            pos_y = y * dimensione
            rettangolo = pygame.Rect(pos_x, pos_y, dimensione, dimensione)

            valore = mappa[y][x]

            if valore == 0:
                colore = VERDE
            elif valore == 1:
                colore = GRIGIO
            elif valore == 2:
                colore = ROSSO
            elif valore == 4:
                colore = GIALLO
            elif valore == 5:
                colore = VIOLA
            elif valore == 6:
                colore = AZZURRO
            elif valore == 7:
                colore = VERDE
            else:
                colore = VERDE

            pygame.draw.rect(schermo, colore, rettangolo)
            pygame.draw.rect(schermo, NERO, rettangolo, 1)

            if valore == 7:
                cx = pos_x + dimensione // 2
                cy = pos_y + dimensione // 2
                pygame.draw.polygon(
                    schermo,
                    (255, 215, 0),
                    [(cx - 10, cy - 10), (cx + 10, cy - 10), (cx, cy + 4)],
                )
                pygame.draw.rect(schermo, (255, 215, 0), (cx - 3, cy + 4, 6, 8))
                pygame.draw.rect(schermo, (255, 215, 0), (cx - 8, cy + 12, 16, 4))


class Giocatore:

    def __init__(self, x, y, nome_classe, forma=None):
        self.x = x
        self.y = y
        self.nome_classe = nome_classe
        self.forma = forma

        self.stats = STATISTICHE_CLASSI.get(nome_classe, {})
        self.hp_max = self.stats.get("hp_max", 100)
        self.hp = self.hp_max

        if self.nome_classe == "Tank":
            self.raggio_attacco = 1
        else:
            self.raggio_attacco = self.stats.get("raggio_attacco", 1)

        self.has_mana = self.stats.get("has_mana", False)
        if self.has_mana:
            self.mana_max = self.stats.get("mana_max", 100)
            self.mana = self.mana_max
            self.mana_rigenerazione_sec = self.stats.get(
                "mana_rigenerazione_sec", 3
            )
            self.ultimo_tick_mana = pygame.time.get_ticks()
        else:
            self.mana_max = 0
            self.mana = 0

        self.attacco = self.stats.get("danno_base", 10)
        self.velocita = self.stats.get("velocita_moltiplicatore", 1.0)

        self.trasformato = False
        self.tempo_fine_trasformazione = 0

        self.invisibile = False
        self.tempo_fine_invisibilita = 0

        self.durata_buff_guerriero = 0

        self.info_abilita = self.stats.get("abilita", {})
        self.usi_max_abilita = self.info_abilita.get("usi_max", 0)
        self.usi_rimanenti_abilita = self.usi_max_abilita

        self.effetti_attacco = []
        self.ultima_direzione = (0, 1)

    def subisci_danno(self, danno):
        if self.invisibile:
            return
        self.hp -= danno
        if self.hp <= 0:
            self.hp = 0

    def aggiorna_stato_tempo_reale(self):
        tempo_attuale = pygame.time.get_ticks()

        if self.has_mana and self.mana < self.mana_max:
            if tempo_attuale - self.ultimo_tick_mana >= 1000:
                self.mana = min(
                    self.mana_max, self.mana + self.mana_rigenerazione_sec
                )
                self.ultimo_tick_mana = tempo_attuale

        if self.trasformato and tempo_attuale >= self.tempo_fine_trasformazione:
            self.trasformato = False

        if self.invisibile and tempo_attuale >= self.tempo_fine_invisibilita:
            self.invisibile = False

    def scala_turni(self):
        if self.durata_buff_guerriero > 0:
            self.durata_buff_guerriero -= 1
            if self.durata_buff_guerriero == 0:
                self.attacco -= self.info_abilita.get("danno_buff", 30)

    def aggiungi_effetto(self, x, y, colore=(255, 255, 0), durata_ms=150):
        tempo_fine = pygame.time.get_ticks() + durata_ms
        self.effetti_attacco.append(
            {"x": x, "y": y, "colore": colore, "fine": tempo_fine}
        )

    def aggiorna_effetti(self):
        tempo_attuale = pygame.time.get_ticks()
        self.effetti_attacco = [
            e for e in self.effetti_attacco if tempo_attuale < e["fine"]
        ]

    def attacco_base(self, nemici, mappa):
        danno = self.attacco
        raggio = self.raggio_attacco

        if self.nome_classe == "Assassino":
            arma_info = self.stats.get("armi", {}).get("Pugnale", {})
            raggio = arma_info.get("raggio", 1)
            danno = arma_info.get("danno_base", 10)
            if random.random() < arma_info.get("crit_prob", 0.10):
                danno += arma_info.get("crit_danno", 40)

        colpito = False
        for nemico in nemici:
            if nemico.vivo:
                if nemico.colpito_da(self.x, self.y, raggio, mappa):
                    era_vivo = nemico.vivo
                    nemico.subisci_danno(danno)
                    self.aggiungi_effetto(nemico.x, nemico.y, (255, 200, 0))
                    colpito = True

                    if era_vivo and not nemico.vivo and self.nome_classe == "Assassino":
                        self.hp = min(self.hp_max, self.hp + 5)
                        self.aggiungi_effetto(self.x, self.y, (0, 255, 0))

        if not colpito:
            self.aggiungi_effetto(
                self.x, self.y, (200, 200, 200), durata_ms=100
            )

        self.scala_turni()

    def abilita_spazio(self, nemici, mappa):
        if self.nome_classe == "Mago":
            self.incantesimo_scia_oscura(nemici, mappa)
            return

        if self.usi_rimanenti_abilita <= 0:
            return

        tempo_attuale = pygame.time.get_ticks()

        if self.nome_classe == "Guerriero":
            self.usi_rimanenti_abilita -= 1
            cura = self.info_abilita.get("cura", 15)
            buff = self.info_abilita.get("danno_buff", 30)
            self.hp = min(self.hp_max, self.hp + cura)
            self.attacco += buff
            self.durata_buff_guerriero = self.info_abilita.get("durata", 10)
            self.aggiungi_effetto(self.x, self.y, (255, 100, 0))

        elif self.nome_classe == "Tank":
            self.usi_rimanenti_abilita -= 1
            self.hp = self.hp_max
            self.aggiungi_effetto(self.x, self.y, (0, 255, 0))

        elif self.nome_classe == "Assassino":
            self.usi_rimanenti_abilita -= 1
            self.invisibile = True
            self.tempo_fine_invisibilita = tempo_attuale + 5000
            self.aggiungi_effetto(self.x, self.y, (220, 220, 255))

        elif self.nome_classe == "Mutaforma":
            self.usi_rimanenti_abilita -= 1
            self.trasformato = True
            self.tempo_fine_trasformazione = tempo_attuale + 10000
            self.aggiungi_effetto(self.x, self.y, (180, 0, 255))

        self.scala_turni()

    def abilita_tasto_destro(self, nemici, mappa):
        if self.nome_classe == "Mago":
            self.incantesimo_fulmine(nemici, mappa)
            return

        elif self.nome_classe == "Assassino":
            arma_info = self.stats.get("armi", {}).get(
                "Coltello da lancio", {}
            )
            raggio = arma_info.get("raggio", 4)
            danno = arma_info.get("danno_base", 3)
            if random.random() < arma_info.get("crit_prob", 0.25):
                danno += arma_info.get("crit_danno", 10)

            for nemico in nemici:
                if nemico.vivo and nemico.colpito_da(
                    self.x, self.y, raggio, mappa
                ):
                    era_vivo = nemico.vivo
                    nemico.subisci_danno(danno)
                    self.aggiungi_effetto(nemico.x, nemico.y, (200, 200, 255))

                    if era_vivo and not nemico.vivo:
                        self.hp = min(self.hp_max, self.hp + 5)
                        self.aggiungi_effetto(self.x, self.y, (0, 255, 0))
                    break

        elif self.nome_classe == "Mutaforma" and self.trasformato:
            if self.forma == "Centauro":
                self.abilita_centauro_carica(nemici, mappa)
            else:
                forma_info = (
                    self.stats.get("forme", {})
                    .get(self.forma, {})
                    .get("abilita_speciale", {})
                )
                raggio = forma_info.get("raggio", 2)
                danno = forma_info.get(
                    "danno", forma_info.get("danno_immediato", 20)
                )

                for nemico in nemici:
                    if nemico.vivo and nemico.colpito_da(
                        self.x, self.y, raggio, mappa
                    ):
                        nemico.subisci_danno(danno)
                        self.aggiungi_effetto(nemico.x, nemico.y, (255, 0, 0))

        self.scala_turni()

    def abilita_centauro_carica(self, nemici, mappa):
        dx, dy = self.ultima_direzione
        if dx == 0 and dy == 0:
            dx, dy = 0, 1

        danno = 25
        caselle_attraversate = []

        for _ in range(4):
            nx, ny = self.x + dx, self.y + dy
            if (
                0 <= nx < len(mappa[0])
                and 0 <= ny < len(mappa)
                and mappa[ny][nx] != 1
            ):
                self.x, self.y = nx, ny
                caselle_attraversate.append((nx, ny))
            else:
                break

        for nemico in nemici:
            if nemico.vivo:
                for cx, cy in caselle_attraversate:
                    dist = abs(nemico.x - cx) + abs(nemico.y - cy)
                    if dist <= 1:
                        nemico.subisci_danno(danno)
                        self.aggiungi_effetto(nemico.x, nemico.y, (255, 100, 0))
                        break

    def incantesimo_cura(self):
        costo = (
            self.stats.get("incantesimi", {})
            .get("Cura", {})
            .get("costo_mana", 10)
        )
        if self.mana >= costo:
            self.mana -= costo
            cura = self.stats["incantesimi"]["Cura"].get("cura", 5)
            self.hp = min(self.hp_max, self.hp + cura)
            self.aggiungi_effetto(self.x, self.y, (0, 255, 100))
            self.scala_turni()

    def incantesimo_repulsione(self, nemici, mappa):
        costo = (
            self.stats.get("incantesimi", {})
            .get("Repulsione", {})
            .get("costo_mana", 20)
        )
        if self.mana >= costo:
            self.mana -= costo
            info = self.stats["incantesimi"]["Repulsione"]
            raggio = info.get("raggio_rilevamento", 3)
            danno = info.get("danno", 2)
            blocchi_spinta = info.get("spinta_blocchi", 2)

            for nemico in nemici:
                if nemico.vivo and nemico.colpito_da(
                    self.x, self.y, raggio, mappa
                ):
                    nemico.subisci_danno(danno)
                    self.aggiungi_effetto(nemico.x, nemico.y, (0, 200, 255))

                    dir_x = nemico.x - self.x
                    dir_y = nemico.y - self.y
                    step_x = 1 if dir_x > 0 else (-1 if dir_x < 0 else 0)
                    step_y = 1 if dir_y > 0 else (-1 if dir_y < 0 else 0)

                    for _ in range(blocchi_spinta):
                        nx = nemico.x + step_x
                        ny = nemico.y + step_y
                        if (
                            0 <= nx < len(mappa[0])
                            and 0 <= ny < len(mappa)
                            and mappa[ny][nx] != 1
                        ):
                            nemico.x = nx
                            nemico.y = ny
                        else:
                            break

            self.scala_turni()

    def incantesimo_scia_oscura(self, nemici, mappa):
        costo = (
            self.stats.get("incantesimi", {})
            .get("Scia Oscura", {})
            .get("costo_mana", 15)
        )
        if self.mana >= costo:
            self.mana -= costo
            info = self.stats.get("incantesimi", {}).get("Scia Oscura", {})
            raggio = info.get("distanza", 5)
            danno = info.get("danno", 15)

            for nemico in nemici:
                if nemico.vivo and nemico.colpito_da(
                    self.x, self.y, raggio, mappa
                ):
                    nemico.subisci_danno(danno)
                    self.aggiungi_effetto(nemico.x, nemico.y, (150, 0, 200))
                    break
            self.scala_turni()

    def incantesimo_fulmine(self, nemici, mappa):
        costo = (
            self.stats.get("incantesimi", {})
            .get("Fulmine", {})
            .get("costo_mana", 10)
        )
        if self.mana >= costo:
            self.mana -= costo
            info = self.stats.get("incantesimi", {}).get("Fulmine", {})
            raggio = info.get("distanza", 5)
            danno = info.get("danno", 5)

            for nemico in nemici:
                if nemico.vivo and nemico.colpito_da(
                    self.x, self.y, raggio, mappa
                ):
                    nemico.subisci_danno(danno)
                    self.aggiungi_effetto(nemico.x, nemico.y, (255, 255, 0))
                    break
            self.scala_turni()

    def reset_stanza(self):
        if self.has_mana:
            self.mana = self.mana_max

        if self.info_abilita.get("tipo_cooldown") == "stanza":
            self.usi_rimanenti_abilita = self.usi_max_abilita


class Nemici:

    def __init__(self, x, y, raggio, hp=40, attacco=15):
        self.x = x
        self.y = y
        self.raggio = raggio
        self.hp_max = hp
        self.hp = hp
        self.attacco = attacco
        self.vivo = True
        self.is_boss = False

    def subisci_danno(self, quantita):
        self.hp -= quantita
        if self.hp <= 0:
            self.hp = 0
            self.vivo = False

    def colpito_da(self, px, py, raggio, mappa):
        distanza = abs(px - self.x) + abs(py - self.y)
        return distanza <= raggio and linea_di_vista(
            px, py, self.x, self.y, mappa
        )

    def Inseguimento(self, player_x, player_y, mappa, giocatore):
        if not self.vivo or (giocatore and giocatore.invisibile):
            return

        distanzax = abs(player_x - self.x)
        distanzay = abs(player_y - self.y)
        distanza_totale = distanzax + distanzay

        if distanza_totale == 1:
            giocatore.subisci_danno(self.attacco)
            giocatore.aggiungi_effetto(
                giocatore.x, giocatore.y, (255, 0, 0), durata_ms=200
            )
            return

        if distanzax > self.raggio or distanzay > self.raggio:
            return

        dx = 1 if player_x > self.x else (-1 if player_x < self.x else 0)
        dy = 1 if player_y > self.y else (-1 if player_y < self.y else 0)

        if distanzax > distanzay:
            dy = 0
        else:
            dx = 0

        nuova_x = self.x + dx
        nuova_y = self.y + dy

        if (nuova_x, nuova_y) == (player_x, player_y):
            giocatore.subisci_danno(self.attacco)
            giocatore.aggiungi_effetto(
                giocatore.x, giocatore.y, (255, 0, 0), durata_ms=200
            )
            return

        if 0 <= nuova_x < len(mappa[0]) and 0 <= nuova_y < len(mappa):
            if mappa[nuova_y][nuova_x] not in (1, 2, 4, 5, 6, 7):
                self.x = nuova_x
                self.y = nuova_y

    def disegnanemico(self, schermo, dimensione):
        if not self.vivo:
            return
        cx = self.x * dimensione + dimensione // 2
        cy = self.y * dimensione + dimensione // 2
        r = dimensione // 2 - 4

        pygame.draw.circle(schermo, (200, 40, 40), (cx, cy), r)
        pygame.draw.circle(schermo, (100, 0, 0), (cx, cy), r, width=2)
        pygame.draw.circle(schermo, (255, 220, 0), (cx - 4, cy - 3), 3)
        pygame.draw.circle(schermo, (255, 220, 0), (cx + 4, cy - 3), 3)


class Boss(Nemici):

    def __init__(self, x, y):
        super().__init__(x, y, raggio=15, hp=500, attacco=20)
        self.is_boss = True
        self.danno_speciale = 30

        tempo_attuale = pygame.time.get_ticks()
        self.ultimo_attacco_normale = tempo_attuale
        self.ultimo_attacco_speciale = tempo_attuale

        self.caricamento_normale = False
        self.fine_caricamento_normale = 0

        self.caricamento_speciale = False
        self.fine_caricamento_speciale = 0
        self.mira_x = None
        self.mira_y = None

    def caselle_occupate(self):
        return [
            (self.x, self.y),
            (self.x + 1, self.y),
            (self.x, self.y + 1),
            (self.x + 1, self.y + 1),
        ]

    def e_adiacente(self, px, py):
        for bx, by in self.caselle_occupate():
            if abs(px - bx) + abs(py - by) == 1:
                return True
        return False

    def colpito_da(self, px, py, raggio, mappa):
        for bx, by in self.caselle_occupate():
            distanza = abs(px - bx) + abs(py - by)
            if distanza <= raggio and linea_di_vista(px, py, bx, by, mappa):
                return True
        return False

    def Inseguimento(self, player_x, player_y, mappa, giocatore):
        if not self.vivo or (giocatore and giocatore.invisibile):
            return

        tempo_attuale = pygame.time.get_ticks()

        if (
            tempo_attuale - self.ultimo_attacco_speciale >= 10000
            and not self.caricamento_speciale
        ):
            self.caricamento_speciale = True
            self.fine_caricamento_speciale = tempo_attuale + 1000
            self.mira_x = player_x
            self.mira_y = player_y
            self.ultimo_attacco_speciale = tempo_attuale

        if self.caricamento_speciale:
            giocatore.aggiungi_effetto(
                self.mira_x, self.mira_y, (255, 0, 0), durata_ms=100
            )
            if tempo_attuale >= self.fine_caricamento_speciale:
                self.caricamento_speciale = False
                if (
                    player_x == self.mira_x and player_y == self.mira_y
                ) or linea_di_vista(self.x, self.y, player_x, player_y, mappa):
                    giocatore.subisci_danno(self.danno_speciale)

        if (
            tempo_attuale - self.ultimo_attacco_normale >= 4000
            and not self.caricamento_normale
        ):
            self.caricamento_normale = True
            self.fine_caricamento_normale = tempo_attuale + 1000
            self.ultimo_attacco_normale = tempo_attuale

        if self.caricamento_normale:
            if tempo_attuale >= self.fine_caricamento_normale:
                self.caricamento_normale = False
                if self.e_adiacente(player_x, player_y):
                    giocatore.subisci_danno(self.attacco)
                    giocatore.aggiungi_effetto(
                        giocatore.x, giocatore.y, (255, 0, 0), durata_ms=200
                    )

        if not self.e_adiacente(player_x, player_y):
            dx = 1 if player_x > self.x else (-1 if player_x < self.x else 0)
            dy = 1 if player_y > self.y else (-1 if player_y < self.y else 0)

            if abs(player_x - self.x) > abs(player_y - self.y):
                dy = 0
            else:
                dx = 0

            nx, ny = self.x + dx, self.y + dy
            valida = True
            for bx, by in [
                (nx, ny),
                (nx + 1, ny),
                (nx, ny + 1),
                (nx + 1, ny + 1),
            ]:
                if not (
                    0 <= bx < len(mappa[0])
                    and 0 <= by < len(mappa)
                    and mappa[by][bx] != 1
                ):
                    valida = False
                    break
            if valida:
                self.x, self.y = nx, ny

    def disegnanemico(self, schermo, dimensione):
        if not self.vivo:
            return

        x_px = self.x * dimensione
        y_px = self.y * dimensione
        larghezza = dimensione * 2

        rect = pygame.Rect(x_px + 2, y_px + 2, larghezza - 4, larghezza - 4)
        colore_boss = (
            (255, 200, 0) if self.caricamento_normale else (140, 20, 20)
        )

        pygame.draw.rect(schermo, colore_boss, rect, border_radius=12)
        pygame.draw.rect(
            schermo, (255, 215, 0), rect, width=4, border_radius=12
        )

        cx = x_px + dimensione
        cy = y_px + dimensione
        pygame.draw.circle(schermo, (255, 255, 255), (cx, cy), 14)
        pygame.draw.circle(schermo, (255, 0, 0), (cx, cy), 8)
        pygame.draw.circle(schermo, (0, 0, 0), (cx, cy), 4)

        percentuale = max(0, self.hp / self.hp_max)
        bar_w = larghezza
        bar_h = 6
        bar_x = x_px
        bar_y = y_px - 10
        pygame.draw.rect(schermo, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(
            schermo,
            (255, 0, 0),
            (bar_x, bar_y, int(bar_w * percentuale), bar_h),
        )


def disegnaplayer(giocatore, dimensione, schermo):
    if not giocatore:
        return

    giocatore.aggiorna_stato_tempo_reale()

    cx = giocatore.x * dimensione + dimensione // 2
    cy = giocatore.y * dimensione + dimensione // 2
    raggio = dimensione // 2 - 4

    if giocatore.nome_classe == "Mago":
        pygame.draw.circle(schermo, (140, 50, 200), (cx, cy), raggio)
        punti_cappello = [(cx, cy - raggio - 4), (cx - 10, cy), (cx + 10, cy)]
        pygame.draw.polygon(schermo, (50, 50, 220), punti_cappello)
        pygame.draw.circle(schermo, (0, 220, 255), (cx + 8, cy + 4), 4)

    elif giocatore.nome_classe == "Guerriero":
        rect = pygame.Rect(
            giocatore.x * dimensione + 4,
            giocatore.y * dimensione + 4,
            dimensione - 8,
            dimensione - 8,
        )
        colore = (220, 80, 40) if giocatore.durata_buff_guerriero > 0 else (180, 60, 60)
        pygame.draw.rect(schermo, colore, rect, border_radius=4)
        pygame.draw.line(
            schermo, (255, 215, 0), (cx - 8, cy + 8), (cx + 8, cy - 8), width=3
        )

    elif giocatore.nome_classe == "Tank":
        rect = pygame.Rect(
            giocatore.x * dimensione + 2,
            giocatore.y * dimensione + 2,
            dimensione - 4,
            dimensione - 4,
        )
        pygame.draw.rect(schermo, (40, 90, 180), rect, border_radius=8)
        pygame.draw.rect(
            schermo, (200, 200, 200), rect, width=3, border_radius=8
        )

    elif giocatore.nome_classe == "Assassino":
        punti = [(cx, cy - raggio), (cx - raggio, cy + raggio), (cx + raggio, cy + raggio)]
        if giocatore.invisibile:
            colore = (220, 220, 240)
            pygame.draw.polygon(schermo, colore, punti)
            pygame.draw.polygon(schermo, (255, 255, 255), punti, width=2)
        else:
            colore = (80, 80, 90)
            pygame.draw.polygon(schermo, colore, punti)

    elif giocatore.nome_classe == "Mutaforma":
        if not giocatore.trasformato:
            pygame.draw.circle(schermo, (40, 180, 80), (cx, cy), raggio)
            pygame.draw.circle(schermo, (255, 255, 255), (cx, cy), 4)
        else:
            if giocatore.forma == "Drago":
                punti_drago = [
                    (cx, cy - raggio - 2),
                    (cx + 5, cy - 4),
                    (cx + raggio, cy),
                    (cx + 5, cy + 4),
                    (cx, cy + raggio + 2),
                    (cx - 5, cy + 4),
                    (cx - raggio, cy),
                    (cx - 5, cy - 4),
                ]
                pygame.draw.polygon(schermo, (255, 100, 0), punti_drago)
                pygame.draw.circle(schermo, (255, 220, 0), (cx, cy), 5)

            elif giocatore.forma == "Serpente Gigante":
                punti_serpente = [
                    (cx, cy - raggio),
                    (cx + raggio - 2, cy),
                    (cx, cy + raggio),
                    (cx - raggio + 2, cy),
                ]
                pygame.draw.polygon(schermo, (0, 200, 120), punti_serpente)
                pygame.draw.line(
                    schermo, (255, 255, 255), (cx - 4, cy - 2), (cx - 4, cy + 2), width=2
                )
                pygame.draw.line(
                    schermo, (255, 255, 255), (cx + 4, cy - 2), (cx + 4, cy + 2), width=2
                )

            elif giocatore.forma == "Centauro":
                punti_centauro = [
                    (cx, cy - raggio),
                    (cx + raggio, cy - 4),
                    (cx + raggio - 3, cy + raggio),
                    (cx - raggio + 3, cy + raggio),
                    (cx - raggio, cy - 4),
                ]
                pygame.draw.polygon(schermo, (160, 90, 40), punti_centauro)
                pygame.draw.polygon(
                    schermo, (255, 215, 0), punti_centauro, width=2
                )


def disegna_effetti(schermo, giocatore, dimensione):
    for effetto in giocatore.effetti_attacco:
        px = effetto["x"] * dimensione
        py = effetto["y"] * dimensione
        surface = pygame.Surface((dimensione, dimensione), pygame.SRCALPHA)
        color_alpha = (*effetto["colore"], 160)
        surface.fill(color_alpha)
        schermo.blit(surface, (px, py))


def segnalino(schermo, stanza_attuale):
    BIANCO = (255, 255, 255)
    font = pygame.font.SysFont(None, 28)
    if stanza_attuale < 4:
        testo_str = f"Stanza {stanza_attuale + 1}"
    elif stanza_attuale == 4:
        testo_str = "STANZA BOSS!"
    else:
        testo_str = "STANZA DEL TESORO"

    superficie_testo = font.render(
        testo_str,
        True,
        (255, 215, 0) if stanza_attuale == 5 else (255, 50, 50) if stanza_attuale == 4 else BIANCO,
    )
    schermo.blit(superficie_testo, (10, 10))


def disegna_hud(schermo, giocatore):
    if not giocatore:
        return

    ROSSO = (200, 40, 40)
    BLU = (40, 100, 220)
    GRIGIO_SCURO = (50, 50, 50)
    BIANCO = (255, 255, 255)

    font = pygame.font.SysFont("Arial", 14, bold=True)

    x_bar = schermo.get_width() - 170
    y_bar = 10
    larghezza_bar = 160
    altezza_bar = 16

    percentuale_hp = max(0, giocatore.hp / giocatore.hp_max)
    pygame.draw.rect(
        schermo, GRIGIO_SCURO, (x_bar, y_bar, larghezza_bar, altezza_bar)
    )
    pygame.draw.rect(
        schermo,
        ROSSO,
        (x_bar, y_bar, int(larghezza_bar * percentuale_hp), altezza_bar),
    )
    pygame.draw.rect(
        schermo, BIANCO, (x_bar, y_bar, larghezza_bar, altezza_bar), 2
    )

    testo_hp = font.render(
        f"HP: {giocatore.hp}/{giocatore.hp_max}", True, BIANCO
    )
    schermo.blit(testo_hp, (x_bar + 5, y_bar + 1))

    if hasattr(giocatore, "mana_max") and giocatore.mana_max > 0:
        y_mana = y_bar + altezza_bar + 6
        percentuale_mana = max(0, giocatore.mana / giocatore.mana_max)

        pygame.draw.rect(
            schermo, GRIGIO_SCURO, (x_bar, y_mana, larghezza_bar, altezza_bar)
        )
        pygame.draw.rect(
            schermo,
            BLU,
            (x_bar, y_mana, int(larghezza_bar * percentuale_mana), altezza_bar),
        )
        pygame.draw.rect(
            schermo, BIANCO, (x_bar, y_mana, larghezza_bar, altezza_bar), 2
        )

        testo_mana = font.render(
            f"MANA: {giocatore.mana}/{giocatore.mana_max}", True, BIANCO
        )
        schermo.blit(testo_mana, (x_bar + 5, y_mana + 1))