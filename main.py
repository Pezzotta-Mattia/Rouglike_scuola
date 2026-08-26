import random
import sys
import pygame
from classi import STATISTICHE_CLASSI
import funzioni

pygame.init()
pygame.font.init()

# Dimensioni ridimensionate: Menu compatto ma ben leggibile, Gioco aderente alla mappa
DIM_MENU_W, DIM_MENU_H = 900, 650
DIM_GIOCO_W, DIM_GIOCO_H = 720, 720  # 18 celle * 40 px

schermo = pygame.display.set_mode((DIM_MENU_W, DIM_MENU_H))
pygame.display.set_caption("Dungeon Crawler - Treasure Room")

FONT_TITOLO = pygame.font.SysFont("Arial", 30, bold=True)
FONT_SUBTITOLO = pygame.font.SysFont("Arial", 18, bold=True)
FONT_OPZIONI = pygame.font.SysFont("Arial", 22)
FONT_INFO = pygame.font.SysFont("Arial", 15)
FONT_CONSIGLIO = pygame.font.SysFont("Arial", 17, bold=True)

RIGHE = 18
COLONNE = 18
DIM_CELLA = 40

NERO = (0, 0, 0)
BIANCO = (255, 255, 255)
GIALLO = (255, 215, 0)
GRIGIO = (170, 170, 170)
ROSSO = (220, 50, 50)
VERDE = (80, 220, 100)
AZZURRO = (100, 200, 255)

classi = list(STATISTICHE_CLASSI.keys())
creature = ["Drago", "Serpente Gigante", "Centauro"]

orologio = pygame.time.Clock()


def reset_gioco():
    stanze = funzioni.creamappe(RIGHE, COLONNE)
    stato = [False] * 6
    numero_stanza = 0

    p_x = COLONNE // 2
    p_y = RIGHE - 2

    nemici_stanze = [
        funzioni.genera_nemici_per_stanza(stanze[i], i, p_x, p_y)
        for i in range(6)
    ]

    return stanze, stato, numero_stanza, p_x, p_y, nemici_stanze


def imposta_dimensione_schermo(larghezza, altezza):
    global schermo
    if schermo.get_width() != larghezza or schermo.get_height() != altezza:
        schermo = pygame.display.set_mode((larghezza, altezza))


stanze, stato, numero_stanza, player_x, player_y, nemici_stanze = reset_gioco()

stato_gioco = "MENU_REGOLE"
indice_selezionato = 0
indice_creatura = 0

classe_scelta = None
creatura_scelta = None
giocatore = None

esecuzione = True
while esecuzione:
    if stato_gioco in ("MENU_REGOLE", "MENU_CLASSE", "MENU_MUTAFORMA"):
        imposta_dimensione_schermo(DIM_MENU_W, DIM_MENU_H)
    else:
        imposta_dimensione_schermo(DIM_GIOCO_W, DIM_GIOCO_H)

    l_corrente = schermo.get_width()
    h_corrente = schermo.get_height()

    mappa_attuale = stanze[numero_stanza]
    nemici_correnti = nemici_stanze[numero_stanza]

    tutti_morti = all(not n.vivo for n in nemici_correnti)
    if tutti_morti and numero_stanza < 5:
        if mappa_attuale[0][COLONNE // 2] == 2:
            mappa_attuale[0][COLONNE // 2] = 4
            if mappa_attuale[RIGHE - 1][COLONNE // 2] == 5:
                mappa_attuale[RIGHE - 1][COLONNE // 2] = 6
            stato[numero_stanza] = True

    if giocatore and giocatore.hp <= 0 and stato_gioco == "IN_GIOCO":
        stato_gioco = "GAME_OVER"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            esecuzione = False

        elif event.type == pygame.MOUSEBUTTONDOWN and stato_gioco == "IN_GIOCO":
            if event.button == 1:
                giocatore.attacco_base(nemici_correnti, mappa_attuale)
            elif event.button == 3:
                giocatore.abilita_tasto_destro(nemici_correnti, mappa_attuale)

        elif event.type == pygame.KEYDOWN:
            if stato_gioco == "MENU_REGOLE":
                if event.key == pygame.K_RETURN:
                    stato_gioco = "MENU_CLASSE"

            elif stato_gioco == "MENU_CLASSE":
                if event.key == pygame.K_UP:
                    indice_selezionato = (indice_selezionato - 1) % len(classi)
                elif event.key == pygame.K_DOWN:
                    indice_selezionato = (indice_selezionato + 1) % len(classi)
                elif event.key == pygame.K_RETURN:
                    classe_scelta = classi[indice_selezionato]
                    if classe_scelta == "Mutaforma":
                        stato_gioco = "MENU_MUTAFORMA"
                    else:
                        giocatore = funzioni.Giocatore(
                            x=player_x, y=player_y, nome_classe=classe_scelta
                        )
                        stato_gioco = "IN_GIOCO"

            elif stato_gioco == "MENU_MUTAFORMA":
                if event.key == pygame.K_UP:
                    indice_creatura = (indice_creatura - 1) % len(creature)
                elif event.key == pygame.K_DOWN:
                    indice_creatura = (indice_creatura + 1) % len(creature)
                elif event.key == pygame.K_RETURN:
                    creatura_scelta = creature[indice_creatura]
                    giocatore = funzioni.Giocatore(
                        x=player_x,
                        y=player_y,
                        nome_classe="Mutaforma",
                        forma=creatura_scelta,
                    )
                    stato_gioco = "IN_GIOCO"
                elif event.key == pygame.K_ESCAPE:
                    stato_gioco = "MENU_CLASSE"

            elif stato_gioco in ("GAME_OVER", "VITTORIA"):
                if event.key == pygame.K_r:
                    (
                        stanze,
                        stato,
                        numero_stanza,
                        player_x,
                        player_y,
                        nemici_stanze,
                    ) = reset_gioco()
                    giocatore = None
                    stato_gioco = "MENU_CLASSE"

            elif stato_gioco == "IN_GIOCO":
                if event.key == pygame.K_SPACE:
                    giocatore.abilita_spazio(nemici_correnti, mappa_attuale)
                elif event.key == pygame.K_q:
                    if giocatore.nome_classe == "Mago":
                        giocatore.incantesimo_cura()
                elif event.key == pygame.K_e:
                    if giocatore.nome_classe == "Mago":
                        giocatore.incantesimo_repulsione(
                            nemici_correnti, mappa_attuale
                        )
                elif event.key == pygame.K_r:
                    if giocatore.nome_classe == "Mago":
                        giocatore.incantesimo_scia_oscura(
                            nemici_correnti, mappa_attuale
                        )
                elif event.key == pygame.K_f:
                    if giocatore.nome_classe == "Mago":
                        giocatore.incantesimo_fulmine(
                            nemici_correnti, mappa_attuale
                        )

                nuova_x, nuova_y = player_x, player_y
                ha_mosso = False

                if event.key == pygame.K_w:
                    nuova_y -= 1
                    ha_mosso = True
                    giocatore.ultima_direzione = (0, -1)
                elif event.key == pygame.K_s:
                    nuova_y += 1
                    ha_mosso = True
                    giocatore.ultima_direzione = (0, 1)
                elif event.key == pygame.K_a:
                    nuova_x -= 1
                    ha_mosso = True
                    giocatore.ultima_direzione = (-1, 0)
                elif event.key == pygame.K_d:
                    nuova_x += 1
                    ha_mosso = True
                    giocatore.ultima_direzione = (1, 0)

                if ha_mosso and 0 <= nuova_x < COLONNE and 0 <= nuova_y < RIGHE:
                    valore_casella = mappa_attuale[nuova_y][nuova_x]

                    if valore_casella == 7:
                        stato_gioco = "VITTORIA"
                    elif valore_casella not in (1, 2, 5):
                        player_x, player_y = nuova_x, nuova_y
                        giocatore.x, giocatore.y = player_x, player_y
                        giocatore.scala_turni()

                        for nemico in nemici_correnti:
                            if nemico.vivo and random.random() < 0.7:
                                nemico.Inseguimento(
                                    player_x, player_y, mappa_attuale, giocatore
                                )

                if mappa_attuale[player_y][player_x] == 4:
                    if numero_stanza < len(stanze) - 1:
                        numero_stanza += 1
                        player_x = COLONNE // 2
                        player_y = RIGHE - 2
                        giocatore.x = player_x
                        giocatore.y = player_y

                        if not stato[numero_stanza]:
                            stanze[numero_stanza][RIGHE - 1][COLONNE // 2] = 5
                        else:
                            stanze[numero_stanza][RIGHE - 1][COLONNE // 2] = 6

                        giocatore.reset_stanza()

                elif mappa_attuale[player_y][player_x] == 6:
                    if numero_stanza > 0:
                        numero_stanza -= 1
                        player_x = COLONNE // 2
                        player_y = 1
                        giocatore.x = player_x
                        giocatore.y = player_y

                        giocatore.reset_stanza()

    schermo.fill(NERO)

    if stato_gioco == "MENU_REGOLE":
        titolo = FONT_TITOLO.render("REGOLE DEL GIOCO", True, GIALLO)
        schermo.blit(titolo, (l_corrente // 2 - titolo.get_width() // 2, 140))

        riga1 = "Per battere il gioco occorre superare varie stanze e battere il boss finale,"
        riga2 = "solo sconfiggendo tutti i nemici di una stanza potrete accedere alla prossima. Buona avventura!"

        surf_riga1 = FONT_SUBTITOLO.render(riga1, True, BIANCO)
        surf_riga2 = FONT_SUBTITOLO.render(riga2, True, BIANCO)

        schermo.blit(surf_riga1, (l_corrente // 2 - surf_riga1.get_width() // 2, 240))
        schermo.blit(surf_riga2, (l_corrente // 2 - surf_riga2.get_width() // 2, 280))

        prompt = FONT_OPZIONI.render(
            'premere "INVIO" per selezionare il personaggio', True, VERDE
        )
        schermo.blit(prompt, (l_corrente // 2 - prompt.get_width() // 2, 420))

    elif stato_gioco == "MENU_CLASSE":
        titolo = FONT_TITOLO.render("SCEGLI LA TUA CLASSE", True, BIANCO)
        schermo.blit(titolo, (l_corrente // 2 - titolo.get_width() // 2, 25))

        for i, nome_classe in enumerate(classi):
            colore = GIALLO if i == indice_selezionato else BIANCO
            testo = FONT_OPZIONI.render(
                f"> {nome_classe}" if i == indice_selezionato else nome_classe,
                True,
                colore,
            )
            schermo.blit(testo, (60, 90 + i * 40))

        classe_corrente = classi[indice_selezionato]
        info_classe = STATISTICHE_CLASSI[classe_corrente]

        y_dettagli = 90
        x_dettagli = 310

        titolo_dettagli = FONT_SUBTITOLO.render(
            f"--- {classe_corrente.upper()} ---", True, GIALLO
        )
        schermo.blit(titolo_dettagli, (x_dettagli, y_dettagli))
        y_dettagli += 30

        hp_txt = FONT_OPZIONI.render(
            f"HP MAX: {info_classe['hp_max']}", True, ROSSO
        )
        schermo.blit(hp_txt, (x_dettagli, y_dettagli))
        y_dettagli += 30

        if info_classe.get("has_mana", False):
            mana_txt = FONT_INFO.render(
                f"MANA MAX: {info_classe['mana_max']} (+{info_classe['mana_rigenerazione_sec']}/sec)",
                True,
                AZZURRO,
            )
            schermo.blit(mana_txt, (x_dettagli, y_dettagli))
            y_dettagli += 22

        spiegazione_titolo = FONT_INFO.render(
            "COMANDI ED EFFETTI ABILITÀ:", True, BIANCO
        )
        schermo.blit(spiegazione_titolo, (x_dettagli, y_dettagli))
        y_dettagli += 22

        for linea in info_classe.get("desc_tasti", []):
            linea_surf = FONT_INFO.render(f"• {linea}", True, GRIGIO)
            schermo.blit(linea_surf, (x_dettagli, y_dettagli))
            y_dettagli += 22

        istruzioni_mov = FONT_CONSIGLIO.render(
            "In gioco ci si muove utilizzando i tasti WASD", True, VERDE
        )
        schermo.blit(
            istruzioni_mov, (l_corrente // 2 - istruzioni_mov.get_width() // 2, 550)
        )

        istruzioni = FONT_INFO.render(
            "Usa FRECCIA SU/GIÙ per navigare, INVIO per confermare",
            True,
            GRIGIO,
        )
        schermo.blit(istruzioni, (l_corrente // 2 - istruzioni.get_width() // 2, 585))

    elif stato_gioco == "MENU_MUTAFORMA":
        titolo = FONT_TITOLO.render(
            "SCEGLI LA FORMA MITOLOGICA", True, BIANCO
        )
        schermo.blit(titolo, (l_corrente // 2 - titolo.get_width() // 2, 35))

        for i, creatura in enumerate(creature):
            colore = GIALLO if i == indice_creatura else BIANCO
            testo = FONT_OPZIONI.render(
                f"> {creatura}" if i == indice_creatura else creatura,
                True,
                colore,
            )
            schermo.blit(testo, (80, 150 + i * 45))

        istruzioni_mov = FONT_CONSIGLIO.render(
            "In gioco ci si muove utilizzando i tasti WASD", True, VERDE
        )
        schermo.blit(
            istruzioni_mov, (l_corrente // 2 - istruzioni_mov.get_width() // 2, 540)
        )

        istruzioni = FONT_INFO.render(
            "INVIO per confermare, ESC per tornare indietro", True, GRIGIO
        )
        schermo.blit(istruzioni, (l_corrente // 2 - istruzioni.get_width() // 2, 580))

    elif stato_gioco == "IN_GIOCO":
        if giocatore:
            giocatore.aggiorna_effetti()

        funzioni.disegnamappa(RIGHE, COLONNE, mappa_attuale, DIM_CELLA, schermo)
        funzioni.disegnaplayer(giocatore, DIM_CELLA, schermo)

        for nemico in nemici_correnti:
            nemico.disegnanemico(schermo, DIM_CELLA)

        funzioni.disegna_effetti(schermo, giocatore, DIM_CELLA)
        funzioni.segnalino(schermo, numero_stanza)
        funzioni.disegna_hud(schermo, giocatore)

        if giocatore.info_abilita:
            nome_abilita = giocatore.info_abilita.get("nome", "Abilità")
            tipo_cd = giocatore.info_abilita.get("tipo_cooldown", "stanza")
            usi = giocatore.usi_rimanenti_abilita

            testo_ab = FONT_INFO.render(
                f"[{nome_abilita}] Usi disponibili ({tipo_cd}): {usi}",
                True,
                (0, 255, 0) if usi > 0 else (255, 100, 100),
            )
            schermo.blit(testo_ab, (10, 50))

    elif stato_gioco == "GAME_OVER":
        titolo_go = FONT_TITOLO.render("GAME OVER", True, ROSSO)
        schermo.blit(titolo_go, (l_corrente // 2 - titolo_go.get_width() // 2, 250))

        sub_go = FONT_OPZIONI.render(
            "Sei stato sconfitto!", True, BIANCO
        )
        schermo.blit(sub_go, (l_corrente // 2 - sub_go.get_width() // 2, 330))

        rst_go = FONT_INFO.render(
            "Premi 'R' per ricominciare una nuova partita", True, GRIGIO
        )
        schermo.blit(rst_go, (l_corrente // 2 - rst_go.get_width() // 2, 400))

    elif stato_gioco == "VITTORIA":
        titolo_win = FONT_TITOLO.render("VITTORIA!", True, GIALLO)
        schermo.blit(titolo_win, (l_corrente // 2 - titolo_win.get_width() // 2, 230))

        sub_win = FONT_OPZIONI.render(
            "Hai raccolto la coppa e completato il dungeon!", True, BIANCO
        )
        schermo.blit(sub_win, (l_corrente // 2 - sub_win.get_width() // 2, 310))

        rst_win = FONT_INFO.render(
            "Premi 'R' per giocare di nuovo", True, GRIGIO
        )
        schermo.blit(rst_win, (l_corrente // 2 - rst_win.get_width() // 2, 390))

    pygame.display.flip()
    orologio.tick(60)

pygame.quit()
sys.exit()